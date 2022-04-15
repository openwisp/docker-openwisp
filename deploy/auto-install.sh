#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export INSTALL_PATH=/opt/openwisp/docker-openwisp
export LOG_FILE=/opt/openwisp/autoinstall.log
export GIT_PATH=https://github.com/openwisp/docker-openwisp.git
export ENV_USER=/opt/openwisp/config.env
export ENV_BACKUP=/opt/openwisp/backup.env

# Terminal colors
export RED='\033[1;31m'
export GRN='\033[1;32m'
export YLW='\033[1;33m'
export BLU='\033[1;34m'
export NON='\033[0m'

start_step() { printf '\e[1;34m%-70s\e[m' "$1" && echo "$1" &>>$LOG_FILE; }
report_ok() { echo -e ${GRN}" done"${NON}; }
report_error() { echo -e ${RED}" error"${NON}; }
get_env() { grep "^$1" "$2" | cut -d'=' -f 2-50; }
set_env() {
	line=$(grep -n "^$1=" $INSTALL_PATH/.env)
	if [ -z "$line" ]; then
		echo "$1=$2" >>$INSTALL_PATH/.env
	else
		line_number=$(echo $line | cut -f1 -d:)
		eval $(echo "awk -i inplace 'NR=="${line_number}" {\$0=\"${1}=${2}\"}1' $INSTALL_PATH/.env")
	fi
}

check_status() {
	if [ $1 -eq 0 ]; then
		report_ok
	else
		error_msg "$2"
	fi
}

error_msg() {
	report_error
	echo -e ${RED}${1}${NON}
	echo -e ${RED}"Check logs at $LOG_FILE"${NON}
	exit 1
}

error_msg_with_continue() {
	report_error
	echo -ne ${RED}${1}${NON}
	read reply
	if [[ ! $reply =~ ^[Yy]$ ]]; then
		exit 1
	fi
}

apt_dependenices_setup() {
	start_step "Setting up dependencies..."
	apt --yes install python3 python3-pip git python3-dev gawk libffi-dev libssl-dev gcc make &>>$LOG_FILE
	pip3 install --upgrade pip &>>$LOG_FILE
	check_status $? "Python dependencies installation failed."
}

setup_docker() {
	start_step "Setting up docker..."
	docker info &>/dev/null
	if [ $? -eq 0 ]; then
		report_ok
	else
		curl -fsSL 'https://get.docker.com' -o '/opt/openwisp/get-docker.sh' &>>$LOG_FILE
		sh '/opt/openwisp/get-docker.sh' &>>$LOG_FILE
		docker info &>/dev/null
		check_status $? "Docker installation failed."
	fi
}

setup_docker_compose() {
	start_step "Setting up docker-compose..."
	python3 -m pip install docker-compose &>>$LOG_FILE
	docker-compose version &>/dev/null
	check_status $? "docker-compose installation failed."
}

