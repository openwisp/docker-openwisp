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
	local extract_dir
	local conf_file
	local file
	# Extract in isolation so stale files in / cannot be mistaken for
	# files from the newly downloaded archive.
	tmp_dir=$(mktemp -d) || return 1
	extract_dir="$tmp_dir/extract"
	mkdir "$extract_dir" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	curl_download --silent --retry 10 --retry-delay 5 --retry-max-time 300 \
		--output "$tmp_dir/vpn.tar.gz" \
		"${API_INTERNAL}/controller/vpn/download-config/${UUID}/?key=${KEY}" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	curl_download --silent --output "$tmp_dir/checksum" \
		"${API_INTERNAL}/controller/vpn/checksum/${UUID}/?key=${KEY}" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	tar xzf "$tmp_dir/vpn.tar.gz" -C "$extract_dir" || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	find "$extract_dir" -type f -name '*.pem' -exec chmod 600 -- {} + || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	# Supervisord always starts OpenVPN with openvpn.conf; normalize whatever
	# config filename the archive contains, including names with whitespace.
	conf_file=""
	for file in "$extract_dir"/*.conf; do
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
	if [ "$conf_file" != "$extract_dir/openvpn.conf" ]; then
		mv -f -- "$conf_file" "$extract_dir/openvpn.conf" || {
			rm -rf -- "$tmp_dir"
			return 1
		}
	fi
	# Install extra files before replacing the active configuration, preserving
	# their archive-relative paths when the destination directory already exists.
	find "$extract_dir" -type f ! -path "$extract_dir/openvpn.conf" -exec sh -c '
		extract_dir="$1"
		shift
		for file; do
			target=${file#"$extract_dir"/}
			mkdir -p "$(dirname "$target")" || exit 1
			mv -f -- "$file" "$target" || exit 1
		done
	' sh "$extract_dir" {} + || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	mv -f -- "$extract_dir/openvpn.conf" openvpn.conf || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	mv -f -- "$tmp_dir/checksum" checksum || {
		rm -rf -- "$tmp_dir"
		return 1
	}
	rm -rf -- "$tmp_dir"
}

crl_download_to() {
	local output_path="$1"
	curl_download --silent --fail --retry 10 --retry-delay 5 --retry-max-time 300 \
		--remote-time \
		--output "$output_path" \
		"${DASHBOARD_INTERNAL}/admin/pki/ca/x509/ca/${CA_UUID}.crl"
	test -s "$output_path" || return 1
	# The CRL is public data (revoked certificate serial numbers), and OpenVPN
	# re-reads it from disk on every TLS session after dropping privileges to
	# the unprivileged "user"/"group" from openvpn.conf, so it must stay
	# world-readable regardless of mktemp's default 0600 mode.
	chmod 644 -- "$output_path"
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

# The five-minute cron caller checks the CRL's Last-Modified value with a HEAD
# request before downloading and preserves the current CRL on errors.
crl_download_if_changed() (
	flock -n 9 || return 1
	local tmp_last_modified
	local last_modified
	if [ ! -f revoked.crl ]; then
		crl_download || return 2
		return 0
	fi
	tmp_last_modified=$(mktemp /tmp/revoked.crl.last-modified.XXXXXX) || return 2
	trap 'rm -f "$tmp_last_modified"' EXIT HUP INT TERM
	touch -d @0 "$tmp_last_modified" || return 2
	last_modified=$(curl_download --silent --fail --head --remote-time \
		--output "$tmp_last_modified" --write-out '%header{last-modified}' \
		"${DASHBOARD_INTERNAL}/admin/pki/ca/x509/ca/${CA_UUID}.crl") || return 2
	[ -n "$last_modified" ] || return 2
	[ "$(stat -c %Y "$tmp_last_modified")" != 0 ] || return 2
	if [ "$(stat -c %Y "$tmp_last_modified")" = "$(stat -c %Y revoked.crl)" ]; then
		return 1
	fi
	crl_download || return 2
	return 0
) 9>/revoked.crl.lock

init_send_network_topology() {
	if [ -z "$TOPOLOGY_UUID" ]; then
		TOPOLOGY_UUID="$(get_redis_value "default_openvpn_topology_uuid")"
		TOPOLOGY_KEY="$(get_redis_value "default_openvpn_topology_key")"
		export TOPOLOGY_UUID TOPOLOGY_KEY
	fi
	(
		crontab -l
		# Forward the generated job's output to PID 1 so Docker can collect it.
		echo "*/$TOPOLOGY_UPDATE_INTERVAL * * * * TOPOLOGY_UUID=$TOPOLOGY_UUID TOPOLOGY_KEY=$TOPOLOGY_KEY sh /send-topology.sh >>/proc/1/fd/1 2>>/proc/1/fd/2"
	) | crontab -
}
