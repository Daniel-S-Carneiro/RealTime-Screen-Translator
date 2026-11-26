# Referência da validação

*O que fica congelado durante a validação com jogos novos, como ela é medida e o que
reprovaria cada regra. Para a rodada 2, vale da tag `referencia-validacao-2026-11-26` até o
resultado da rodada estar escrito em `docs/resultados-validacao.md`. A rodada 1 foi medida
com a tag `referencia-validacao-2026-11-22`, e a referência dela continua no fim deste
arquivo. O passo a passo da coleta está no [plano de validação](plano-de-validacao.md).*

## O que está congelado (rodada 2)

A tag `referencia-validacao-2026-11-26` é o **ponto de congelamento da rodada 2**. Ela tem
tudo o que estava na tag de 22/11 e mais as nove correções da fase 4, feitas a partir dos
erros da rodada 1 (PRs #33 a #39, #41, #43 e #44; veja [Por que as linhas se
perderam](classificacao-linhas-perdidas.md)). Os gabaritos dos 150 prints foram relidos em
25/11, antes do congelamento.

Até a rodada 2 ser medida, **os módulos de leitura e montagem não mudam**:
`paragrafos.py`, `espacos.py`, `quantidades.py`, `releitura.py`, `ocr_engine.py`,
`pipeline_ocr.py` e `processador_texto.py`. São eles que o benchmark mede. O teste é este
comando, que precisa sair vazio:

```
git diff referencia-validacao-2026-11-26 -- paragrafos.py espacos.py quantidades.py releitura.py ocr_engine.py pipeline_ocr.py processador_texto.py
```

**Se alguma coisa falhar, volta para este ponto.** Este comando descarta as mudanças nesses
módulos e devolve os da tag:

```
git restore --source=referencia-validacao-2026-11-26 -- paragrafos.py espacos.py quantidades.py releitura.py ocr_engine.py pipeline_ocr.py processador_texto.py
```

**O resto do app pode mudar** (26/11, decisão do dono do projeto): a interface, os motores
de tradução, a captura e a configuração, para a primeira build. Cada build é medida no
benchmark antes de sair, e a que piorar as letras ou as linhas inteiras não sai. Até 26/11,
o congelamento valia para todo `.py` da raiz.

Também podem mudar: a régua (`benchmark/benchmark.py` só ganha medidas novas, sem mudar as que
existem), os testes, a documentação, as ferramentas em `ferramentas/` e os prints e
gabaritos da rodada 2. O gabarito da rodada 2 é escrito olhando só a imagem, sem abrir o
rascunho do app, pela regra de uma linha por parágrafo ou item.

Todo script criado ou editado passa pelo Pylint e pelo Pylance
([regra completa](verificacao-de-codigo.md)). **Um alerta num `.py` congelado é só
relatado.** Corrigir exige decisão do dono do projeto, novo ponto de congelamento e os 150
prints idênticos.

No ponto de congelamento: 162 testes (5 deles falham de propósito, os limites conhecidos)
e nenhum alerta na verificação da base.

## A régua (rodada 2)

Os portões são os mesmos da rodada 1, como manda o plano. A referência por tipo de tela é
a dos 90 prints, agora com as regras e os gabaritos de 26/11. Os 50 prints da rodada 1
entram no ajuste desde 24/11: aparecem na tabela só como registro, não como prova.

Benchmarks do ponto de congelamento, fora do git: `benchmark_20261126_001157.csv` (90
prints), `_001251` (rodada 1) e `_001301` (espanhol). Para medir os 90 de novo:
`benchmark.py --configs producao --periodo base,2026-11-02..2026-11-15`. A rodada 2:
`--periodo segunda-validacao`.

