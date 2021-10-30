#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export INSTALL_PATH=/opt/openwisp/docker-openwisp
export LOG_FILE=/opt/openwisp/autoinstall.log
# Terminal colors
export RED='\033[1;31m'
export GRN='\033[1;32m'
export YLW='\033[1;33m'
export BLU='\033[1;34m'
export NON='\033[0m'

start_step() { printf '\e[1;34m%-70s\e[m' "$1" && echo "$1" &>> $LOG_FILE; }
report_ok() { echo -e ${GRN}" done"${NON}; }
report_error() { echo -e ${RED}" error"${NON}; }
get_env() { grep "$1" $INSTALL_PATH/.env | cut -d'=' -f 2-50; }
set_env() {
    grep -q "^$1=" $INSTALL_PATH/.env &&
    sed --in-place "s/$1=.*/$1=$2/g" $INSTALL_PATH/.env ||
    echo "$1=$2" >> $INSTALL_PATH/.env
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
    echo -ne ${RED}${1}${NON};
    read reply;
    if [[ ! $reply =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

apt_dependenices_setup() {
    start_step "Setting up dependencies...";
    apt --yes install python3 python3-pip git python3-dev libffi-dev libssl-dev gcc make &>> $LOG_FILE
    check_status $? "Python dependencies installation failed."
}

setup_docker() {
    start_step "Setting up docker...";
    docker info &> /dev/null
    if [ $? -eq 0 ]; then
        report_ok
    else
        curl -fsSL 'https://get.docker.com' -o '/opt/openwisp/get-docker.sh' &>> $LOG_FILE;
        sh '/opt/openwisp/get-docker.sh' &>> $LOG_FILE
        docker info &> /dev/null
        check_status $? "Docker installation failed."
    fi
}

setup_docker_compose() {
    start_step "Setting up docker-compose...";
    python3 -m pip install docker-compose &>> $LOG_FILE
    docker-compose version &> /dev/null
    check_status $? "docker-compose installation failed.";
}

setup_docker_openwisp() {
    git_path="https://github.com/openwisp/docker-openwisp.git";
    env_user="/opt/openwisp/config.env";
    echo -e ${GRN}"\nOpenWISP Configuration:"${NON};
    echo -ne ${GRN}"OpenWISP Version (leave blank for latest): "${NON}; read openwisp_version;
    if [[ -z "$openwisp_version" ]]; then openwisp_version=latest; fi
    echo -ne ${GRN}"Do you have .env file? Enter filepath (leave blank for ad-hoc configuration): "${NON};
    read env_path;
    if [[ ! -f "$env_path" ]]; then
        # Dashboard Domain
        echo -ne ${GRN}"(1/6) Enter dashboard domain: "${NON};
        read dashboard_domain;
        domain=$(echo "$dashboard_domain" | cut -f2- -d'.')
        # API Domain
        echo -ne ${GRN}"(2/6) Enter API domain (blank for api.${domain}): "${NON};
        read API_DOMAIN;
        # Radius Domain
        echo -ne ${GRN}"(3/6) Enter radius domain (blank for radius.${domain}, N to disable module): "${NON};
        read radius_domain;
        # VPN domain
        echo -ne ${GRN}"(4/6) Enter OpenVPN domain (blank for vpn.${domain}, N to disable module): "${NON};
        read vpn_domain;
        # Site manager email
        echo -ne ${GRN}"(5/6) Site manager email: "${NON};
        read django_default_email;
        # VPN domain
        echo -ne ${GRN}"(6/6) Enter letsencrypt email (leave blank for self-signed certificate): "${NON};
        read letsencrypt_email;
    else
        cp $env_path $env_user &>> $LOG_FILE;
    fi
    echo "";

    start_step "Downloading docker-openwisp...";
    if [[ -f $INSTALL_PATH/.env ]]; then
        mv $INSTALL_PATH/.env /opt/openwisp/docker.env &>> $LOG_FILE;
        rm -rf $INSTALL_PATH &>> $LOG_FILE;
    fi

    if [[ $openwisp_version -ne "edge" ]]; then
        git clone $git_path $INSTALL_PATH --depth 1 --branch $openwisp_version &>> $LOG_FILE;
    else
        git clone $git_path $INSTALL_PATH --depth 1 &>> $LOG_FILE;
    fi

    cd $INSTALL_PATH &>> $LOG_FILE;
    echo $openwisp_version > $INSTALL_PATH/VERSION
    check_status $? "docker-openwisp download failed.";

    if [[ ! -f "$env_path" ]]; then
        # Dashboard Domain
        set_env "DASHBOARD_DOMAIN" "$dashboard_domain";
        # API Domain
        if [[ -z "$API_DOMAIN" ]]; then
            set_env "API_DOMAIN" "api.${domain}";
        else
            set_env "API_DOMAIN" "$API_DOMAIN";
        fi
        # Radius Domain
        if [[ -z "$radius_domain" ]]; then
            set_env "RADIUS_DOMAIN" "radius.${domain}";
        elif [[ "${radius_domain,,}" == "n" ]]; then
            set_env "USE_OPENWISP_RADIUS" "No";
        else
            set_env "RADIUS_DOMAIN" "$radius_domain";
            set_env "USE_OPENWISP_RADIUS" "Yes";
        fi
        # VPN domain
        if [[ -z "$vpn_domain" ]]; then
            set_env "VPN_DOMAIN" "vpn.${domain}";
        elif [[ "${vpn_domain,,}" == "n" ]]; then
            set_env "VPN_DOMAIN" "example.com";
        else
            set_env "VPN_DOMAIN" "$vpn_domain";
        fi
        # Site manager email
        set_env "EMAIL_DJANGO_DEFAULT" "$django_default_email";
        # Set random secret values
        python3 $INSTALL_PATH/build.py change-secret-key > /dev/null
        python3 $INSTALL_PATH/build.py change-database-credentials > /dev/null
        # VPN domain
        set_env "CERT_ADMIN_EMAIL" "$letsencrypt_email";
        if [[ -z "$letsencrypt_email" ]]; then
            set_env "SSL_CERT_MODE" "SelfSigned";
        else
            set_env "SSL_CERT_MODE" "Yes";
        fi
        # Other
        hostname=$(echo "$django_default_email" | cut -d @ -f 2)
        set_env "POSTFIX_ALLOWED_SENDER_DOMAINS" "$hostname"
        set_env "POSTFIX_MYHOSTNAME" "$hostname"
        set_env "POSTFIX_MYHOSTNAME" "$hostname"
    else
        mv $env_user $INSTALL_PATH/.env &>> $LOG_FILE;
        rm -rf $env_user &>> $LOG_FILE;
    fi

    start_step "Configuring docker-openwisp...";
    report_ok
    start_step "Starting images docker-openwisp (this will take a while)...";
    make start TAG=$(cat $INSTALL_PATH/VERSION) -C $INSTALL_PATH/ &>> $LOG_FILE
    check_status $? "Starting openwisp failed.";
}

give_information_to_user() {
    dashboard_domain=$(get_env "DASHBOARD_DOMAIN");
    db_user=$(get_env "DB_USER");
    db_pass=$(get_env "DB_PASS");
    echo -e ${GRN}"
Your setup is ready, your dashboard should be avaiable on https://$dashboard_domain in 2 minutes.
You can login on the dashboard with
    username: admin
    password: admin
Please remember to change these credentials.
Random database user and password generate by the script:
   username: $db_user
   password: $db_pass
Please note them, might be helpful for accessing postgresql data in future.
"${NON}
}

prep_debian() {
    apt_dependenices_setup
    setup_docker
    setup_docker_compose
    setup_docker_openwisp
    give_information_to_user
}

prep_debian_10() {
    prep_debian
}

init_setup() {
    echo -e ${GRN}"
Welcome to OpenWISP auto-installation script.
Please ensure following requirements:
- Fresh instance
- 2GB RAM (Min)
- Debian 10 / Ubuntu 18.04
- Root privileges\n"${NON}

    if [ "$EUID" -ne 0 ]; then
        echo -e ${RED}"Please run with root privileges."${NON};
        exit 1;
    fi

    mkdir -p /opt/openwisp;
    echo "" > $LOG_FILE;

    start_step "Checking your system capabilities...";
    apt --yes update &>> $LOG_FILE
    apt -qq --yes install lsb-release &>> $LOG_FILE
    system_id=$(lsb_release --id --short)
    system_release=$(lsb_release --release --short)
    incompatible_message="$system_id $system_release is not support. Installation might fail, continue anyway? (Y/n): "

    if [ "$system_id" == "Debian" ]; then
        case "$system_release" in
            10) report_ok && prep_debian_10;;
            *)
                error_msg_with_continue "$incompatible_message"
                prep_debian
                ;;
        esac
    elif [ "$system_id" == "Ubuntu" ]; then
        case "$system_release" in
            18.04) report_ok && prep_debian;;
            *)
                error_msg_with_continue "$incompatible_message"
                prep_debian
                ;;
        esac
    else
        error_msg_with_continue "$incompatible_message"
        prep_debian
    fi
}

init_setup
