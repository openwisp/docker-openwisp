#!/bin/bash

function dashboard_admin_login {
    # This function is used to login into django-admin
    # It creates the cookie.txt file that containes CSRF
    # token and session ID.
    touch $COOKIES
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

function wait_for_services {
    # Waits for services to start up and then checks 
    # if the openwisp-dashboard is reachable
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
    wait_for_services
    dashboard_admin_login
    run_dashboard_tests
    rm $COOKIES
    exit $FAILURE
}
