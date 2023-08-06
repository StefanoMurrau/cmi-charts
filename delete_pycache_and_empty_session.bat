@ECHO OFF 

FOR /d /r . %%d IN (__pycache__) DO (
    @IF EXIST "%%d" (
        echo Deleting folder: %%d
        rd /s /q "%%d"
    )
)

SET WD=%~dp0
@IF EXIST "%WD%flask_session" (
        echo Deleting folder: "%WD%flask_session"
        rd /s /q "%WD%flask_session"
    )
)
