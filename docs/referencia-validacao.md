# Referência da validação

*O que fica congelado durante a validação com jogos novos, como ela é medida e o que
reprovaria cada regra. Vale da tag `referencia-validacao-2026-11-22` até o resultado da
validação estar escrito em `docs/resultados-validacao.md`. O passo a passo da coleta está
no [plano de validação](plano-de-validacao.md).*

## O que está congelado

A tag `referencia-validacao-2026-11-22` é o **ponto de congelamento**. Ela tem as regras de 19/11
(tag `referencia-validacao-2026-11-19`) mais a correção da troca de língua e os ajustes de
anotação pedidos pelo Pylance, de 22/11. Nenhum resultado mudou: o benchmark dos 90 prints
saiu igual ao de 19/11, print a print.

Até a validação ser medida, **nenhum arquivo `.py` da raiz do projeto muda**. O teste é
este comando, que precisa sair vazio:

```
git diff referencia-validacao-2026-11-22 -- ":(glob)*.py"
```

**Se alguma coisa falhar, volta para este ponto.** Este comando descarta as mudanças nos
arquivos `.py` da raiz e devolve os da tag:

```
git restore --source=referencia-validacao-2026-11-22 -- ":(glob)*.py"
```

Podem mudar: a régua (`benchmark/benchmark.py` só ganha medidas novas, sem mudar as que
existem), os testes, a documentação, as ferramentas em `ferramentas/` e os prints e
gabaritos da validação.

Todo script criado ou editado passa pelo Pylint e pelo Pylance
([regra completa](verificacao-de-codigo.md)). **Um alerta num `.py` congelado é só
relatado.** Corrigir exige decisão do dono do projeto, novo ponto de congelamento e os 90
prints idênticos, como foi feito na correção da troca de língua.

## A régua

Medidas nos 90 prints da referência, com o RapidOCR (benchmark do ponto de congelamento,
`relatorios/benchmark/benchmark_20261122_111940.csv`, fora do git). Para medir só esses
90 de novo: `benchmark.py --configs producao --periodo base,2026-11-02..2026-11-15`.

| Medida | O que conta | Referência (90 prints) | Portão da validação |
|---|---|---|---|
| **Letras sem ordem** (`cer_sem_ordem`) | Letras com as linhas lidas postas na ordem do gabarito: letra trocada, texto que falta e texto a mais contam, a ordem entre as linhas não | **97,0%** | **93% ou mais** |
| Letras (`cer`) | Letras na ordem em que o app leu | 95,8% | registrada, sem portão |
| Palavras (`wer`) | Palavras na ordem em que o app leu | 91,4% | registrada |
| **Linhas inteiras** | Linhas do gabarito com 2+ palavras que saem inteiras e sozinhas | **81,5%** (539 de 661) | **75% ou mais** |
| Quebras achadas / certas | | 91,9% / 90,8% | registradas |
| Quebras a mais | | 69 | registradas |
| Tempo por print | Média e p95 | 0,8 s e 2,5 s | registrados |
| **Por tipo de tela** | Letras sem ordem e linhas inteiras de cada tipo | tabela abaixo | **nenhum tipo mais de 5 pontos abaixo** do mesmo tipo aqui |

| Tipo de tela | Letras sem ordem | Letras | Linhas inteiras |
|---|---|---|---|
| ficha | 95,2% | 90,5% | 77% |
| legenda | 99,4% | 99,4% | 81% |
| letreiro | 85,9% | 85,9% | 78% |
| menu | 98,8% | 98,8% | 80% |
| texto | 99,5% | 99,5% | 92% |

**O portão vale para os jogos em inglês** (`--periodo validacao`). O jogo em japonês ou
espanhol fica numa pasta própria (`--periodo outra-lingua --idioma ja` ou `es`) e é medido
à parte, sem passar nem reprovar: é a primeira medida do app fora do inglês e não tem
referência nos 90 prints. Uma leitura mais fraca do japonês não diz nada sobre as regras
de montagem terem decorado o dataset.

**A validação tem duas rodadas.** O portão acima é o da rodada 1: Katawa Shoujo, Butterfly
Soup, Disco Elysium, Path of Exile e The Big Con (no lugar do Firewatch, que quase não tem
placas). Os outros 8 jogos da lista do [plano de
validação](plano-de-validacao.md) formam a rodada 2 (`--periodo segunda-validacao`), que
fica guardada para provar as correções e é medida uma vez, com o ponto de congelamento que
existir depois delas.

**Por que o portão de letras usa a medida sem ordem.** Uma tela com dois painéis pode ter
duas ordens de leitura certas. No resumo de personagem do Caves of Qud, as duas ordens
fazem sentido, e mesmo assim a medida de sempre dá 65% de erro. Na validação, um painel
lido na outra ordem pareceria uma regra que decorou o dataset. A troca foi decidida em
19/11, antes da coleta, a partir das avaliações do ChatGPT e do Grok. Nos 90 prints, só 4
mudam, todos fichas com dois painéis: resumo do Caves of Qud (65% → 11% de erro),
perícias do EVE (39% → 7%), reputação do Caves of Qud (35% → 21%) e Pip-Boy (23% → 11%).
Legendas, menus, texto e letreiros ficam iguais.

## As regras