| Medida | O que conta | Referência (90 prints) | Rodada 1, hoje ajuste (50 prints) | Portão da rodada 2 |
|---|---|---|---|---|
| **Letras sem ordem** (`cer_sem_ordem`) | Letras com as linhas lidas postas na ordem do gabarito: letra trocada, texto que falta e texto a mais contam, a ordem entre as linhas não | **97,4%** | 92,4% | **93% ou mais** |
| Letras (`cer`) | Letras na ordem em que o app leu | 95,9% | 91,4% | registrada, sem portão |
| Palavras (`wer`) | Palavras na ordem em que o app leu | 92,1% | 85,1% | registrada |
| **Linhas inteiras** | Linhas do gabarito com 2+ palavras que saem inteiras e sozinhas | **81,8%** (549 de 671) | 75,5% (219 de 290) | **75% ou mais** |
| Quebras achadas / certas | | 90,3% / 92,0% | 93,6% / 91,7% | registradas |
| Quebras a mais | | 60 | 28 | registradas |
| Tempo por print | Média e p95, de uma medida só | 1,1 s e 2,8 s | 1,0 s e 1,9 s | registrados |
| **Por tipo de tela** | Letras sem ordem e linhas inteiras de cada tipo | tabela abaixo | | **nenhum tipo mais de 5 pontos abaixo** do mesmo tipo nos 90 prints |

| Tipo de tela | Letras sem ordem | Letras | Linhas inteiras | Linhas inteiras em 22/11 |
|---|---|---|---|---|
| ficha | 95,3% | 90,8% | 80% (310 de 387) | 77% |
| legenda | 99,5% | 99,5% | 93% (25 de 27) | 81% |
| letreiro | 88,6% | 86,0% | 83% (19 de 23) | 78% |
| menu | 98,9% | 98,9% | 82% (37 de 45) | 80% |
| texto | 99,5% | 99,5% | 84% (158 de 189) | 92% |

