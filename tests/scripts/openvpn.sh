#!/bin/sh
# This shell script tests CRL refresh behavior.
set -e

test_dir=/tmp/openwisp-crl-refresh-test

cleanup() {
	rm -rf "$test_dir"
}

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
	test -n "$output_path"
	case "$CRL_TEST_MODE" in
	initial)
		printf '%s\n' 'Last Update: one' 'Next Update: two' \
			'Revoked Certificates:' '    Serial Number: 01' >"$output_path"
		;;
	timestamp_only)
		printf '%s\n' 'Last Update: three' 'Next Update: four' \
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
}

openssl() {
	if [ "$CRL_TEST_MODE" = malformed ]; then
		return 1
	fi
	while [ "$#" -gt 0 ]; do
		case "$1" in
		-in)
			cat "$2"
			return
			;;
		*)
			shift
			;;
		esac
	done
	return 1
}

run_case() {
	local mode="$1"
	local expected_status="$2"
	local expected_crl="$3"
	local initial_crl="${4:-}"
	local status
	rm -f revoked.crl
	if [ -n "$initial_crl" ]; then
		printf '%s\n' "$initial_crl" >revoked.crl
	fi
	CRL_TEST_MODE="$mode"
	export CRL_TEST_MODE
	if crl_download_if_changed; then
		status=0
	else
		status=$?
	fi
	test "$status" -eq "$expected_status"
	printf '%s\n' "$expected_crl" | cmp -s - revoked.crl
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
timestamp_crl='Last Update: three
Next Update: four
Revoked Certificates:
    Serial Number: 01'
changed_crl='Last Update: five
Next Update: six
Revoked Certificates:
    Serial Number: 02'

run_case initial 0 "$initial_crl"
run_case timestamp_only 1 "$timestamp_crl" "$initial_crl"
run_case changed 0 "$changed_crl" "$initial_crl"
run_case failed 2 "$initial_crl" "$initial_crl"
run_case empty 2 "$initial_crl" "$initial_crl"
run_case malformed 2 "$initial_crl" "$initial_crl"

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