**Estado:** todas estão *medidas nos 90 prints* e *integradas* (o benchmark de 19/11 roda
todas juntas). Nenhuma está *validada em jogo novo*; é isso que a validação vai dizer.

**Geral** quer dizer medida em vários jogos. **Especializada** quer dizer que a evidência
vem de um jogo ou dois e o sinal pode não existir em outros.

| Regra (onde) | Constantes principais | Evidência | Tipo | O que a reprovaria num jogo novo |
|---|---|---|---|---|
| Blocos e colunas estreitas (`paragrafos._blocos`, `_parece_coluna`) | `VAO_BLOCO_*`, `VAO_COLUNA_ESTREITA` 0,2, `APOIO_COLUNA` 3, `DIFERENCA_TIPOS` 0,8 | Fichas e grades de vários jogos | Geral | Frase cortada por uma coluna falsa; tabela de registros lida coluna por coluna |
| Itens lado a lado (`_separar_itens`) | `VAO_ITENS` 0,8, `PALAVRAS_ITEM` 3 | Menus e abas de vários jogos | Geral | Fala em maiúsculas partida palavra a palavra |
| Quebras entre linhas (`_comeca_paragrafo`) | `VAO_PARAGRAFO` 0,8, `TITULO_PALAVRAS` 5 | Os 90 prints | Geral | Frase cortada depois de uma linha que parece título |
| Margem do painel (`_margem_local`) | `LINHA_LONGA` 16, `FOLGA_PRINT` 4 | 4 prints, todos para melhor | Geral (critério local) | Frase de painel estreito cortada; linhas de tabela juntadas |
| Listas de rótulo e valor (`_quebras_de_lista`) | `CAMPO_LARGURA` 16, `CAMPOS_SEGUIDOS` 3 | 2 prints, de 2 jogos | Geral | Prosa curta terminada em número partida (o caso alemão já é limite conhecido) |
| Abas pelo fundo (`_abas_pelo_fundo`) | `ABA_FUNDO` 25, `ABAS_FUNDO_IGUAL` 8 | 3 barras do EVE | **Especializada, provisória** | Cabeçalho de tabela ou fileira de botões separada à toa |
| Barra de menu numa caixa (`_barra_de_menu`) | `BARRA_ESPACO` 1,5, `BARRA_PALAVRAS` 6 | 2 barras do Doki Doki | **Especializada, provisória** | Fala ou título de 6+ palavras partido palavra a palavra |
| Menu vertical (`_quebras_de_menu`) | `MENU_VAO` 0,8, `MENU_CURTA` 0,85, `MENU_PALAVRAS` 5 | Menus simulados, Caves of Qud, Morrowind | Geral | Fala estreita partida linha a linha |
| Itens em duas linhas (`_itens_quebrados`) | `TOPICO_SOBREPOSICAO` 0,1, `TOPICO_PASSO` 0,85, `TOPICO_PASSO_FRACO` 0,75 | 1 lista do Morrowind; o Pip-Boy no EasyOCR | Especializada (o modo fraco é geral) | Duas linhas de uma frase juntadas ou partidas por causa de caixas coladas |
| Segunda leitura das caixas pequenas (`releitura.py`) | menos de 32 px e 0,6 da altura típica, até 8 por print, 0,85 | Os 90 prints, sobretudo os letreiros | Geral | Texto pequeno de verdade descartado (palavra faltando numa ficha ou num HUD) |
| Quantidades (`quantidades.completar_quantidades`) | coluna de 2+ números, até 8 releituras, confiança 0,7 | Inventário do Persona, ficha do Morrowind | Especializada | Número inventado numa linha; quantidade à esquerda não é coberta |
| Ícones (`quantidades.tirar_icones`) | coluna de glifos misturados, glifo solto fora de 0,6-1,5 altura | 5 ícones do EVE | Especializada | Letra ou número de verdade apagado |
| Correções do inglês (`processador_texto.py`) | só com a língua "en" | Os 90 prints | Geral, só inglês | Termo de jogo trocado por palavra comum |

**Abas e barra de menu são provisórias.** Se o jogo novo não tiver o sinal (a aba
selecionada com fundo próprio, a barra com espaço maior que o da fala), a regra
simplesmente não dispara, e isso não a reprova. Se ela cortar errado, a decisão é
estreitar ou desligar, nunca reajustar os 25 níveis ou o 1,5 em cima da validação.

**Limites conhecidos**, registrados como testes que falham de propósito: prosa alemã curta
com 3 números, menu de só 2 itens, fala japonesa estreita, itens de largura parecida e
itens com minúscula no mesmo passo de uma frase. Se um desses testes passar a funcionar sem
um print novo que o exija, a suíte deixou de medir o que devia.

## Depois da validação

1. O resultado vai para `docs/resultados-validacao.md`, uma vez, com as medidas da tabela
   acima.
2. Cada erro novo é classificado em leitura, sobra, partida ou ordem. Erro que aparece
   num jogo só não vira regra.
3. A partir daí, os prints da rodada 1 passam a ser conjunto de ajuste. A próxima prova é
   a rodada 2, com jogos que nenhuma correção viu.
4. Reorganizar o código (dividir o `paragrafos.py`, por exemplo) só depois, sem mudar
   constante nenhuma e com o benchmark idêntico ao da tag, print a print.
