@echo off
SETLOCAL ENABLEEXTENSIONS DISABLEDELAYEDEXPANSION

:: ==============================================================================
:: NOME DO SCRIPT: build_instaler.cmd
:: PROPOSITO    : Automatiza a build do executavel e a criacao do instalador NSIS
:: AUTOR        : Desenvolvedor RealTime-Screen-Translator
:: DATA         : 28/06/2026
:: ==============================================================================

:: --- CONFIGURACOES E CONSTANTES ---
SET "PY_SCRIPT=main.py"
SET "APP_NAME=RealTimeScreenTranslator"
SET "MAKENSIS=C:\Program Files (x86)\NSIS\makensis.exe"
SET "NSIS_SCRIPT=%~dp0instalador.nsi"
:: Ambiente so de build, com o PyTorch de CPU (veja "Build the installer" no README).
:: O PyTorch com CUDA passa de 2 GB, o limite do NSIS; ele e baixado depois da
:: instalacao, so em PCs com placa NVIDIA (aceleracao_gpu.py).
SET "PYINSTALLER=%~dp0env_build\Scripts\pyinstaller.exe"

echo [INFO] Iniciando build do RealTimeScreenTranslator...

:: Verificacao de seguranca: checa se os arquivos existem antes de executar
IF NOT EXIST "%PY_SCRIPT%" (
    echo [ERRO] Arquivo %PY_SCRIPT% nao encontrado!
    EXIT /b 1
)
IF NOT EXIST "%PYINSTALLER%" (
    echo [ERRO] Ambiente de build nao encontrado em env_build. Veja "Build the installer" no README.
    EXIT /b 1
)

echo [INFO] Executando PyInstaller...
:: O uso direto do .exe evita ambiguidades e a necessidade do comando CALL
:: --onedir gera uma pasta: o app abre sem descompactar tudo a cada uso
:: --icon define o icone do .exe; --add-data leva o mesmo arquivo para a janela e a bandeja
:: --runtime-hook faz o app usar o PyTorch com CUDA da pasta gpu, quando ele existir
"%PYINSTALLER%" --clean --noconfirm --noconsole --onedir --name="%APP_NAME%" --icon="assets\icone.ico" --add-data="assets\icone.ico;assets" --runtime-hook="pyi_gancho_gpu.py" "%PY_SCRIPT%"
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha no PyInstaller!
    EXIT /b 1
)

echo [INFO] Executando NSIS...
:: Aspas duplas protegem contra injecao de comandos
"%MAKENSIS%" "%NSIS_SCRIPT%"
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao compilar o instalador!
    EXIT /b 1
)

echo.
echo [SUCESSO] O instalador foi gerado na pasta do projeto.
echo.

ENDLOCAL
EXIT /b 0