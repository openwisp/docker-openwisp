#!/bin/bash
: """
This script will ensure that the following services are running:
- Django (dashboard)
- Redis
- Postfix
- Freeradius
- Celery
"""

function print_services_logs {
    # Print logs of the containers in case of failure
    # to help with debugging in travis-ci. first arguement
    # needs to be "logs" for this function to be called.
    echo "Pre-test logs:"
    cat $PRE_LOGS
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
    echo "Celery logs:"
    docker-compose logs celery
    echo "Postfix logs:"
    docker-compose logs postfix
    echo "Postgresql logs:"
    docker-compose logs postgres
    echo "freeradius logs:"
    docker-compose logs freeradius
    echo "Nginx logs:"
    docker-compose logs nginx
    echo "Redis logs:"
    docker-compose logs redis
}

function test_admin_login {
    # This function is used to login into django-admin
    python3 $PWD/tests/tests.py TestServices.test_admin_login || FAILURE=1
}

function test_dashboard_login {
    # This tests the login was successful; being able to
    # access this page also means redis is running.
    $CURL_BIN --head ${APP_URL}/admin/ | grep -q "200 OK" && \
                { echo "SUCCESS: Admin login successful!"; } || \
                { echo "ERROR: Admin login failed!"; FAILURE=1; }
}

function test_postfix {
    # This test ensures that postfix service is running
    # correctly by making a request to reset password.
    $CURL_BIN ${APP_URL}/admin/login/ > /dev/null
    DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | \
                  sed 's/^.*csrftoken[[:blank:]]*//')"
    $CURL_BIN -d "$DJANGO_TOKEN;email=admin@example.com" \
              -X POST --dump-header - \
              ${APP_URL}/accounts/password/reset/ | grep -q "302 Found" && \
            { echo "SUCCESS: Postfix service is working!"; } || \
            { echo "ERROR: Postfix service did not respond!"; FAILURE=1; }
}

function test_freeradius {
    # This test ensures that freeradius service is running correctly.
    docker run -it --rm --network docker-openwisp_default 2stacks/radtest \
               radtest admin admin freeradius 0 testing123 | \
               grep -q "Received Access-Accept" && \
            { echo "SUCCESS: Freeradius service is working!"; } || \
            { echo "ERROR: Freeradius service did not respond!"; FAILURE=1; }
}

function test_celery {
    # This test ensures that celery status returns "OK".
    echo `docker-compose run --rm celery celery -A openwisp status 2> /dev/null` | \
        grep -q "OK" && \
            { echo "SUCCESS: Celery service is working!"; } || \
            { echo "ERROR: Celery service did not respond!"; FAILURE=1; }
}

function wait_for_services {
    # Wait for services to start up and then check
    # if the openwisp-dashboard is reachable.
    python3 $PWD/tests/tests.py Pretest || FAILURE=1
}

function pre_tests {
    # Functions need to performed before tests.
    docker pull 2stacks/radtest:latest &>> $PRE_LOGS
    docker-compose run --rm \
                       --entrypoint 'python manage.py shell --command="import pre_tests; pre_tests.setup()"' \
                       --volume $PWD/tests/pre_tests.py:/opt/openwisp/pre_tests.py \
                       dashboard &>> $PRE_LOGS
    docker-compose up -d freeradius &>> $PRE_LOGS
}

function init_tests {
    # Init function that can be called to run tests
    # for all the services.
    APP_URL=http://dashboard.openwisp.org
    USERNAME='admin'
    PASSWORD='admin'
    PRE_LOGS=pre_logs.logs
    COOKIES=cookies.txt
    CURL_BIN="curl -s -c $COOKIES -b $COOKIES -e ${APP_URL}/admin/login/"
    FAILURE=0
    touch $COOKIES $PRE_LOGS
    wait_for_services
    pre_tests
    test_postfix
    test_admin_login
    test_celery
    test_dashboard_login
    test_freeradius
    if [[ $FAILURE = 1 ]] && [[ $TRAVIS ]]; then
        print_services_logs
    fi
    rm $COOKIES $PRE_LOGS
    if [[ $FAILURE = 1 ]]; then
        exit $FAILURE
    fi
}
