#!/bin/bash
# This script will ensure that the following services are running:
# - Django (dashboard)
# - Redis
# - Postfix
# - Websocket

function print_services_logs {
    # Print logs of the containers in case of failure
    # to help with debugging in travis-ci. first arguement
    # needs to be "logs" for this function to be called.
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

function admin_login {
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

function test_dashboard_login {
    # This tests the login was successful; being able to
    # access this page also means redis is running.
    $CURL_BIN --head http://dashboard.openwisp.org/admin/ | grep -q "200 OK" && \
              { echo "SUCCESS: Admin login successful!"; } || \
              { echo "ERROR: Admin login failed!"; FAILURE=1; }
}

function test_postfix {
    # This test ensures that postfix service is running
    # correctly by making a request to reset password.
    $CURL_BIN $LOGIN_URL > /dev/null
    DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | \
                  sed 's/^.*csrftoken[[:blank:]]*//')"
    $CURL_BIN -d "$DJANGO_TOKEN;email=admin@example.com" \
              -X POST --dump-header - \
              http://dashboard.openwisp.org/accounts/password/reset/ | grep -q "302 Found" && \
            { echo "SUCCESS: Postfix service is working!"; } || \
            { echo "ERROR: Postfix service did not respond!"; FAILURE=1; }
}

function test_websocket {
    # This test ensures that wesocket service is running
    # correctly by trying to reach \ws location in nginx.
    timeout 2 $CURL_BIN --include \
                        --no-buffer \
                        --header "Connection: Upgrade" \
                        --header "Upgrade: websocket" \
                        --header "Host: dashboard.openwisp.org" \
                        --header "Origin: https://dashboard.openwisp.org" \
                        --header "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
                        --header "Sec-WebSocket-Version: 13" \
               http://dashboard.openwisp.org/ws/ | \
        grep -q "101 Switching Protocols" && \
        { echo "SUCCESS: Websocket service is working!"; } || \
        { echo "ERROR: Websocket service did not respond!"; FAILURE=1; }
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
    # Init function that can be called to run tests
    # for all the services.
    LOGIN_URL=http://dashboard.openwisp.org/admin/login/
    USERNAME='admin'
    PASSWORD='admin'
    COOKIES=cookies.txt
    CURL_BIN="curl -s -c $COOKIES -b $COOKIES -e $LOGIN_URL"
    FAILURE=0
    touch $COOKIES
    wait_for_services
    test_postfix
    admin_login
    test_dashboard_login
    test_websocket
    if [[ $FAILURE = 1 ]] && [[ $1 = logs ]]; then
        print_services_logs
    fi
    rm $COOKIES
    exit $FAILURE
}
