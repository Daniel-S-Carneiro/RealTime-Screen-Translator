; ============================================================================
; SCRIPT DE INSTALAÇÃO NSIS - REALTIME SCREEN TRANSLATOR
; Licença: GNU General Public License v3.0 (GPLv3)
; ============================================================================

!include "MUI2.nsh"

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

; ----------------------------------------------------------------------------
; Configurações da Interface Visual (Modern UI)
; ----------------------------------------------------------------------------
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Bem-vindo ao instalador do RealTime Screen Translator"
!define MUI_WELCOMEPAGE_TEXT "Este assistente guiará você na instalação do RealTime Screen Translator no seu computador.\r\n\r\nClique em Avançar para continuar."

; Opção para rodar o programa automaticamente na tela final de conclusão
!define MUI_FINISHPAGE_RUN "$INSTDIR\RealTimeScreenTranslator.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Executar RealTime Screen Translator agora"

; ----------------------------------------------------------------------------
; Páginas do Instalador (Inseridas apenas uma vez)
; ----------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
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
; Seção Principal de Instalação
; ----------------------------------------------------------------------------
Section "Instalar Arquivos" SecPrincipal

; Define a pasta de destino
SetOutPath "$INSTDIR"

; Copia o executável usando caminho relativo à pasta do projeto
File "dist\RealTimeScreenTranslator.exe"

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
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator" "DisplayName" "RealTime Screen Translator"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator" "UninstallString" '"$INSTDIR\uninstall.exe"'
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator" "DisplayVersion" "1.0.0"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator" "Publisher" "Desenvolvimento Próprio"
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator" "NoRepair" 1
SectionEnd

; ----------------------------------------------------------------------------
; Seção de Desinstalação
; ----------------------------------------------------------------------------
Section "Uninstall"

; Deleta o executável e o próprio desinstalador
Delete "$INSTDIR\RealTimeScreenTranslator.exe"
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
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RealTimeScreenTranslator"

SectionEnd