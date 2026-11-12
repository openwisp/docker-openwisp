#!/bin/sh
# This shell script tests CRL refresh behavior.
set -e

test_dir=/tmp/openwisp-crl-refresh-test

cleanup() {
	rm -rf "$test_dir"
}

curl() {
	head=false
	output_path=""
	remote_time=false
	while [ "$#" -gt 0 ]; do
		case "$1" in
		--head)
			head=true
			shift
			;;
		--output)
			output_path="$2"
			shift 2
			;;
		--remote-time)
			remote_time=true
			shift
			;;
		*)
			shift
			;;
		esac
	done
	case "$CRL_TEST_MODE" in
	changed | failed | empty | malformed) last_modified=200 ;;
	*) last_modified=100 ;;
	esac
	if [ "$head" = true ]; then
		# Record the request in a file so it remains visible outside the subshell.
		: >.head-request
		test "$remote_time" = true
		case "$CRL_TEST_MODE" in
		no_last_modified) return ;;
		invalid_last_modified)
			printf '%s' 'invalid last-modified'
			return
			;;
		esac
		touch -d "@$last_modified" "$output_path"
		printf '%s' "$last_modified"
		return
	fi
	# Record the download separately to distinguish GET from HEAD requests.
	: >.get-request
	test -n "$output_path"
	test "$remote_time" = true
	case "$CRL_TEST_MODE" in
	not_modified)
		return 1
		;;
	initial)
		printf '%s\n' 'Last Update: one' 'Next Update: two' \
			'Revoked Certificates:' '    Serial Number: 01' >"$output_path"
		;;
	refreshed)
		printf '%s\n' 'Last Update: one' 'Next Update: later' \
			'Revoked Certificates:' '    Serial Number: 01' >"$output_path"
		;;
	changed)
		printf '%s\n' 'Last Update: five' 'Next Update: six' \
			'Revoked Certificates:' '    Serial Number: 02' >"$output_path"
		;;
	empty)
		: >"$output_path"
		;;
	failed)
		return 1
		;;
	malformed)
		printf '%s\n' 'not a CRL' >"$output_path"
		;;
	slow)
		: >.slow-download-started
		sleep 1
		printf '%s\n' 'Last Update: one' 'Next Update: two' \
			'Revoked Certificates:' '    Serial Number: 01' >"$output_path"
		;;
	esac
	touch -d "@$last_modified" "$output_path"
}

openssl() {
	local input=""
	local nextupdate=false
	while [ "$#" -gt 0 ]; do
		case "$1" in
		-in)
			input="$2"
			shift 2
			;;
		-nextupdate)
			nextupdate=true
			shift
			;;
		*)
			shift
			;;
		esac
	done
	if [ "$nextupdate" = true ]; then
		[ "$CRL_TEST_EXPIRY" != unreadable ] || return 1
		[ "$CRL_TEST_EXPIRY" != missing ] || return 0
		printf 'nextUpdate=%s\n' "$CRL_TEST_EXPIRY"
		return
	fi
	[ "$CRL_TEST_MODE" != malformed ] || return 1
	cat "$input"
}

date() {
	if [ "$#" -eq 1 ] && [ "$1" = +%s ]; then
		printf '%s\n' 1893553445
	else
		command date "$@"
	fi
}

run_case() {
	local mode="$1"
	local expected_status="$2"
	local expected_crl="$3"
	local initial_crl="${4:-}"
	local expiry="${5:-2030-01-02 03:04:06Z}"
	local expected_requests="${6:-head-get}"
	local status
	rm -f revoked.crl .head-request .get-request
	if [ -n "$initial_crl" ]; then
		printf '%s\n' "$initial_crl" >revoked.crl
		touch -d @100 revoked.crl
	fi
	CRL_TEST_MODE="$mode"
	CRL_TEST_EXPIRY="$expiry"
	export CRL_TEST_MODE CRL_TEST_EXPIRY
	if crl_download_if_changed; then
		status=0
	else
		status=$?
	fi
	[ "$status" -eq "$expected_status" ] || {
		echo "$mode ($expiry): expected status $expected_status, got $status" >&2
		return 1
	}
	printf '%s\n' "$expected_crl" | cmp -s - revoked.crl || {
		echo "$mode ($expiry): unexpected CRL contents" >&2
		return 1
	}
	case "$expected_requests" in
	head-get) [ -f .head-request ] && [ -f .get-request ] ;;
	head) [ -f .head-request ] && [ ! -f .get-request ] ;;
	get) [ ! -f .head-request ] && [ -f .get-request ] ;;
	esac || {
		echo "$mode ($expiry): expected requests $expected_requests" >&2
		return 1
	}
}

# Use an isolated directory and remove it when the test completes.
trap cleanup EXIT
mkdir -p "$test_dir"
cd "$test_dir"
CA_UUID=test
. /openvpn_utils.sh

initial_crl='Last Update: one
Next Update: two
Revoked Certificates:
    Serial Number: 01'
changed_crl='Last Update: five
Next Update: six
Revoked Certificates:
    Serial Number: 02'
refreshed_crl='Last Update: one
Next Update: later
Revoked Certificates:
    Serial Number: 01'

