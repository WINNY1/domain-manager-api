#!/usr/bin/env bash
function start_gunicorn() {
    nohup gunicorn -w 4 -b 127.0.0.1:8081 run:app &
}

function stop_gunicorn() {
    ps aux | grep gunicorn | grep -v grep | awk '{ print $2 }' | xargs kill
}

function main()
{
    action=$1
    case ${action} in
        "start")
            start_gunicorn
            ;;
        "stop")
            stop_gunicorn
            ;;
        "restart")
            stop_gunicorn
            start_gunicorn
            ;;
        *)
            echo "Bad argument!"
            ;;
    esac
}

main $*
