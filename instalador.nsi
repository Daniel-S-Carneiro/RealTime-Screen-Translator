; ============================================================================
; SCRIPT DE INSTALAÇÃO NSIS - REALTIME SCREEN TRANSLATOR
; Licença: GNU General Public License v3.0 (GPLv3)
; ============================================================================

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WordFunc.nsh"

; ----------------------------------------------------------------------------
; Configurações Globais (Codificação e Resolução)
; ----------------------------------------------------------------------------
; Define o uso de Unicode (Obrigatório para acentos)
Unicode true
!define MUI_UNICODE true

; Suporte a telas de alta resolução (evita desfoque)
ManifestDPIAware true

; ----------------------------------------------------------------------------
; Informações Básicas
; ----------------------------------------------------------------------------
Name "RealTime Screen Translator"
OutFile "dist\RealTimeScreenTranslator_Setup.exe"
InstallDir "$PROGRAMFILES64\RealTimeScreenTranslator"
RequestExecutionLevel admin

; Versão deste instalador; o build pode trocar com makensis /DVERSAO=x.y.z
!ifndef VERSAO
  !define VERSAO "1.1.0"
!endif
!define NOME_EXE "RealTimeScreenTranslator.exe"
!define CHAVE_DESINSTALAR "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator"

; Preenchidas no .onInit, conforme já exista ou não uma versão instalada
Var Atualizando
Var VersaoInstalada
Var TextoBoasVindas

; ----------------------------------------------------------------------------
; Configurações da Interface Visual (Modern UI)
; ----------------------------------------------------------------------------
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icone.ico"
!define MUI_UNICON "assets\icone.ico"
!define MUI_WELCOMEPAGE_TITLE "Bem-vindo ao instalador do RealTime Screen Translator"
; O texto muda quando já existe uma versão instalada (veja o .onInit)
!define MUI_WELCOMEPAGE_TEXT "$TextoBoasVindas"

; Opção para rodar o programa automaticamente na tela final de conclusão
!define MUI_FINISHPAGE_RUN "$INSTDIR\RealTimeScreenTranslator.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Executar RealTime Screen Translator agora"

; ----------------------------------------------------------------------------
; Páginas do Instalador (Inseridas apenas uma vez)
; ----------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
; Na atualização a pasta é a da versão instalada, então a escolha de pasta não aparece
!define MUI_PAGE_CUSTOMFUNCTION_PRE PularPastaSeAtualizando
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; ----------------------------------------------------------------------------
; Páginas do Desinstalador
; ----------------------------------------------------------------------------
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; ----------------------------------------------------------------------------
; Idioma do Instalador (Inserido após as páginas)
; ----------------------------------------------------------------------------
!insertmacro MUI_LANGUAGE "PortugueseBR"

