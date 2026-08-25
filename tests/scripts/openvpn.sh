#!/bin/sh
# This fixture verifies that CRL refreshes only report changed revocations.
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
	esac
}

openssl() {
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
	local expected_content="$3"
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
	grep -F "$expected_content" revoked.crl >/dev/null
}

trap cleanup EXIT
mkdir -p "$test_dir"
cd "$test_dir"
CA_UUID=test
. /openvpn_utils.sh

initial_crl='Last Update: one
Next Update: two
Revoked Certificates:
    Serial Number: 01'

run_case initial 0 'Last Update: one'
run_case timestamp_only 1 'Last Update: three' "$initial_crl"
run_case changed 0 'Serial Number: 02' "$initial_crl"
run_case failed 2 'Serial Number: 01' "$initial_crl"
run_case empty 2 'Serial Number: 01' "$initial_crl"
