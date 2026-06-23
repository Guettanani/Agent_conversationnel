@echo off
chcp 65001 >nul
echo.
echo =============================================
echo     OpenRouter Chat (CMD) - Gratuit
echo =============================================
echo.

:: Mets ta clé ici (ou laisse vide pour la variable système)
set "API_KEY=%OPENROUTER_API_KEY%"

if "%API_KEY%"=="" (
    echo ERREUR: La variable OPENROUTER_API_KEY n'est pas definie.
    echo Tape cette commande d'abord :
    echo setx OPENROUTER_API_KEY "sk-or-v1-ta_clé_ici"
    pause
    exit
)

:chat
echo.
set /p "question=Toi > "

if /i "%question%"=="exit" goto end
if /i "%question%"=="quit" goto end

curl -s https://openrouter.ai/api/v1/chat/completions ^
  -H "Authorization: Bearer %API_KEY%" ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"openrouter/free\", \"messages\": [{\"role\": \"user\", \"content\": \"%question%\"}]}" | findstr "content" 

echo.
goto chat

:end
echo Au revoir !
pause