; ----------------------------------------------------------------------------
; Detecção de Versão Instalada (Atualização)
; ----------------------------------------------------------------------------
; A atualização só sobrescreve os arquivos da pasta do programa. As configurações e
; as chaves de API ficam em %APPDATA%\RealTimeScreenTranslator e não são tocadas.
Function .onInit
  StrCpy $Atualizando "0"
  ReadRegStr $0 HKLM "${CHAVE_DESINSTALAR}" "UninstallString"
  ${If} $0 == ""
    StrCpy $TextoBoasVindas "Este assistente guiará você na instalação do RealTime Screen Translator ${VERSAO} no seu computador.$\r$\n$\r$\nClique em Avançar para continuar."
    Return
  ${EndIf}

  StrCpy $Atualizando "1"

  ; Instala por cima, na mesma pasta. A 1.0.0 não gravava InstallLocation, então a
  ; pasta sai do caminho do desinstalador ("C:\...\uninstall.exe", com aspas).
  ReadRegStr $1 HKLM "${CHAVE_DESINSTALAR}" "InstallLocation"
  ${If} $1 == ""
    StrCpy $2 $0 1
    ${If} $2 == '"'
      StrCpy $0 $0 "" 1
      StrCpy $0 $0 -1
    ${EndIf}
    ${GetParent} $0 $1
  ${EndIf}
  ${If} $1 != ""
    StrCpy $INSTDIR $1
  ${EndIf}

  ReadRegStr $VersaoInstalada HKLM "${CHAVE_DESINSTALAR}" "DisplayVersion"
  StrCpy $3 "Suas configurações e chaves de API serão mantidas. Se o programa estiver aberto, ele será fechado.$\r$\n$\r$\nClique em Avançar para continuar."
  ${If} $VersaoInstalada == ""
    StrCpy $TextoBoasVindas "Uma versão anterior já está instalada e será atualizada para a ${VERSAO}.$\r$\n$\r$\n$3"
    Return
  ${EndIf}

  ; 0 = versões iguais, 1 = a instalada é mais nova, 2 = a instalada é mais antiga
  ${VersionCompare} "$VersaoInstalada" "${VERSAO}" $4
  ${If} $4 == "0"
    StrCpy $TextoBoasVindas "A versão ${VERSAO} já está instalada e será reinstalada.$\r$\n$\r$\n$3"
  ${ElseIf} $4 == "1"
    StrCpy $TextoBoasVindas "Uma versão mais nova ($VersaoInstalada) já está instalada e será substituída pela ${VERSAO}.$\r$\n$\r$\n$3"
  ${Else}
    StrCpy $TextoBoasVindas "A versão $VersaoInstalada será atualizada para a ${VERSAO}.$\r$\n$\r$\n$3"
  ${EndIf}
FunctionEnd

Function PularPastaSeAtualizando
  ${If} $Atualizando == "1"
    Abort
  ${EndIf}
FunctionEnd

; O .exe aberto fica travado e não pode ser sobrescrito nem apagado. O PyInstaller
; abre dois processos com o mesmo nome, por isso o taskkill usa /T.
!macro FUNCAO_FECHAR_APP_ABERTO PREFIXO
Function ${PREFIXO}FecharAppAberto
  nsExec::ExecToStack '"$SYSDIR\cmd.exe" /c tasklist /FI "IMAGENAME eq ${NOME_EXE}" /NH | "$SYSDIR\find.exe" /I "${NOME_EXE}"'
  Pop $0 ; código de saída: 0 quando o processo foi encontrado
  Pop $1 ; texto da saída, não usado
  ${If} $0 == "0"
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "O RealTime Screen Translator está aberto e será fechado para continuar." /SD IDOK IDOK +2
    Abort
    nsExec::Exec '"$SYSDIR\taskkill.exe" /F /T /IM "${NOME_EXE}"'
    Pop $0
    Sleep 1500 ; dá tempo de o Windows liberar o arquivo
  ${EndIf}
FunctionEnd
!macroend
!insertmacro FUNCAO_FECHAR_APP_ABERTO ""
!insertmacro FUNCAO_FECHAR_APP_ABERTO "un."

; ----------------------------------------------------------------------------
; Seção Principal de Instalação
; ----------------------------------------------------------------------------
Section "Instalar Arquivos" SecPrincipal

Call FecharAppAberto

; Define a pasta de destino
SetOutPath "$INSTDIR"

; O app é uma pasta: o .exe e a _internal. Na atualização, a _internal antiga sai
; inteira, para não sobrar arquivo de uma versão anterior. A pasta gpu fica: o app
; confere sozinho se ela ainda serve para a versão nova.
RMDir /r "$INSTDIR\_internal"
File /r "dist\RealTimeScreenTranslator\*.*"

; Cria o desinstalador executável dentro da pasta do programa
WriteUninstaller "$INSTDIR\uninstall.exe"

; --------------------------------------------------------------------------
; Atalhos do Sistema
; --------------------------------------------------------------------------
; Atalho no Menu Iniciar
CreateDirectory "$SMPROGRAMS\RealTime Screen Translator"
CreateShortcut "$SMPROGRAMS\RealTime Screen Translator\RealTime Screen Translator.lnk" "$INSTDIR\RealTimeScreenTranslator.exe"
CreateShortcut "$SMPROGRAMS\RealTime Screen Translator\Desinstalar.lnk" "$INSTDIR\uninstall.exe"