run_case initial 0 "$initial_crl" '' '' get
run_case not_modified 1 "$initial_crl" "$initial_crl" '' head
run_case changed 0 "$changed_crl" "$initial_crl"
run_case failed 2 "$initial_crl" "$initial_crl"
run_case empty 2 "$initial_crl" "$initial_crl"
run_case malformed 2 "$initial_crl" "$initial_crl"
run_case no_last_modified 2 "$initial_crl" "$initial_crl" '' head
run_case invalid_last_modified 2 "$initial_crl" "$initial_crl" '' head
run_case refreshed 0 "$refreshed_crl" "$initial_crl" '2030-01-02 03:04:04Z' get
run_case refreshed 0 "$refreshed_crl" "$initial_crl" '2030-01-02 03:04:05Z' get
run_case failed 2 "$initial_crl" "$initial_crl" '2030-01-02 03:04:04Z' get
run_case empty 2 "$initial_crl" "$initial_crl" '2030-01-02 03:04:04Z' get
run_case malformed 2 "$initial_crl" "$initial_crl" '2030-01-02 03:04:04Z' get
run_case refreshed 0 "$refreshed_crl" "$initial_crl" unreadable get
run_case failed 2 "$initial_crl" "$initial_crl" unreadable get
run_case refreshed 0 "$refreshed_crl" "$initial_crl" missing get
run_case refreshed 0 "$refreshed_crl" "$initial_crl" invalid get

rm -f revoked.crl .slow-download-started
CRL_TEST_MODE=slow
export CRL_TEST_MODE
crl_download_if_changed &
slow_download_pid=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do
	if [ -f .slow-download-started ]; then break; fi
	sleep 0.1
done
test -f .slow-download-started
CRL_TEST_MODE=changed
export CRL_TEST_MODE
if crl_download_if_changed; then
	crl_status=0
else
	crl_status=$?
fi
test "$crl_status" -eq 1
wait "$slow_download_pid"

# Verify that VPN_NAME does not need to match the OpenVPN config filename.
test_vpn_name_config_filename_decoupling() (
	config_test_dir=$(mktemp -d) || exit 1
	trap 'rm -rf -- "$config_test_dir"' EXIT HUP INT TERM
	mkdir "$config_test_dir/archive" "$config_test_dir/work"
	printf '%s' 'new config' >"$config_test_dir/archive/my vpn.conf"
	printf '%s' 'pem' >"$config_test_dir/archive/client.pem"
	tar -czf "$config_test_dir/vpn.tar.gz" -C "$config_test_dir/archive" \
		'my vpn.conf' client.pem
	printf '%s' 'stale config' >"$config_test_dir/work/openvpn.conf"
	cd "$config_test_dir/work"
	curl() {
		output_path=""
		while [ "$#" -gt 0 ]; do
			case "$1" in
			--output)
				output_path="$2"
				shift 2
				;;
			*)
				shift
				;;
			esac
		done
		case "$output_path" in
		*/vpn.tar.gz) cp "$config_test_dir/vpn.tar.gz" "$output_path" ;;
		*/checksum) printf '%s\n' checksum >"$output_path" ;;
		*) return 1 ;;
		esac
	}
	API_INTERNAL=https://api.internal
	UUID=vpn-uuid
	KEY=vpn-key
	openvpn_config_download
	test "$(cat openvpn.conf)" = 'new config'
	test ! -f 'my vpn.conf'
	test "$(cat checksum)" = checksum
	test "$(stat -c '%a' client.pem)" = 600
	mkdir "$config_test_dir/multiple"
	printf '%s' 'first config' >"$config_test_dir/archive/first.conf"
	printf '%s' 'second config' >"$config_test_dir/archive/second.conf"
	tar -czf "$config_test_dir/vpn.tar.gz" -C "$config_test_dir/archive" \
		first.conf second.conf
	printf '%s\n' previous-checksum >"$config_test_dir/multiple/checksum"
	cd "$config_test_dir/multiple"
	if openvpn_config_download >/dev/null 2>&1; then
		return 1
	fi
	test ! -f openvpn.conf
	test "$(cat checksum)" = previous-checksum
	mkdir "$config_test_dir/empty"
	printf '%s' 'empty archive' >"$config_test_dir/archive/empty.txt"
	tar -czf "$config_test_dir/vpn.tar.gz" -C "$config_test_dir/archive" empty.txt
	printf '%s' 'stale config' >"$config_test_dir/empty/openvpn.conf"
	cd "$config_test_dir/empty"
	if openvpn_config_download >/dev/null 2>&1; then
		return 1
	fi
	test "$(cat openvpn.conf)" = 'stale config'
	test ! -f checksum
	mkdir -p "$config_test_dir/archive/etc/openvpn" \
		"$config_test_dir/nested/etc/ssl"
	printf '%s' 'nested config' >"$config_test_dir/archive/server.conf"
	printf '%s' 'nested pem' >"$config_test_dir/archive/etc/openvpn/ca.pem"
	tar -czf "$config_test_dir/vpn.tar.gz" -C "$config_test_dir/archive" \
		server.conf etc/openvpn/ca.pem
	printf '%s' 'stale config' >"$config_test_dir/nested/openvpn.conf"
	printf '%s' 'existing file' >"$config_test_dir/nested/etc/ssl/keep"
	cd "$config_test_dir/nested"
	openvpn_config_download
	test "$(cat openvpn.conf)" = 'nested config'
	test "$(cat etc/openvpn/ca.pem)" = 'nested pem'
	test "$(cat etc/ssl/keep)" = 'existing file'
)

test_config_update_lock() (
	lock_test_dir=$(mktemp -d) || exit 1
	trap 'rm -rf -- "$lock_test_dir" /checksum' EXIT HUP INT TERM
	mkdir "$lock_test_dir/bin"
	printf '%s\n' '#!/bin/sh' 'exit 1' >"$lock_test_dir/bin/curl"
	chmod 700 "$lock_test_dir/bin/curl"
	printf '%s\n' local >/checksum
	PATH="$lock_test_dir/bin:$PATH"
	UUID=vpn-uuid
	KEY=vpn-key
	export PATH UUID KEY
	(
		flock -n 9 || exit 1
		sh /openvpn.sh
	) 9>/.openvpn-config.lock
)

test_vpn_name_config_filename_decoupling
test_config_update_lock
