#!/bin/bash

if [ "$(whoami)" != "$OPENWISP_USER" ]; then
	echo "Script should only be run by $OPENWISP_USER. Exiting!"
	exit 9
fi

# make sure this directory is writable by the user which calls the script
CONF_DIR="/opt/openwisp"

# do not modify these vars
_VPN_URL_PATH="$API_INTERNAL/controller/vpn"
_VPN_CHECKSUM_URL="$_VPN_URL_PATH/checksum/$WIREGUARD_VPN_UUID/?key=$WIREGUARD_VPN_KEY"
_VPN_DOWNLOAD_URL="$_VPN_URL_PATH/download-config/$WIREGUARD_VPN_UUID/?key=$WIREGUARD_VPN_KEY"
_WORKING_DIR="$CONF_DIR/.openwisp"
_CHECKSUM_FILE="$_WORKING_DIR/checksum"
_TIMESTAMP_FILE="$_WORKING_DIR/timestamp"
_MANAGED_INTERFACE="$_WORKING_DIR/managed-interface"
_APPLIED_CONF_DIR="$_WORKING_DIR/current-conf"
_CONF_TAR="$_WORKING_DIR/conf.tar.gz"
_CURL="curl -s --show-error --fail"

mkdir -p $_WORKING_DIR
mkdir -p $_APPLIED_CONF_DIR

assert_exit_code() {
	exit_code=$?
	lineno=$(($1 - 1))
	if [ "$exit_code" != "0" ] && [ ! -z "$2" ]; then
		echo $2
	fi
	if [ "$exit_code" != "0" ]; then
		echo "Line $lineno: Command returned non zero exit code: $exit_code"
		sudo kill 1
		exit $exit_code
	fi
}

check_config() {
	_latest_checksum=$($_CURL $_VPN_CHECKSUM_URL)
	assert_exit_code $LINENO "Failed to fetch VPN checksum. Ensure VPN UUID and key are correct."
	if [ -f "$_CHECKSUM_FILE" ]; then
		_current_checksum=$(cat $_CHECKSUM_FILE)
	else
		_current_checksum=""
	fi

	if [ "$_current_checksum" != "$_latest_checksum" ]; then
		echo "Configuration changed, downloading new configuration..."
		update_config
	fi
}

clean_old_interface() {
	echo "Bringing down old wireguard interface $managed_interface_name"
	for old_conf_file in $_APPLIED_CONF_DIR/*.conf; do
		[ -e "$old_conf_file" ] || continue
		sudo wg-quick down $old_conf_file
	done
	rm $_APPLIED_CONF_DIR/*.conf
}

create_new_interface() {
	echo "Bringing up new wireguard interface $interface"
	sudo wg-quick up $file
}

update_config() {
	# Set file permissions to 0660, otherwise wg will complain
	# for having public configurations
	umask 0117
	$($_CURL $_VPN_DOWNLOAD_URL >"$_CONF_TAR")
	assert_exit_code $LINENO "Failed to download VPN configuration. Ensure VPN UUID and key are correct."
	echo "Configuration downloaded, extracting it..."
	tar -zxvf $_CONF_TAR -C $CONF_DIR >/dev/null
	assert_exit_code $LINENO
	if [ -e "$_MANAGED_INTERFACE" ]; then
		managed_interface_name=$(cat "$_MANAGED_INTERFACE")
	fi

	for file in $CONF_DIR/*.conf; do
		[ -e "$file" ] || continue
		filename=$(basename $file)
		interface="${filename%.*}"

		# There is no managed_interface
		if [ -z ${managed_interface_name+x} ]; then
			create_new_interface
		# Current managed interface is not present in new configuration
		elif [ "$managed_interface_name" != "$interface" ]; then
			clean_old_interface
			assert_exit_code $LINENO
			create_new_interface
			assert_exit_code $LINENO
		else
			# Update the configuration of current managed interface
			echo "Reloading wireguard interface $interface with config file $file..."
			wg_conf_filename="$filename-wg"
			sudo wg-quick strip "$CONF_DIR/$filename" >"$CONF_DIR/$wg_conf_filename"
			assert_exit_code $LINENO
			sudo wg syncconf $interface "$CONF_DIR/$wg_conf_filename"
			assert_exit_code $LINENO
			rm "$CONF_DIR/$wg_conf_filename"
		fi
		echo "$interface" >"$_MANAGED_INTERFACE"
		mv -f "$file" "$_APPLIED_CONF_DIR/$filename"
		assert_exit_code $LINENO
	done

	# Save checksum of applied configuration
	echo $_latest_checksum >$_CHECKSUM_FILE
}

bring_up_interface() {
	for conf_file in $_APPLIED_CONF_DIR/*.conf; do
		[ -e "$conf_file" ] || continue
		sudo wg-quick up $conf_file || true
	done
	exit 0
}

watch_configuration_change() {
	_REDIS_CMD="redis-cli -h $REDIS_HOST -n $REDIS_DATABASE"
	if [[ "$REDIS_PORT" ]]; then
		_REDIS_CMD="$_REDIS_CMD -p $REDIS_PORT"
	fi
	if [[ "$REDIS_PASS" ]]; then
		_REDIS_CMD="$_REDIS_CMD -a $REDIS_PASS --no-auth-warning"
	fi
	while true; do
		if [ -f "$_TIMESTAMP_FILE" ]; then
			local_timestamp=$(cat $_TIMESTAMP_FILE)
		else
			local_timestamp=""
		fi
		current_timestamp=$($_REDIS_CMD GET wg-$WIREGUARD_VPN_UUID)
		if [ "$current_timestamp" != "$local_timestamp" ]; then
			echo "Configuration reload triggered by the updater."
			check_config
			assert_exit_code $LINENO
			# Save timestamp of applied configuration
			echo $current_timestamp >$_TIMESTAMP_FILE
		fi
		sleep 3
	done
}

"$@"