; Atalho na Área de Trabalho do Usuário
CreateShortcut "$DESKTOP\RealTime Screen Translator.lnk" "$INSTDIR\RealTimeScreenTranslator.exe"

; --------------------------------------------------------------------------
; Registro do Windows (Para "Adicionar ou Remover Programas")
; --------------------------------------------------------------------------
WriteRegStr HKLM "${CHAVE_DESINSTALAR}" "DisplayName" "RealTime Screen Translator"
WriteRegStr HKLM "${CHAVE_DESINSTALAR}" "DisplayIcon" '"$INSTDIR\RealTimeScreenTranslator.exe"'
WriteRegStr HKLM "${CHAVE_DESINSTALAR}" "UninstallString" '"$INSTDIR\uninstall.exe"'
WriteRegStr HKLM "${CHAVE_DESINSTALAR}" "InstallLocation" "$INSTDIR"
WriteRegStr HKLM "${CHAVE_DESINSTALAR}" "DisplayVersion" "${VERSAO}"
WriteRegStr HKLM "${CHAVE_DESINSTALAR}" "Publisher" "Desenvolvimento Próprio"
WriteRegDWORD HKLM "${CHAVE_DESINSTALAR}" "NoModify" 1
WriteRegDWORD HKLM "${CHAVE_DESINSTALAR}" "NoRepair" 1

; --------------------------------------------------------------------------
; Aceleração por GPU (pacote baixado depois da instalação)
; --------------------------------------------------------------------------
; O PyTorch com CUDA passa de 2 GB, o limite do NSIS. Em PCs com placa NVIDIA, o
; próprio app abre a janela que baixa esse pacote (cerca de 2,5 GB) do site do
; PyTorch. Se ele já estiver instalado e na versão certa, a janela nem aparece.
; O Sysnative enxerga a System32 de 64 bits a partir deste instalador de 32 bits.
${IfNot} ${Silent}
${AndIf} ${FileExists} "$WINDIR\Sysnative\nvidia-smi.exe"
  DetailPrint "Placa NVIDIA encontrada: abrindo a janela da aceleração por GPU..."
  ExecWait '"$INSTDIR\${NOME_EXE}" --instalar-gpu'
${EndIf}
SectionEnd

; ----------------------------------------------------------------------------
; Seção de Desinstalação
; ----------------------------------------------------------------------------
Section "Uninstall"

Call un.FecharAppAberto

; Deleta o programa (o .exe, a pasta _internal e o pacote GPU) e o desinstalador
Delete "$INSTDIR\RealTimeScreenTranslator.exe"
RMDir /r "$INSTDIR\_internal"
RMDir /r "$INSTDIR\gpu"
RMDir /r "$INSTDIR\gpu.novo"
RMDir /r "$INSTDIR\gpu.download"
Delete "$INSTDIR\uninstall.exe"

; Remove os atalhos do Menu Iniciar
Delete "$SMPROGRAMS\RealTime Screen Translator\RealTime Screen Translator.lnk"
Delete "$SMPROGRAMS\RealTime Screen Translator\Desinstalar.lnk"
RMDir "$SMPROGRAMS\RealTime Screen Translator"

; Remove o atalho da Área de Trabalho
Delete "$DESKTOP\RealTime Screen Translator.lnk"

; Limpa a pasta principal (só remove se estiver vazia)
RMDir "$INSTDIR"

; Limpa as chaves criadas no Registro do Windows
DeleteRegKey HKLM "${CHAVE_DESINSTALAR}"

; As configurações e as chaves de API só são apagadas se a pessoa pedir. A
; atualização não passa por aqui, então nunca as apaga.
MessageBox MB_YESNO|MB_ICONQUESTION "Apagar também as configurações e as chaves de API salvas?$\r$\n$\r$\nEscolha Não para mantê-las caso instale o programa de novo." /SD IDNO IDNO +2
RMDir /r "$APPDATA\RealTimeScreenTranslator"

SectionEnd