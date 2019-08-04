#!/bin/bash

function pre_testcases {
    # Actions to be performed before tests
    case $2 in
        http) APP_PROTOCOL="http";;
        *)    APP_PROTOCOL="https";;
    esac
    TEST_LOGS=tests.logs
    touch $TEST_LOGS
	mv .env tests/testcases/.env
	mv tests/testcases/${2}.env .env
    echo -e "\nTesting with: ${1}.sh and ${2}.env:"
    echo -e "Starting containers for test. (This may take a while)\n"
    docker-compose up -d &>> $TEST_LOGS
}

function post_testcases {
    docker-compose stop &>> $TEST_LOGS
    if [[ $FAILURE = 1 ]] && [[ $CI ]]; then
        print_services_logs
        exit $FAILURE
    fi
    # Actions to be performed after tests
	mv .env tests/testcases/${2}.env
	mv tests/testcases/.env .env
    rm $TEST_LOGS
}

function init_tests {
    source tests/$1.sh
    pre_testcases $1 $2
    call_tests $APP_PROTOCOL
    post_testcases $1 $2
}
