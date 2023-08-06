#!/bin/bash

delete_pycache () {
    for f in $(find . -name '__pycache__')
        do echo Deleting folder: $f; rm -rf $f
    done
}

delete_flask_session () {
    rm -rf -v ./flask_session/
}

delete_pycache
delete_flask_session
