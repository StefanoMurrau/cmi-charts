#!/bin/bash

help () {
    echo $1
    echo \"werkzeug\" for development environment.
    echo \"gunicorn\" for development/production environment with "gunicorn" web server.
    echo \"help\" to show this message.
}

check_env () {
    export VIRTUAL_ENV=venv
    export ENV=$1

    if [ ! -f "$PWD/$VIRTUAL_ENV/bin/activate" ]; then
        echo "[-] INSTALLING VIRTUALENV"
        pip3 install virtualenv
        python3 -m venv $VIRTUAL_ENV
        if [ $? -eq 0 ]; then
            echo "[*] VIRTUALENV INSTALLED SUCCESSFULLY"
        else
            echo "[X] ERROR: CANNOT INSTALL VIRTUALENV"
            exit 1
        fi
    fi

    echo "[-] ACTIVATING VIRTUALENV"
    source "$PWD/$VIRTUAL_ENV/bin/activate"
    if [ $? -eq 0 ]; then
        echo "[*] VIRTUALENV ACTIVATED SUCCESSFULLY"
    else
        echo "[X] ERROR: CANNOT ACTIVATE VIRTUALENV"
        exit 1
    fi
    
    echo "[-] CHECKING PIP VERSION"
    python3 -m pip install --upgrade pip
    if [ $? -eq 0 ]; then
        echo "[*] LATEST PIP VERSION INSTALLED"
    else
        echo "[X] ERROR: CANNOT INSTALL LATEST PIP VERSION"
    fi

    echo "[-] CHECKING REQUIREMENTS"
    pip3 install wheel & pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "[*] ALL REQUIREMENTS INSTALLED SUCCESSFULLY"
    else
        echo "[X] ERROR: CANNOT INSTALL ALL REQUIREMENTS"
        exit 1
    fi

    echo "[-] STARTINS DB MIGRATION"
    flask db upgrade
    if [ $? -eq 0 ]; then
        echo "[*] DB MIGRATION COMPLETED SUCCESSFULLY"
    else
        echo "[X] ERROR: CANNOT COMPLETE DB MIGRATION"
        exit 1
    fi

    echo "[-] STARTINS DB SEEDING"
    flask seed run
    if [ $? -eq 0 ]; then
        echo "[*] DB SEEDING COMPLETED SUCCESSFULLY"
        echo
    else
        echo "[X] ERROR: CANNOT COMPLETE DB SEEDING"
        exit 1
    fi

    if [ "$ENV" == "werkzeug" ]
        then
            python3 run.py
    fi

    if [ "$ENV" == "gunicorn" ]
        then
            gunicorn -w 4 run:app
    fi

    exit 0
}

if [ "$#" -eq 0 ]; then
    help "Missing parameter(s)."
    exit 0
fi

if [ "$1" == help ]; then
    help "Help - Please use one of the parameters below."
    exit 0
fi

if [ "$#" -gt 1 ]; then
    help "Too many parameters"
    exit 0
fi

if [ "$1" == "werkzeug" ]; then
    check_env "werkzeug"
fi

if [ "$1" == "gunicorn" ]; then
    check_env "gunicorn"
fi

help "Unrecognized parameter(s)."
exit 0
