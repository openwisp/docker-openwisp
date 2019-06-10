#!/bin/bash
# This script will ensure that the following services are running:
# - Django (dashboard)
# - Redis
# - Postfix

function print_services_logs {
    echo "Containers:"
    docker container ls -a
    echo "Dashboard logs:"
    docker-compose logs dashboard
    echo "Controller logs:"
    docker-compose logs controller
    echo "Radius logs:"
    docker-compose logs radius
    echo "Network Topology logs:"
    docker-compose logs topology
    echo "postfix logs:"
    docker-compose logs postfix
    echo "postgresql logs:"
    docker-compose logs postgres
    echo "nginx logs:"
    docker-compose logs nginx
    echo "nginx logs:"
    docker-compose logs redis
}

function dashboard_admin_login {
    # This function is used to login into django-admin
    # It creates the cookie.txt file that containes CSRF
    # token and session ID.
    $CURL_BIN $LOGIN_URL > /dev/null
    DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | \
                    sed 's/^.*csrftoken[[:blank:]]*//')"
    $CURL_BIN -d "$DJANGO_TOKEN;username=$USERNAME;password=$PASSWORD" \
                -X POST --dump-header - $LOGIN_URL | grep -q "302 Found" && \
                { echo "SUCCESS: Login request acknowledgement received!"; } || \
                { echo "ERROR: Login request acknowledgement not received!"; FAILURE=1; }
    }

function run_dashboard_tests {
    # This tests the login was successful; being able to
    # access this page also means redis is running.
    $CURL_BIN --head http://dashboard.openwisp.org/admin/ | grep -q "200 OK" && \
              { echo "SUCCESS: Admin login successful!"; } || \
              { echo "ERROR: Admin login failed!"; FAILURE=1; }
}

function forgot_password_send_email {
    # This test ensures that postfix service is running
    # correctly.
    $CURL_BIN $LOGIN_URL > /dev/null
    DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | \
                  sed 's/^.*csrftoken[[:blank:]]*//')"
    $CURL_BIN -d "$DJANGO_TOKEN;email=admin@example.com" \
              -X POST --dump-header - \
              http://dashboard.openwisp.org/accounts/password/reset/ | grep -q "302 Found" && \
            { echo "SUCCESS: Postfix service is working."; } || \
            { echo "ERROR: Postfix service did not respond."; FAILURE=1; }
}

function wait_for_services {
    # Wait for services to start up and then check
    # if the openwisp-dashboard is reachable.
    FAILURE=1
    for ((i=1;i<=10;i++)); do
        curl -s --head http://dashboard.openwisp.org/admin/login/ | grep -q "200 OK"
        if [[ $? = "0" ]]; then
            echo "SUCCESS: openwisp-dashboard login page reachable!"
            FAILURE=0
            break
        fi
        sleep 5
    done
    if [[ $FAILURE = 1 ]]; then
        echo "ERROR: openwisp-dashboard login page not reachable!"
    fi
}

function init_dashoard_tests {
    LOGIN_URL=http://dashboard.openwisp.org/admin/login/
    USERNAME='admin'
    PASSWORD='admin'
    COOKIES=cookies.txt
    CURL_BIN="curl -s -c $COOKIES -b $COOKIES -e $LOGIN_URL"
    FAILURE=0
    touch $COOKIES
    wait_for_services
    forgot_password_send_email
    dashboard_admin_login
    run_dashboard_tests
    if [[ $FAILURE = 1 ]]; then
        print_services_logs
    fi
    rm $COOKIES
    exit $FAILURE
}
