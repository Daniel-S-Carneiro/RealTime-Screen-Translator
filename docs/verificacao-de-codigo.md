# Verificação de código: Pylint e Pylance

*A regra do projeto para conferir cada script criado ou editado, e o erro real que levou a
ela. Adotada em 23/11/2026, durante a coleta de prints da validação.*

## A regra

**Depois de cada criação ou edição de um script do projeto, rodar o Pylint e o Pylance.**
O alvo é zero alertas sem explicação. Cada alerta é classificado antes de qualquer mudança:

| O alerta é | O que fazer |
|---|---|
| Defeito real | Corrigir e, quando der, criar um teste que reproduza o defeito |
| Alarme falso | Ajustar a anotação sem mudar o comportamento. Evitar desligar o aviso |
| Em `.py` congelado | Só relatar. Mudar exige decisão do dono do projeto, novo ponto de congelamento e os 90 prints idênticos |

Valem para a regra os arquivos `.py` da raiz, `tests/`, `benchmark/` e `ferramentas/`.
**`laboratorios/` fica de fora**: são scripts de medição, fora do app e do git, e polir aviso
ali não melhora nenhum resultado.

## O erro que o Pylance achou

Em 22/11, o Pylance do VS Code marcou esta linha do `ocr_engine.py`:

```
"readtext" não é um atributo conhecido de "None"
```

**A causa.** A troca de língua gravava a língua nova antes de carregar o motor:

```python
def alterar_idioma(self, novo_idioma):
    if novo_idioma in self.idiomas_atuais:
        return
    self.idiomas_atuais = [novo_idioma]  # gravada antes de saber se o motor carrega
    self._carregar()
```

Línguas como russo, árabe e coreano usam o EasyOCR, que baixa o modelo na primeira vez. Sem
internet, o carregamento falhava, e o app ficava marcado com a língua nova e sem motor
nenhum.

**O efeito, reproduzido com uma falha simulada.** Toda leitura mostrava
`Erro: 'NoneType' object has no attribute 'readtext'`. Salvar a mesma língua de novo não
resolvia, porque o app achava que já estava nela. Só trocar de língua ou reabrir o app
tirava dali. Inglês, japonês e espanhol não eram afetados, porque usam o RapidOCR.

**Por que ninguém tinha visto.** O Pylint não acusou, os testes não passavam por uma falha
de carregamento e o benchmark só mede leituras em que o motor carregou. O defeito ficava
num caminho que nenhuma medida percorria.

**A correção** (PR #28, commit `4b6601c`). Se o carregamento falha, a língua e o motor
anteriores voltam, e a tela de configuração avisa que a língua não carregou:

```python
def alterar_idioma(self, novo_idioma):
    if novo_idioma in self.idiomas_atuais:
        return
    anteriores, nome_anterior = self.idiomas_atuais, self.nome
    self.idiomas_atuais = [novo_idioma]
    try:
        self._carregar()
    except Exception:
        self.idiomas_atuais, self.nome = anteriores, nome_anterior
        raise
```

Entraram 4 testes novos (`tests/test_troca_de_lingua.py`), e o benchmark dos 90 prints saiu
idêntico, print a print. Esse ponto virou a tag `referencia-validacao-2026-11-22`, o
congelamento atual.

## Quanto o Pylance acerta

Na primeira passada, ele deu 32 alertas no app e nos testes. **Um era defeito real e
alcançável.**

| Alertas | O que eram |
|---:|---|
| 1 | **Defeito real e alcançável**: o da troca de língua |
| 1 | Real, mas inalcançável hoje: caminho de imagem inexistente, que ninguém chama |
| 2 | Mesmo padrão do defeito, sem efeito na prática |
| 17 | Falsos: tipos da saída do RapidOCR, que a biblioteca declara de forma ampla |
| 6 | Falsos: casos que o analisador não acompanha (`paragrafos.py`, `tela_carregamento.py`) |
| 5 | Falsos: o import de `tests/test_benchmark.py`, por causa do `sys.path.insert` |
| **32** | |

A maioria é ruído, e a regra precisa contar com isso. Ainda assim, vale: resolver os falsos
foi feito uma vez, sem mudar o comportamento, e agora a base está em **zero alertas**. Com a
base limpa, qualquer alerta novo aponta para a edição que acabou de ser feita.

## Como a regra roda

O Pylance só funciona dentro do VS Code. Fora dele, a verificação usa o **Pyright**, o motor
de análise do Pylance, no modo `standard`, o mesmo configurado no VS Code. O script
[`ferramentas/verificar_codigo.py`](../ferramentas/verificar_codigo.py) roda os dois.

**Automática, em toda edição feita pelo Claude Code.** Um gancho em `.claude/settings.json`
confere o arquivo editado, em 3 a 6 segundos. Se houver alerta, ele volta na hora para ser
tratado. Se a ferramenta não rodar, isso também é avisado: falta de verificação não passa
como "sem erros".

**Manual, na base inteira, antes de cada commit** (cerca de 1min30):

```
env\Scripts\python.exe ferramentas\verificar_codigo.py
```

Resultado esperado: `0 alerta(s)`.

**Instalação em outra máquina.** O Pyright fica fora do git, em `ferramentas/node_modules/`,
com a versão fixada em `ferramentas/package.json` (1.1.414). Precisa do Node.js e baixa cerca
de 20 MB:

```
npm ci --prefix ferramentas
```

O Pyright não entra no `requirements.txt` nem no instalador do app.

## O que a regra não cobre

- **Lógica errada.** Um analisador de tipos não sabe se uma regra de quebra de linha está
  certa. Isso continua com os testes e o benchmark.
- **Quem chama o arquivo editado.** O gancho olha só o arquivo mexido. Renomear uma função
  pode quebrar outro arquivo, e é por isso que a base inteira roda antes do commit.
- **Edições feitas por comando.** O gancho dispara nas ferramentas de edição do Claude Code,
  não em script que altera arquivo. A passada antes do commit cobre esse caso.
- **Edições feitas à mão.** Nessas, o aviso aparece no próprio VS Code.

## Dois avisos conhecidos

- `gerenciador_idiomas.py:71`, `E1137`: alarme falso do Pylint. `self.checkboxes` é um
  dicionário, e a anotação confunde a ferramenta. O arquivo está congelado, então o alerta
  fica registrado em `ALARMES_FALSOS` no script. Depois da validação, dá para resolver na
  própria linha e tirar de lá.
- `duplicate-code` fica desligado na verificação. Ele só aponta um trecho auxiliar parecido
  em dois arquivos de teste, sem efeito no app.
