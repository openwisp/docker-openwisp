#!/bin/sh

get_redis_value() {
	local key="$1"
	printf 'GET %s\r\n' "$key" | nc -w 5 redis 6379 | awk 'NR==2 {gsub(/\r/, ""); print}'
}

function openvpn_preconfig {
	mkdir -p /dev/net
	if [ ! -c /dev/net/tun ]; then
		mknod /dev/net/tun c 10 200
	fi
	ip -6 route show default 2>/dev/null
	if [ $? = 0 ]; then
		echo "Enabling IPv6 Forwarding"
		sysctl -w net.ipv6.conf.all.disable_ipv6=0 || echo "Failed to enable IPv6 support"
		sysctl -w net.ipv6.conf.default.forwarding=1 || echo "Failed to enable IPv6 Forwarding default"
		sysctl -w net.ipv6.conf.all.forwarding=1 || echo "Failed to enable IPv6 Forwarding"
	fi
}

function openvpn_config {
	# Fectch UUID and Key of the default VPN only if they
	# are not already set. The user may override the UUID and Key
	# by setting them in the environment variables to use deploy
	# a different VPN server.
	if [ -z "$UUID" ]; then
		export UUID=$(get_redis_value "openwisp_default_vpn_uuid")
		export KEY=$(get_redis_value "openwisp_default_vpn_key")
		export CA_UUID=$(get_redis_value "openwisp_default_vpn_ca_uuid")
	fi
}

function openvpn_config_checksum {
	local remote_checksum
	local local_checksum

	remote_checksum=$(curl --silent --show-error --fail --insecure \
		${API_INTERNAL}/controller/vpn/checksum/$UUID/?key=$KEY) || return 1
	if [ -z "$remote_checksum" ]; then
		return 1
	fi

	if [ -s checksum ]; then
		local_checksum=$(cat checksum)
	fi
	if [ -z "$local_checksum" ]; then
		local_checksum=""
	fi

	export OFILE="$remote_checksum"
	export NFILE="$local_checksum"
}

function openvpn_config_download {
	local tmp_tar
	local tmp_checksum
	local tmp_extract_dir
	local expected_checksum
	local actual_checksum

	tmp_tar=$(mktemp /tmp/vpn-config.XXXXXX) || return 1
	tmp_checksum=$(mktemp /tmp/vpn-checksum.XXXXXX) || {
		rm -f "$tmp_tar"
		return 1
	}
	tmp_extract_dir=$(mktemp -d /tmp/vpn-config-dir.XXXXXX) || {
		rm -f "$tmp_tar" "$tmp_checksum"
		return 1
	}
	trap 'rm -f "$tmp_tar" "$tmp_checksum"; rm -rf "$tmp_extract_dir"' EXIT HUP INT TERM

	curl --silent --show-error --fail --retry 10 --retry-delay 5 --retry-max-time 300 \
		--insecure --output "$tmp_tar" \
		${API_INTERNAL}/controller/vpn/download-config/$UUID/?key=$KEY || return 1
	test -s "$tmp_tar" || return 1

	curl --silent --show-error --fail --insecure --output "$tmp_checksum" \
		${API_INTERNAL}/controller/vpn/checksum/$UUID/?key=$KEY || return 1
	test -s "$tmp_checksum" || {
		echo "Downloaded OpenVPN checksum is empty" >&2
		return 1
	}

	expected_checksum=$(awk 'NF {print $1; exit}' "$tmp_checksum" | tr -d '\r')
	if [ -z "$expected_checksum" ]; then
		echo "Downloaded OpenVPN checksum is empty" >&2
		return 1
	fi

	case "${#expected_checksum}" in
		32)
			actual_checksum=$(md5sum "$tmp_tar" | awk '{print $1}') || return 1
			;;
		40)
			actual_checksum=$(sha1sum "$tmp_tar" | awk '{print $1}') || return 1
			;;
		64)
			actual_checksum=$(sha256sum "$tmp_tar" | awk '{print $1}') || return 1
			;;
		128)
			actual_checksum=$(sha512sum "$tmp_tar" | awk '{print $1}') || return 1
			;;
		*)
			echo "Unsupported OpenVPN checksum format: $expected_checksum" >&2
			return 1
			;;
	esac
	if [ "$actual_checksum" != "$expected_checksum" ]; then
		echo "Downloaded OpenVPN config checksum mismatch" >&2
		return 1
	fi

	tar xzf "$tmp_tar" -C "$tmp_extract_dir" || return 1
	set -- "$tmp_extract_dir"/*.pem
	test -e "$1" || return 1
	chmod 600 "$@" || return 1
	cp -R "$tmp_extract_dir"/. / || return 1

	mv "$tmp_checksum" checksum || return 1
	rm -f "$tmp_tar"
	rm -rf "$tmp_extract_dir"
	trap - EXIT HUP INT TERM
}

function crl_download_to {
	local output_path="${1:-revoked.crl}"
	curl --silent --show-error --fail --retry 10 --retry-delay 5 --retry-max-time 300 \
		--insecure --output "$output_path" \
		${DASHBOARD_INTERNAL}/admin/pki/ca/x509/ca/${CA_UUID}.crl
}

function crl_download {
	curl --silent --show-error --fail --retry 10 --retry-delay 5 --retry-max-time 300 \
		--insecure --output revoked.crl \
		${DASHBOARD_INTERNAL}/admin/pki/ca/x509/ca/${CA_UUID}.crl
}

function crl_download_if_changed {
	local tmp_crl
	tmp_crl=$(mktemp /tmp/revoked.crl.XXXXXX) || return 2
	trap 'rm -f "$tmp_crl"' EXIT HUP INT TERM

	if ! crl_download_to "$tmp_crl"; then
		trap - EXIT HUP INT TERM
		rm -f "$tmp_crl"
		return 2
	fi

	if [ ! -f revoked.crl ] || ! cmp -s "$tmp_crl" revoked.crl; then
		mv "$tmp_crl" revoked.crl || return 2
		trap - EXIT HUP INT TERM
		return 0
	fi

	trap - EXIT HUP INT TERM
	rm -f "$tmp_crl"
	return 1
}

function init_send_network_topology {
	case "$TOPOLOGY_UPDATE_INTERVAL" in
		''|*[!0-9]*|0)
			echo "Skipping topology cron: invalid TOPOLOGY_UPDATE_INTERVAL: $TOPOLOGY_UPDATE_INTERVAL" >&2
			return 0
			;;
	esac

	if [ -z "$TOPOLOGY_UUID" ]; then
		export TOPOLOGY_UUID=$(get_redis_value "default_openvpn_topology_uuid")
		export TOPOLOGY_KEY=$(get_redis_value "default_openvpn_topology_key")
	fi
	if [ -z "$TOPOLOGY_UUID" ] || [ -z "$TOPOLOGY_KEY" ]; then
		echo "Skipping topology cron: missing TOPOLOGY_UUID or TOPOLOGY_KEY" >&2
		return 0
	fi
	(
		crontab -l
		echo "*/$TOPOLOGY_UPDATE_INTERVAL * * * * TOPOLOGY_UUID=$TOPOLOGY_UUID TOPOLOGY_KEY=$TOPOLOGY_KEY sh /send-topology.sh"
	) | crontab -
}