setup_docker_openwisp() {
	echo -e ${GRN}"\nOpenWISP Configuration:"${NON}
	echo -ne ${GRN}"OpenWISP Version (leave blank for latest): "${NON}
	read openwisp_version
	if [[ -z "$openwisp_version" ]]; then openwisp_version=latest; fi
	echo -ne ${GRN}"Do you have .env file? Enter filepath (leave blank for ad-hoc configuration): "${NON}
	read env_path
	if [[ ! -f "$env_path" ]]; then
		# Dashboard Domain
		echo -ne ${GRN}"(1/5) Enter dashboard domain: "${NON}
		read dashboard_domain
		domain=$(echo "$dashboard_domain" | cut -f2- -d'.')
		# API Domain
		echo -ne ${GRN}"(2/5) Enter API domain (blank for api.${domain}): "${NON}
		read API_DOMAIN
		# VPN domain
		echo -ne ${GRN}"(3/5) Enter OpenVPN domain (blank for vpn.${domain}, N to disable module): "${NON}
		read vpn_domain
		# Site manager email
		echo -ne ${GRN}"(4/5) Site manager email: "${NON}
		read django_default_email
		# SSL Configuration
		echo -ne ${GRN}"(5/5) Enter letsencrypt email (leave blank for self-signed certificate): "${NON}
		read letsencrypt_email
	else
		cp $env_path $ENV_USER &>>$LOG_FILE
	fi
	echo ""

	start_step "Downloading docker-openwisp..."
	if [[ -f $INSTALL_PATH/.env ]]; then
		mv $INSTALL_PATH/.env $ENV_BACKUP &>>$LOG_FILE
		rm -rf $INSTALL_PATH &>>$LOG_FILE
	fi

	if [[ $openwisp_version -ne "edge" ]]; then
		git clone $GIT_PATH $INSTALL_PATH --depth 1 --branch $openwisp_version &>>$LOG_FILE
	else
		git clone $GIT_PATH $INSTALL_PATH --depth 1 &>>$LOG_FILE
	fi

	cd $INSTALL_PATH &>>$LOG_FILE
	check_status $? "docker-openwisp download failed."
	echo $openwisp_version >$INSTALL_PATH/VERSION

	if [[ ! -f "$env_path" ]]; then
		# Dashboard Domain
		set_env "DASHBOARD_DOMAIN" "$dashboard_domain"
		# API Domain
		if [[ -z "$API_DOMAIN" ]]; then
			set_env "API_DOMAIN" "api.${domain}"
		else
			set_env "API_DOMAIN" "$API_DOMAIN"
		fi
		# Use Radius
		if [[ -z "$USE_OPENWISP_RADIUS" ]]; then
			set_env "USE_OPENWISP_RADIUS" "Yes"
		else
			set_env "USE_OPENWISP_RADIUS" "No"
		fi
		# VPN domain
		if [[ -z "$vpn_domain" ]]; then
			set_env "VPN_DOMAIN" "vpn.${domain}"
		elif [[ "${vpn_domain,,}" == "n" ]]; then
			set_env "VPN_DOMAIN" "example.com"
		else
			set_env "VPN_DOMAIN" "$vpn_domain"
		fi
		# Site manager email
		set_env "EMAIL_DJANGO_DEFAULT" "$django_default_email"
		# Set random secret values
		python3 $INSTALL_PATH/build.py change-secret-key >/dev/null
		python3 $INSTALL_PATH/build.py change-database-credentials >/dev/null
		# SSL Configuration
		set_env "CERT_ADMIN_EMAIL" "$letsencrypt_email"
		if [[ -z "$letsencrypt_email" ]]; then
			set_env "SSL_CERT_MODE" "SelfSigned"
		else
			set_env "SSL_CERT_MODE" "Yes"
		fi
		# Other
		hostname=$(echo "$django_default_email" | cut -d @ -f 2)
		set_env "POSTFIX_ALLOWED_SENDER_DOMAINS" "$hostname"
		set_env "POSTFIX_MYHOSTNAME" "$hostname"
	else
		mv $ENV_USER $INSTALL_PATH/.env &>>$LOG_FILE
		rm -rf $ENV_USER &>>$LOG_FILE
	fi

	start_step "Configuring docker-openwisp..."
	report_ok
	start_step "Starting images docker-openwisp (this will take a while)..."
	make start TAG=$(cat $INSTALL_PATH/VERSION) -C $INSTALL_PATH/ &>>$LOG_FILE
	check_status $? "Starting openwisp failed."
}

upgrade_docker_openwisp() {
	echo -e ${GRN}"\nOpenWISP Configuration:"${NON}
	echo -ne ${GRN}"OpenWISP Version (leave blank for latest): "${NON}
	read openwisp_version
	if [[ -z "$openwisp_version" ]]; then openwisp_version=latest; fi
	echo ""

	start_step "Downloading docker-openwisp..."
	cp $INSTALL_PATH/.env $ENV_BACKUP &>>$LOG_FILE
	rm -rf $INSTALL_PATH &>>$LOG_FILE

	if [[ $openwisp_version -ne "edge" ]]; then
		git clone $GIT_PATH $INSTALL_PATH --depth 1 --branch $openwisp_version &>>$LOG_FILE
	else
		git clone $GIT_PATH $INSTALL_PATH --depth 1 &>>$LOG_FILE
	fi

	cd $INSTALL_PATH &>>$LOG_FILE
	check_status $? "docker-openwisp download failed."
	echo $openwisp_version >$INSTALL_PATH/VERSION

	start_step "Configuring docker-openwisp..."
	for config in $(grep '=' $ENV_BACKUP | cut -f1 -d'='); do
		value=$(get_env "$config" "$ENV_BACKUP")
		set_env "$config" "$value"
	done
	report_ok

	start_step "Starting images docker-openwisp (this will take a while)..."
	make start TAG=$(cat $INSTALL_PATH/VERSION) -C $INSTALL_PATH/ &>>$LOG_FILE
	check_status $? "Starting openwisp failed."
}

