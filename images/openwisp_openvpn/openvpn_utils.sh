#!/bin/sh

. /utils.sh

get_redis_value() {
	local key="$1"
	printf 'GET %s\r\n' "$key" | nc redis 6379 | awk 'NR==2 {gsub(/\r/, ""); print}'
}

openvpn_preconfig() {
	mkdir -p /dev/net
	if [ ! -c /dev/net/tun ]; then
		mknod /dev/net/tun c 10 200
	fi
	if ip -6 route show default >/dev/null 2>&1; then
		echo "Enabling IPv6 Forwarding"
		sysctl -w net.ipv6.conf.all.disable_ipv6=0 || echo "Failed to enable IPv6 support"
		sysctl -w net.ipv6.conf.default.forwarding=1 || echo "Failed to enable IPv6 Forwarding default"
		sysctl -w net.ipv6.conf.all.forwarding=1 || echo "Failed to enable IPv6 Forwarding"
	fi
}

openvpn_config() {
	# Fetch UUID and Key of the default VPN only if they
	# are not already set. The user may override the UUID and Key
	# by setting them in the environment variables to deploy
	# a different VPN server.
	if [ -z "$UUID" ]; then
		UUID="$(get_redis_value "openwisp_default_vpn_uuid")"
		KEY="$(get_redis_value "openwisp_default_vpn_key")"
		CA_UUID="$(get_redis_value "openwisp_default_vpn_ca_uuid")"
		export UUID KEY CA_UUID
	fi
}

openvpn_config_checksum() {
	OFILE=$(curl_download --silent \
		"${API_INTERNAL}/controller/vpn/checksum/${UUID}/?key=${KEY}")
	export OFILE
	NFILE=$(cat checksum)
	export NFILE
}

openvpn_config_download() {
	local tmp_dir
	local conf_file
	local file
	# Extract in isolation so stale files in / cannot be mistaken for
	# files from the newly downloaded archive.
	tmp_dir=$(mktemp -d) || return 1
	curl_download --silent --retry 10 --retry-delay 5 --retry-max-time 300 --output vpn.tar.gz \
		"${API_INTERNAL}/controller/vpn/download-config/${UUID}/?key=${KEY}" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	curl_download --silent --output checksum \
		"${API_INTERNAL}/controller/vpn/checksum/${UUID}/?key=${KEY}" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	tar xzf vpn.tar.gz -C "$tmp_dir" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	chmod 600 -- "$tmp_dir"/*.pem 2>/dev/null || true
	# Supervisord always starts OpenVPN with openvpn.conf; normalize whatever
	# config filename the archive contains, including names with whitespace.
	conf_file=""
	for file in "$tmp_dir"/*.conf; do
		[ -f "$file" ] || continue
		if [ -n "$conf_file" ]; then
			echo "ERROR: more than one OpenVPN config file found after extraction" >&2
			rm -rf -- "$tmp_dir"
			return 1
		fi
		conf_file="$file"
	done
	if [ -z "$conf_file" ]; then
		echo "ERROR: no OpenVPN config file found after extraction" >&2
		rm -rf -- "$tmp_dir"
		return 1
	fi
	mv -f -- "$conf_file" openvpn.conf || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	# Move the remaining extracted files after moving the normalized config.
	find "$tmp_dir" -mindepth 1 -maxdepth 1 ! -name '*.conf' -exec mv -f -- {} . \; || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	rm -rf -- "$tmp_dir"
}

crl_download_to() {
	local output_path="$1"
	curl_download --silent --fail --retry 10 --retry-delay 5 --retry-max-time 300 \
		--output "$output_path" \
		"${DASHBOARD_INTERNAL}/admin/pki/ca/x509/ca/${CA_UUID}.crl"
	test -s "$output_path"
}

crl_download() {
	local tmp_crl
	tmp_crl=$(mktemp /tmp/revoked.crl.XXXXXX) || return 1
	if ! crl_download_to "$tmp_crl"; then
		rm -f "$tmp_crl"
		return 1
	fi
	if ! openssl crl -in "$tmp_crl" -noout >/dev/null 2>&1; then
		rm -f "$tmp_crl"
		return 1
	fi
	mv "$tmp_crl" revoked.crl || {
		rm -f "$tmp_crl"
		return 1
	}
}

crl_revocations() {
	openssl crl -in "$1" -noout >/dev/null 2>&1 || return 1
	openssl crl -in "$1" -noout -text 2>/dev/null | awk '
		/^Revoked Certificates:$/ { revoked = 1; next }
		revoked && /^    Signature Algorithm:/ { exit }
		revoked { print }
	'
}

# The five-minute cron caller restarts only for changed revocations and
# preserves the current CRL on errors.
crl_download_if_changed() (
	flock -n 9 || return 1
	local tmp_crl
	local tmp_new_revocations
	local tmp_old_revocations
	local crl_changed
	tmp_crl=$(mktemp /tmp/revoked.crl.XXXXXX) || return 2
	tmp_new_revocations=$(mktemp /tmp/revoked.revocations.XXXXXX) || {
		rm -f "$tmp_crl"
		return 2
	}
	tmp_old_revocations=$(mktemp /tmp/revoked.revocations.XXXXXX) || {
		rm -f "$tmp_crl" "$tmp_new_revocations"
		return 2
	}
	trap 'rm -f "$tmp_crl" "$tmp_new_revocations" "$tmp_old_revocations"' EXIT HUP INT TERM

	if ! crl_download_to "$tmp_crl" ||
		! crl_revocations "$tmp_crl" >"$tmp_new_revocations"; then
		return 2
	fi
	if [ ! -f revoked.crl ]; then
		mv "$tmp_crl" revoked.crl || return 2
		trap - EXIT HUP INT TERM
		rm -f "$tmp_new_revocations" "$tmp_old_revocations"
		return 0
	fi
	if ! crl_revocations revoked.crl >"$tmp_old_revocations"; then
		return 2
	fi
	cmp -s "$tmp_new_revocations" "$tmp_old_revocations"
	crl_changed=$?
	if [ "$crl_changed" -ne 0 ]; then
		mv "$tmp_crl" revoked.crl || return 2
		trap - EXIT HUP INT TERM
		rm -f "$tmp_new_revocations" "$tmp_old_revocations"
		return 0
	fi
	mv "$tmp_crl" revoked.crl || return 2
	trap - EXIT HUP INT TERM
	rm -f "$tmp_new_revocations" "$tmp_old_revocations"
	return 1
) 9>/revoked.crl.lock

init_send_network_topology() {
	if [ -z "$TOPOLOGY_UUID" ]; then
		TOPOLOGY_UUID="$(get_redis_value "default_openvpn_topology_uuid")"
		TOPOLOGY_KEY="$(get_redis_value "default_openvpn_topology_key")"
		export TOPOLOGY_UUID TOPOLOGY_KEY
	fi
	(
		crontab -l
		echo "*/$TOPOLOGY_UPDATE_INTERVAL * * * * TOPOLOGY_UUID=$TOPOLOGY_UUID TOPOLOGY_KEY=$TOPOLOGY_KEY sh /send-topology.sh"
	) | crontab -
}
