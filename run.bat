@ECHO OFF
setlocal enabledelayedexpansion

:MAIN
    IF "%1" == "" (
        CALL :HELP "Missing parameters."
        EXIT /B
    )

    IF "%1" == "help" (
        CALL :HELP "Help - Please use one of the parameters below."
        EXIT /B
    ) 

    IF NOT [%2] == [] (
        CALL :HELP "Too many parameters"
        EXIT /B
    ) 

    IF "%1" == "werkzeug" ( 
        goto CHECK_ENV "werkzeug"
    ) 
    
    IF "%1" == "waitress" ( 
        goto CHECK_ENV "waitress "
    ) 

    CALL :HELP "Unrecognized parameter."

    EXIT /B  

:HELP
    echo %~1
    echo "werkzeug" for development environment.
    echo "waitress" for development/production environment with "waitress" web server.
    echo "help" to show this message.

    EXIT /B

:INSTALL_VENV
    pip.exe install virtualenv && python.exe -m venv %VIRTUAL_ENV% 

    EXIT /B

:CHECK_ENV
    SET VIRTUAL_ENV=venv
    SET WD=%~dp0
    SET ENV=%~1

    IF NOT EXIST "%VIRTUAL_ENV%\Scripts\activate.bat" (
        ECHO [-] INSTALLING VIRTUALENV
        CALL :INSTALL_VENV

        IF !ERRORLEVEL! neq 0 ( 
            ECHO [X] ERROR: CANNOT INSTALL VIRTUALENV
            EXIT /B 1
        ) ELSE (
            ECHO [*] VIRTUALENV ACTIVATED SUCCESSFULLY    
        )
    )
  
    CALL "%WD%%VIRTUAL_ENV%\Scripts\activate.bat"

    ECHO [-] CHECKING PIP VERSION
    python.exe -m pip install --upgrade pip
    IF !ERRORLEVEL! neq 0 ( 
        ECHO [X] ERROR: CANNOT INSTALL LATEST PIP VERSION
    ) ELSE (
        ECHO [*] LATEST PIP VERSION INSTALLED    
    )

    ECHO [-] CHECKING REQUIREMENTS
    pip install wheel & pip install -r requirements.txt
    IF !ERRORLEVEL! neq 0 ( 
        ECHO [X] ERROR: CANNOT INSTALL ALL REQUIREMENTS
        EXIT /B 1
    ) ELSE (
        ECHO [*] ALL REQUIREMENTS INSTALLED SUCCESSFULLY   
    )

    ECHO "[-] STARTINS DB MIGRATION"
    flask db upgrade
    IF !ERRORLEVEL! neq 0 ( 
        ECHO [X] ERROR: CANNOT COMPLETE DB MIGRATION
        EXIT /B 1
    ) ELSE (
        ECHO [*] DB MIGRATION COMPLETED SUCCESSFULLY   
    )

    ECHO "[-] STARTINS DB SEEDING"
    flask seed run
    IF !ERRORLEVEL! neq 0 ( 
        ECHO [X] ERROR: CANNOT COMPLETE DB SEEDING
        EXIT /B 1
    ) ELSE (
        ECHO [*] DB SEEDING COMPLETED SUCCESSFULLY   
    )


    IF %ENV%==werkzeug (
        python.exe run.py
    )

    IF %ENV%==waitress (
        pip.exe install waitress
        ECHO Serving on http://127.0.0.1:4041
        waitress-serve --call --url-scheme=https --threads=4 --port=4041 app:create_app  
    )
    