give_information_to_user() {
	dashboard_domain=$(get_env "DASHBOARD_DOMAIN" "$INSTALL_PATH/.env")
	db_user=$(get_env "DB_USER" "$INSTALL_PATH/.env")
	db_pass=$(get_env "DB_PASS" "$INSTALL_PATH/.env")

	echo -e ${GRN}"\nYour setup is ready, your dashboard should be available on https://${dashboard_domain} in 2 minutes.\n"
	echo -e "You can login on the dashboard with"
	echo -e "    username: admin"
	echo -e "    password: admin"
	echo -e "Please remember to change these credentials.\n"
	echo -e "Random database user and password generate by the script:"
	echo -e "    username: ${db_user}"
	echo -e "    password: ${db_pass}"
	echo -e "Please note them, might be helpful for accessing postgresql data in future.\n"${NON}
}

upgrade_debian() {
	apt_dependenices_setup
	upgrade_docker_openwisp
	dashboard_domain=$(get_env "DASHBOARD_DOMAIN" "$INSTALL_PATH/.env")
	echo -e ${GRN}"\nYour upgrade was successfully done."
	echo -e "Your dashboard should be available on https://${dashboard_domain} in 2 minutes.\n"${NON}
}

install_debian() {
	apt_dependenices_setup
	setup_docker
	setup_docker_compose
	setup_docker_openwisp
	give_information_to_user
}

init_setup() {
	if [[ "$1" == "upgrade" ]]; then
		echo -e ${GRN}"Welcome to OpenWISP auto-upgradation script."
		echo -e "You are running the upgrade option to change version of"
		echo -e "OpenWISP already setup with this script.\n"${NON}
	else
		echo -e ${GRN}"Welcome to OpenWISP auto-installation script."
		echo -e "Please ensure following requirements:"
		echo -e "  - Fresh instance"
		echo -e "  - 2GB RAM (Minimum)"
		echo -e "  - Root privileges"
		echo -e "  - Supported systems"
		echo -e "    - Debian: 10 & 11"
		echo -e "    - Ubuntu 18.04, 18.10 & 20.04"
		echo -e ${YLW}"\nYou can use -u\--upgrade if you are upgrading from an older version.\n"${NON}
	fi

	if [ "$EUID" -ne 0 ]; then
		echo -e ${RED}"Please run with root privileges."${NON}
		exit 1
	fi

	mkdir -p /opt/openwisp
	echo "" >$LOG_FILE

	start_step "Checking your system capabilities..."
	apt update &>>$LOG_FILE
	apt -qq --yes install lsb-release &>>$LOG_FILE
	system_id=$(lsb_release --id --short)
	system_release=$(lsb_release --release --short)
	incompatible_message="$system_id $system_release is not support. Installation might fail, continue anyway? (Y/n): "

	if [[ "$system_id" == "Debian" || "$system_id" == "Ubuntu" ]]; then
		case "$system_release" in
		18.04 | 20.04 | 10 | 11)
			if [[ "$1" == "upgrade" ]]; then
				report_ok && upgrade_debian
			else
				report_ok && install_debian
			fi
			;;
		*)
			error_msg_with_continue "$incompatible_message"
			install_debian
			;;
		esac
	else
		error_msg_with_continue "$incompatible_message"
		install_debian
	fi
}

init_help() {
	echo -e ${GRN}"Welcome to OpenWISP auto-installation script.\n"

	echo -e "Please ensure following requirements:"
	echo -e "  - Fresh instance"
	echo -e "  - 2GB RAM (Minimum)"
	echo -e "  - Root privileges"
	echo -e "  - Supported systems"
	echo -e "    - Debian: 10 & 11"
	echo -e "    - Ubuntu 18.04, 18.10 & 20.04\n"
	echo -e "  -i\--install : (default) Install OpenWISP"
	echo -e "  -u\--upgrade : Change OpenWISP version already setup with this script"
	echo -e "  -h\--help    : See this help message"
	echo -e ${NON}
}

## Parse command line arguements
while test $# != 0; do
	case "$1" in
	-i | --install) action='install' ;;
	-u | --upgrade) action='upgrade' ;;
	-h | --help) action='help' ;;
	*) action='help' ;;
	esac
	shift
done

## Init script
if [[ "$action" == "help" ]]; then
	init_help
elif [[ "$action" == "upgrade" ]]; then
	init_setup upgrade
else
	init_setup
fi