**O texto caiu por causa da régua, não do app.** Os 11 tomos do Immortal Clan são do tipo
texto, e a releitura separou em 10 deles a etiqueta do elemento do selo do tipo ("Wood
Technique" e "Sword Art"). O app junta as duas, e o gabarito antigo também juntava. Sem
os tomos, o texto sobe: 87% (69 de 79), contra 85% (67 de 79) em 22/11.

O tempo subiu de 0,7 s para 1,1 s de média entre os dois benchmarks. É uma medida só, sem
repetição, e o benchmark não serve para comparar tempo de rodadas diferentes; o tempo é
registrado, sem portão.

**O portão vale para os jogos em inglês.** Um jogo em outra língua, se houver, fica numa
pasta própria e é medido à parte, sem passar nem reprovar.

## As regras

**Estado:** todas estão *integradas*, e o benchmark do ponto de congelamento roda todas
juntas. As da tag de 22/11 foram medidas nos 90 prints e reprovaram na rodada 1. As nove da
fase 4 foram medidas nos 90 prints e nos 60 da rodada 1 e do espanhol, com o RapidOCR do app
e com o EasyOCR. Nenhuma está *validada em jogo novo*; é isso que a rodada 2 vai dizer.

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
| **Fase 4:** passo grande (`_quebras_por_passo`) | `PASSO_GRANDE` 1,35, `PASSO_MESMA_FILEIRA` 0,5 | Os 140 prints, sem nenhuma perda nem quebra a mais | Geral | Frase cortada onde o jogo afasta mais as linhas de um mesmo parágrafo |
| **Fase 4:** palavra final da fala (`_continua_frase`) | `PALAVRA_FINAL` | 1 fala do Stardew | Especializada | Tópico de uma palavra, com ponto no fim, colado à linha de cima |
| **Fase 4:** linhas coladas (`_linhas_coladas`, problema 9) | `FIM_COLADO` 0,18, `FIM_FONTE` 1,4 | 5 jogos | Geral | Dois parágrafos sem respiro entre eles juntados |
| **Fase 4:** descrição centralizada (`_quebras_centralizadas`, problema 10) | `DESCRICAO_CHEIA` 0,82, `DESCRICAO_VAO` 0,45, `DESCRICAO_ESQUERDA` 0,5, `DESCRICAO_LARGA` 8 | Path of Exile, Stardew e cartazes | Geral; as travas foram escolhidas olhando os resultados | Propriedades de um item juntadas, ou uma frase centralizada partida |
| **Fase 4:** menu numa caixa só, pelas palavras (`_menu_pelas_palavras`, problema 11) | `ITENS_SALTO` 2,2, `ITENS_PISO` 0,15, `ITENS_REGULAR` 2, `ITENS_PALAVRAS` 4 | Butterfly Soup e abas do Katawa | **Especializada** | Frase com espaços largos partida em itens |
| **Fase 4:** espaço engolido (`espacos.py`, problema 12) | `CANDIDATO_PASSO` 1,15, `CANDIDATO_TINTA` 0,20, `MARGEM_MINIMA` −1 | 10 jogos | Geral; o limite −1 foi escolhido olhando os resultados | Palavra partida ao meio por um espaço inventado |
| **Fase 4:** duas caixas na mesma linha (`_pares_distantes`, `_itens_distantes`, problema 13) | `DISTANTES_VAO` 2,1, `DISTANTES_BORDA` 1, `DISTANTES_PASSO` 3, `DISTANTES_PARES` 0,5 | 6 jogos | Geral | Rótulo e valor separados |
| **Fase 4:** ícones colados (`_tirar_icones_colados`, problema 14) | `ICONES_NA_COLUNA` 3, `ICONE_COLADO` 0,8, `ICONE_BAIXO` 0,75, `ICONE_LONGE` 2,1 | 6 jogos | Geral | Símbolo ou dígito que é texto apagado (um "+" de verdade, um "1" de quantidade) |
| **Fase 4:** frases quebradas (`_frases_quebradas`, problema 15) | `LETREIRO_VAO` −0,15, `LETREIRO_LINHAS` 3 a 4, `ITEM_QUEBRADO_PASSO` 0,8, `CAUDA_PALAVRAS` 4 | 7 jogos; uma regra estreita por formato | Geral | Itens de menu ou de lista colados juntados como se fossem uma frase |

**Abas e barra de menu são provisórias.** Se o jogo novo não tiver o sinal (a aba
selecionada com fundo próprio, a barra com espaço maior que o da fala), a regra
simplesmente não dispara, e isso não a reprova. Se ela cortar errado, a decisão é
estreitar ou desligar, nunca reajustar os 25 níveis ou o 1,5 em cima da validação. O
mesmo vale para o menu pelas palavras.

**Limites conhecidos**, registrados como testes que falham de propósito: prosa alemã curta
com 3 números, menu de só 2 itens, fala japonesa estreita, itens de largura parecida e
itens com minúscula no mesmo passo de uma frase. Se um desses testes passar a funcionar sem
um print novo que o exija, a suíte deixou de medir o que devia.

**Sem regra, por serem de um jogo só:** a grade de atributos do Disco Elysium e a etiqueta
com o selo dos tomos do Immortal Clan, na mesma linha. O título estilizado em duas linhas
deslocadas também ficou sem regra: o único caso nos 150 prints era um gabarito errado.

## Depois da validação

1. O resultado vai para `docs/resultados-validacao.md`, uma vez, com as medidas da tabela
   acima.
2. Cada erro novo é classificado em leitura, sobra, partida ou ordem. Erro que aparece
   num jogo só não vira regra.
3. A partir daí, os prints da rodada passam a ser conjunto de ajuste. Depois da rodada 1,
   a prova passou a ser a rodada 2. Depois da rodada 2, a próxima prova precisa de jogos
   que nenhuma correção viu.
4. Reorganizar o código (dividir o `paragrafos.py`, por exemplo) só depois, sem mudar
   constante nenhuma e com o benchmark idêntico ao da tag, print a print.

## A referência da rodada 1 (tag de 22/11)

A rodada 1 foi medida em 24/11 com a tag `referencia-validacao-2026-11-22` e não passou
([resultado](resultados-validacao.md)). Essa tag tem as regras de 19/11 (tag
`referencia-validacao-2026-11-19`) mais a correção da troca de língua e os ajustes de
anotação pedidos pelo Pylance, de 22/11. Nenhum resultado mudou: o benchmark dos 90 prints
saiu igual ao de 19/11, print a print.

A referência era a dos 90 prints com o RapidOCR (`benchmark_20261122_111940.csv`, fora do
git), com os gabaritos de antes da releitura:

| Medida | Referência (90 prints) | Portão da rodada 1 |
|---|---|---|
| **Letras sem ordem** | **97,0%** | **93% ou mais** |
| Letras | 95,8% | registrada, sem portão |
| Palavras | 91,4% | registrada |
| **Linhas inteiras** | **81,5%** (539 de 661) | **75% ou mais** |
| Quebras achadas / certas | 91,9% / 90,8% | registradas |
| Quebras a mais | 69 | registradas |
| Tempo por print | 0,8 s e 2,5 s | registrados |
| **Por tipo de tela** | tabela abaixo | **nenhum tipo mais de 5 pontos abaixo** do mesmo tipo aqui |

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
