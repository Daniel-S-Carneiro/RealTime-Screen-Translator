# Problemas em aberto na montagem e na leitura do texto

*Escrito em 17/11/2026 para quem for pesquisar soluções, pessoa ou modelo de IA. Cada
problema traz os dados reais, o que já foi tentado e como medir uma solução. Os próximos
passos estão no [plano de validação](plano-de-validacao.md), e a história completa, no
[estudo de caso](estudo-de-caso-ocr.md).*

## 1. Contexto para quem não conhece o projeto

O RealTime Screen Translator tira um print da área embaixo de uma janela transparente,
lê o texto com OCR, monta os parágrafos e manda cada parágrafo para um tradutor (Google,
DeepL, Azure, Google Cloud ou Argos offline). O alvo é texto de jogo: legendas, menus,
fichas de personagem, inventários, letreiros.

### O caminho do texto

| Etapa | O que faz hoje | Arquivo |
|---|---|---|
| Captura | `mss` tira o print da área | `janela_overlay.py` |
| Imagem | Só converte para tons de cinza | `capturador.py` |
| OCR | RapidOCR com os modelos PP-OCRv6 small do PaddleOCR, no ONNX Runtime, na CPU. O detector lê o print no tamanho original (`limit_type=max`, até 2016 px). Caixas com confiança abaixo de 0,7 são descartadas. Em língua latina, caracteres chineses lidos em ícones são apagados. Escritas que o modelo não lê (cirílico, árabe, coreano, devanágari, tailandês…) vão para o EasyOCR | `ocr_engine.py` |
| Montagem | Transforma as caixas em parágrafos: linhas, blocos, colunas, itens e quebras | `paragrafos.py` |
| Correção | Separa palavras grudadas; só em inglês, corrige letras confundidas e apóstrofos | `processador_texto.py` |
| Tradução | Um parágrafo por item enviado ao tradutor | `motores_traducao.py` |

### O formato da saída do OCR

Uma lista de caixas, cada uma `(4 cantos [[x, y], ...], texto, confiança)`. O RapidOCR
agrupa as palavras de uma linha numa caixa só; ele só separa caixas na mesma linha
quando há um espaço visual grande. Exemplo real, a tela de subida de nível do Morrowind
(x inicial e final de cada caixa, por linha):

```
y 333: [139-270] "x3 Strength 72"    [336-440] "x2 Speed 62"
y 353: [172-287] "Intelligence 42"   [370-472] "Endurance 41"
y 375: [152-277] "x2 Willpower 40"   [368-478] "Personality 30"
y 392: [171-254] "Agility 75"        [369-437] "Luck 40"
```

### As regras de montagem que existem hoje

Todas as medidas são proporções da altura típica da letra, para valer em qualquer
resolução.

| Regra | O que faz | Constantes |
|---|---|---|
| Linhas | Caixas com o centro a menos de meia altura do centro médio da linha formam uma linha | — |
| Filtro de desenho | Caixa 3 vezes mais alta que o texto típico e com até 3 letras é desenho | `LIXO_ALTURA = 3.0` |
| Endireitar | Gira o texto pela inclinação mediana | `INCLINACAO_MINIMA = 0.05` |
| Blocos (corte XY) | Faixas vazias horizontais (1 altura) e verticais (3 alturas) separam blocos | `VAO_BLOCO_*` |
| Colunas estreitas | Faixa vertical a partir de 0,2 altura separa colunas se 3 linhas ou mais têm texto dos dois lados. Não vale se a direita continua a frase ou se os lados são campos de um registro | `VAO_COLUNA_ESTREITA`, `APOIO_COLUNA`, `DIFERENCA_TIPOS` |
| Título atravessando | Linha de uma caixa que cruza a faixa de colunas vira um bloco | — |
| Rótulo e valor | "Strength ..... 65" fica junto; coluna de valores é tabela, não painel | `FRACAO_VALORES` |
| Itens lado a lado | Fila de 3+ itens curtos, duas caixas em maiúsculas, abas com palavra em comum, HUD alternando rótulo e valor, par de itens isolado | `VAO_ITENS`, `MINIMO_ITENS`, `PALAVRAS_ITEM` |
| Quebra de parágrafo | Vão vertical maior que 0,8 altura; a 1ª palavra de baixo "caberia" na linha de cima (até a margem do painel, achada pelas linhas longas vizinhas com a mesma esquerda, ou até a do print); outra fonte; recuo; item solto; marcador; menu de uma palavra por linha; sentença terminada; título seguido de minúscula | `VAO_PARAGRAFO`, `RECUO`, `FONTE`… |
| Continuação | Linha que começa com minúscula continua a frase de cima | — |
| Línguas | Árabe, persa, urdu e uigur são espelhados; chinês, japonês e tailandês juntam sem espaço | — |

### Como uma solução é medida

- **Dataset:** 90 prints com gabarito, de 11 jogos e 3 exemplos públicos. Os prints de
  jogo não estão no repositório, porque são telas de terceiros.
- **Métricas:**
  - acerto de letras (100 − CER) e de palavras (100 − WER);
  - quebras achadas e certas;
  - **linhas inteiras**: das linhas do gabarito com 2+ palavras, quantas saem inteiras e
    sozinhas, prontas para o tradutor.

  Tudo é medido também por tipo de tela (legenda, texto, menu, ficha, letreiro).
- **Teste diferencial:** `laboratorios/quebras/testar_regras.py --comparar main` aplica a
  regra sobre as caixas guardadas dos 90 prints (leituras do RapidOCR e do EasyOCR) e
  compara com a versão atual, print a print, em segundos.
- **Testes automáticos:** 29 casos simulados em várias línguas e 10 testes de abas com telas desenhadas (`tests/`). Uma regra nova
  não pode quebrá-los.
- **Critério de entrada:** melhora a média, não piora a maioria dos prints e não estraga
  outra língua.

### Restrições de qualquer solução

- Windows 10/11, Python 3.12, **sem GPU obrigatória**: a placa de testes é uma GeForce
  MX350 de 2 GB, e o app roda na CPU.
- Tempo: hoje cerca de **1 s por print**, da imagem ao texto. Uma solução não deve somar
  mais que algumas centenas de milissegundos.
- Instalador: 413 MB hoje. Evitar somar mais que algumas dezenas de MB.
- Licença do projeto: **GPLv3**. Bibliotecas Apache, MIT, BSD ou LGPL servem.
- Offline: a leitura não pode depender de serviço na internet.
- **83 línguas**: nada pode depender de vocabulário de uma língua só, a não ser que fique
  restrito a ela (como as correções do inglês).
- Nada específico de um jogo: listas de palavras de um jogo, posições fixas de tela.

## 2. Os números de hoje

| Medida | Resultado |
|---|---|
| Acerto de letras | 95,1% |
| Acerto de palavras | 91,1% |
| Quebras achadas / certas | 90% / 89% (670 de 744 achadas, 79 a mais) |
| Linhas inteiras | 80% (529 de 661) |
| Das que não chegam inteiras | 42 com sobra (quebra perdida), 25 partidas, 65 com palavra faltando |

| Tipo de tela | Prints | Acerto de letras | Linhas inteiras | Quebras a mais |
|---|---|---|---|---|
| texto | 28 | 99,5% | 92% | 3 |
| legenda | 21 | 99,4% | 81% | 1 |
| menu | 9 | 98,8% | 80% | 1 |
| ficha | 24 | 90,3% | 75% | 63 |
| letreiro | 8 | 79,4% | 74% | 11 |

Os 10 prints que mais perdem linhas inteiras são todos fichas e somam 57% das perdas.

## 3. Os problemas, do maior para o menor

### Problema 1: parágrafos em colunas estreitas cortados ao meio (resolvido)

**Resolvido em 17/11/2026.** A margem do "caberia" passou a ser a do painel quando há
evidência dele: até 2 linhas acima e abaixo que começam no mesmo x (1 altura), com a
altura típica e 16 alturas de largura ou mais. A margem é o fim da mais longa delas mais
uma altura, e só vale se ficar 4 alturas ou mais para dentro do print. Sem isso, fica a
margem do print. A ideia veio da resposta do ChatGPT; foram medidas as propostas de
quatro IAs:

| Proposta | Quebras certas (RapidOCR) | Quebras a mais | Linhas inteiras | Por que ganhou ou perdeu |
|---|---|---|---|---|
| Antes | 662 | 85 | 519 | — |
| **ChatGPT** (linhas longas vizinhas) | **662** | **79** | **524** | Só 4 prints mudaram, todos para melhor |
| Grok (fim repetido por 2 linhas longas) | 658 | 79 | 520 | Sem a folga até o print, juntou 4 linhas da tabela do overview do EVE |
| Gemini (mediana das linhas que continuam) | 637 | 76 | 504 | Margem única para o bloco: estragou fichas e menus |
| Copilot (percentil 80 do bloco) | 634 | 78 | 496 | É a margem por bloco já descartada; estragou fichas |

Corrigiu os dois exemplos abaixo, "mutated / human." no genótipo do Qud e duas frases
da reputação do Qud. O tamanho estimado estava errado: eram 6 quebras a mais, não "a
maior parte" das 69 das fichas. O teste está em `laboratorios/quebras/experimentos/margens.py`.
O texto abaixo fica como registro do problema.

**Tipo:** montagem. **Tamanho:** a maior parte das quebras a mais das fichas. **Prints:**
diálogo do Morrowind, tutorial e criação de personagem do Caves of Qud, reputação do Caves
of Qud.

**O que acontece.** A regra "a primeira palavra de baixo caberia na linha de cima" mede o
espaço até a **margem direita do print inteiro**. Depois que o app separa as colunas, um
parágrafo pode ficar num painel estreito. Ali sempre "cabe" mais uma palavra até a margem
do print, e o app quebra frases ao meio.

**Exemplo real (diálogo do Morrowind).** O texto do diálogo ocupa x = 28 a 1137, e a lista
de tópicos, à direita, x = 1170 a 1319. A margem usada é 1319:

```
y 374: [ 32-1114] "The Guild of Mages only accepts ... the great schools of magic:"
y 390: [ 31-1068] "Destruction, Alteration, Illusion, and Mysticism. ..."
```

A linha de cima termina em 1114, e até 1319 cabem uns 20 caracteres, então
"Destruction," "caberia" e o app quebra. Com a margem do painel (cerca de 1137), não
quebraria. O mesmo acontece em "...knowledge freely with other" / "Guild members.".

**Exemplo real (tutorial do Caves of Qud).** O texto ocupa x = 123 a 516; a margem do
print é 1108:

```
y 202: [125-506] "(The recommended way! Once you get your"
y 221: [124-217] "footing.)"
```

**O que já foi tentado:**
- margem do bloco para todas as linhas: perdeu 38 quebras certas, porque menus curtos
  dentro de um bloco estreito passam a se juntar;
- margem do bloco só quando a linha de cima tem 4 palavras ou mais: perdeu 6 quebras
  certas e tirou 8 erradas; não compensou.

**O que pesquisar.** Como estimar a largura do "contêiner" de um parágrafo (a coluna de
texto) a partir das próprias linhas:
- a borda direita mais comum das linhas longas com a mesma borda esquerda;
- um percentil das bordas direitas;
- a detecção de texto justificado ou alinhado à esquerda.

Em documentos isso se chama análise de layout ou segmentação de colunas de texto
(*text column detection*, *paragraph reconstruction*, *line wrap detection*).

**Como medir.** Quebras a mais nas fichas (69 hoje) e linhas "partidas" (30 hoje), sem
aumentar as "com sobra" (47) nos menus.

### Problema 2: listas de "rótulo valor" que saem numa linha só (resolvido)

**Resolvido em 17/11/2026.** Uma linha é um campo quando tem menos de 16 alturas de
largura, até 8 palavras e termina num valor ("41", "0.0", "16:29", "0.0 ?") ou tem ":" com
letra logo antes ("Total Net Worth:"). Três campos ou mais seguidos, empilhados na mesma
coluna (vão de até 0,8 altura e sobreposição de 0,4 da largura do mais curto), viram uma
linha cada, menos antes de uma linha que começa com minúscula. A ideia veio da resposta do
Grok; foram medidas as propostas de quatro IAs:

| Proposta | Quebras certas (RapidOCR) | Quebras a mais | Linhas inteiras | Por que ganhou ou perdeu |
|---|---|---|---|---|
| Antes | 662 | 79 | 524 | — |
| **Grok** (3+ campos curtos empilhados, guarda da minúscula) | **666** | **79** | **529** | Só os 2 prints do problema mudaram; igual de 10h a 24h e de 2 a 4 linhas |
| ChatGPT (janela de 3-4 linhas com passo regular) | 666 | 80 | 528 | Sem a guarda da minúscula, cortou uma frase do registro do Qud |
| Copilot (grupo alinhado, 60% com número ou ":") | 665 | 80 | 526 | Idem; e só separou parte do perfil do EVE |
| Gemini (par de linhas com "valor" no fim) | 666 | 91 | 519 | Contava "." e "," como valor e não exigia repetição: 12 quebras erradas |
| Copilot, só geometria (mesmo x, larguras parecidas) | 667 | 198 | 494 | Todo parágrafo alinhado à esquerda vira lista |

Limite conhecido: três linhas curtas de prosa seguidas, todas terminando em número, com
maiúscula embaixo (comum em alemão), viram parágrafos separados. Está em
`tests/casos_paragrafos.py` como caso de limite. O teste está em
`laboratorios/quebras/experimentos/fichas.py`. O texto abaixo fica como registro do problema.

**Tipo:** montagem. **Prints:** subida de nível do Morrowind e perfil do EVE.

**O que acontece.** Numa coluna de atributos em que cada linha é uma caixa só
("Endurance 41"), nenhuma regra de quebra dispara: o vão entre as linhas é pequeno, a
linha de baixo começa com maiúscula, e a de cima não termina com ponto. Saída real:

```
app:      "Endurance 41 Personality 30 Luck 40"
gabarito: "Endurance 41" / "Personality 30" / "Luck 40"
```

O perfil do EVE tem o mesmo problema com rótulos de dois pontos: "Born: 2022.01.13 16:29"
/ "Total Net Worth:" / "Security Status: 0.0".

**Por que o "caberia" não dispara (medido em 17/11).** A lista fica encostada na borda
direita do print, e não sobra espaço para a primeira palavra de baixo. Na subida de nível
do Morrowind, a margem do print é 509 (o fim da linha mais longa):

```
y 333: [139-270] "x3 Strength 72"    [336-440] "x2 Speed 62"
y 353: [172-287] "Intelligence 42"   [370-472] "Endurance 41"
y 375: [152-277] "x2 Willpower 40"   [368-478] "Personality 30"
y 392: [171-254] "Agility 75"        [369-437] "Luck 40"
```

A coluna da esquerda sai certa, uma linha por atributo, porque até 509 sobra espaço. Na
da direita, "Endurance 41" termina em 472, e "Personality" precisa de cerca de 120 px;
sobram 37. No perfil do EVE, a lista é o texto mais largo do print (margem 278):

```
y  68: [84-246] "Born: 2022.01.13 16:29"
y  97: [87-202] "Total Net Worth:"
y 120: [85-247] "SecurityStatus: 0.0 ?"
y 147: [86-278] "Home Station: Kisogo 1.0 ?"
```

O app só quebra depois do "?" (sentença terminada). Linha terminada em ":" não é quebra
hoje, de propósito: "...the great schools of magic:" / "Destruction, ..." é a mesma frase.

**O que pesquisar.** Uma regra do tipo "a linha de cima termina com número e a de baixo
tem o mesmo formato (Rótulo número)". O cuidado é não quebrar texto corrido em que uma
linha termina com número ("...founded in 1990" / "and later..."). Ainda não foi medida.

**Como medir.** Linhas "com sobra" nas fichas, sem quebras novas nos tipos texto e legenda.

### Problema 3: abas de uma palavra encostadas (resolvido)

**Resolvido em 18/11/2026.** A aba selecionada tem fundo próprio. Numa fileira de 2 a 5
caixas de uma palavra encostadas (vão menor que 0,8 altura), sem palavra só minúscula nem
pontuação de frase, se uma caixa tem o tom de cinza mais comum *dentro* dela 25 níveis ou
mais diferente das outras, e as outras têm o mesmo tom (a até 8), cada caixa vira uma
linha. É a primeira regra que olha a imagem: o print em cinza desce pelo pipeline como
parâmetro opcional. A ideia juntou duas respostas: a medida do fundo do Mistral e os vetos
de texto do Grok. Foram medidas as propostas de cinco IAs:

| Proposta | Certas (RapidOCR) | Certas (EasyOCR) | Erradas novas | Por que ganhou ou perdeu |
|---|---|---|---|---|
| Antes | 666 | 626 | — | — |
| **Mistral + vetos do Grok** | **670** | **630** | **0** | As 3 barras do EVE nas duas leituras; igual com 15 e 25 níveis |
| Mistral (moda dentro da caixa) | 668 | 626 | 0 | Exige a mesma altura (0,2h): o "g" de "Mining" derruba; vão até 0,6h exclui o EasyOCR |
| Grok (faixa acima da letra, CamelCase) | 666 | 628 | 1 | Faixa cai fora da aba com as caixas altas do RapidOCR; veto de cabeçalho trava as abas; CamelCase separou "[Esc] \| Back" |
| ChatGPT (faixas fora da caixa, sublinhado, veto de tabela) | 666 | 626 | 0 | Veto de tabela trava as abas; sem o sublinhado, separou "HP \| 129" |
| DeepSeek (sublinhado de 0,8-1,6h, veto de tabela) | 666 | 620 | 29 | Sublinhado longe demais; sem vetos de texto, cortou frases no EasyOCR |
| Qwen | — | — | — | Leu ao contrário: a regra mantém as abas juntas |

Limite: a evidência são 3 barras de um jogo só; a diferença de 25 níveis precisa ser
conferida em abas de outros jogos. Duas quebras de abas de uma palavra continuam
perdidas. O teste está em `laboratorios/quebras/experimentos/abas.py`. O texto abaixo
fica como registro do problema.

**Tipo:** montagem (itens lado a lado). **Tamanho:** 6 quebras. **Prints:** mercado e
overview do EVE.

**O que acontece.** Abas como "Browse | Quickbar", "Details | Groups" e "General | Mining
| WarpTo" vêm em caixas separadas, mas a apenas 0,17 a 0,29 altura uma da outra. A regra
de itens exige vão de 0,8 altura ou mais. Sem essa exigência, uma fala em maiúsculas que
o EasyOCR lê com uma caixa por palavra viraria uma palavra por linha.

**O que existe na imagem.** As abas do EVE não têm divisória desenhada. Só a aba
selecionada tem fundo mais claro, e um sublinhado corre por baixo da barra toda. Um
cabeçalho de tabela tem o mesmo visual.

**O que já foi tentado.** Aceitar vão pequeno quando alguma caixa da linha tem 2 palavras
ou mais. Isso resolveu as abas da ficha do EVE ("Home Station | ... | Expert Systems"),
mas não serve quando todas as abas têm uma palavra só.

**O que pesquisar.** Segmentação de elementos de interface pela imagem: regiões de fundo
de cor uniforme, bordas de botões e abas, detecção de componentes de UI. Em inglês, *GUI
element detection*, *UI component segmentation*, *screen parsing*. A solução teria de ser
leve, sem rede neural pesada.

**Como medir.** As 6 quebras, sem separar cabeçalhos de tabela nem falas em maiúsculas.

### Problema 4: itens que o OCR lê numa caixa só

**Tipo:** OCR e montagem. **Tamanho:** 11 quebras, 10 delas de um jogo. **Print:** barra
do Doki Doki ("History Skip Auto Save Load Settings").

**O que acontece.** O detector do RapidOCR expande cada palavra (`unclip_ratio = 1,6`)
antes de agrupar, e itens próximos viram uma caixa só. O espaço entre eles, medido nos
pixels da imagem:

| Texto | Espaço entre palavras (em alturas de letra) |
|---|---|
| Fala do Doki Doki | 0,12 a 0,20 |
| Barra do Doki Doki | cerca de 0,4, com um buraco de 1,8 a 3,7 entre "Auto" e "Save" |
| Fala do Mass Effect (fonte diferente) | até 0,35 |

Não há um limite que valha para todas as fontes. As caixas por palavra que o RapidOCR
devolve (`return_word_box`) são arredondadas pelo modelo e não servem para medir isso.

**O que já foi tentado.** Medir o espaço nas caixas por palavra e nos pixels; nenhum
limite separa a barra da fala sem errar em outra fonte. Também foi descartado reconhecer
os itens por uma lista de palavras ("Save", "Load"), porque só funcionaria em inglês.

**O que pesquisar:**
- comparar o espaço com o da **mesma fonte** em outra parte da tela, o que exigiria saber
  quais caixas usam a mesma fonte;
- detectar barras de interface pela posição e pelo tamanho da letra, já que a barra fica
  na borda e tem letra menor que a fala;
- uma segunda passada do detector com expansão menor, só para medir os vãos.

**Como medir.** As 10 quebras da barra, sem cortar falas e títulos de várias palavras
("Mass Effect Legendary Edition").

### Problema 5: texto miúdo e borrado em letreiros

**Tipo:** leitura. **Tamanho:** os letreiros acertam 79,4% das letras, contra 95,1% na
média. **Prints:** letreiro da banca e letreiros de rua do Night in the Woods (104,9% e
46,7% de erro de letras).

**O que acontece.** O OCR lê lixo em texto pequeno, borrado ou de pouco contraste. O
letreiro da banca tem mais lixo que texto. O corte de confiança em 0,7 já tira parte disso.

**O que já foi tentado.** Tudo aplicado ao print inteiro, sempre pior que a imagem em
cinza: ampliar 2x (com o EasyOCR, 12,27% → 13,32% de erro e 4 vezes mais lento),
binarizar, inverter cores, suavizar, CLAHE, nitidez. Com o RapidOCR, ampliar até 736 px
também piorou (7,87% → 9,30%).

**O que pesquisar:**
- super-resolução **só nas caixas pequenas ou de baixa confiança**, com uma segunda
  leitura do recorte. Modelos leves na CPU (Real-ESRGAN pequeno, ESPCN, FSRCNN; o OpenCV
  tem `dnn_superres`) e o custo de tempo de cada um;
- como reconhecer lixo de OCR (texto que não forma palavras) sem depender da língua.

**Como medir.** Acerto de letras nos letreiros, sem piorar os outros tipos e sem passar de
algumas centenas de milissegundos por print.

### Problema 6: números pequenos e ícones perto do texto

**Tipo:** leitura. **Prints:** inventário do Persona 4, overview do EVE.

**O que acontece:**
- no inventário do Persona, as quantidades ("x 1") somem: o "×" vira "X" e o número
  pequeno não é lido ("Soul Drop X" no lugar de "Soul Drop x 5");
- no overview do EVE, ícones da primeira coluna viram letras soltas ("i", "n", "D", "0",
  "△") e entram no texto.

**O que pesquisar:**
- uma segunda leitura de recortes pequenos à direita de um rótulo, só para números;
- como reconhecer ícones lidos como letra pela forma da caixa (quadrada, isolada,
  confiança mais baixa).

**Como medir.** Linhas "faltando" nas fichas (65 no total hoje).

### Problema 7: quebras verticais difíceis

**Tipo:** montagem. **Tamanho:** cerca de 10 quebras. **Prints:**
- título inclinado do Danganronpa;
- descrições curtas sem pontuação, uma por linha, no Caves of Qud ("Charge-based melee
  fighter" / "Ability to freeze enemies" / "Highly maneuverable");
- frases do mesmo parágrafo separadas pela regra de sentença terminada ("...the
  disappearance of the Dwarves." / "Yes, that's an excellent task for you") no diálogo do
  Morrowind e no tutorial do Caves of Qud.

**O que pesquisar.** Para as descrições curtas, a forma das linhas: várias linhas curtas
seguidas, de tamanho parecido e bem menores que a coluna, costumam ser uma lista. Para
as sentenças, se a linha de cima chegou perto da margem do painel (a do problema 1, que
agora existe no código como `_margem_local`), a quebra é visual, não de parágrafo.

### Problema 8: menu em que o primeiro item é o mais largo

**Tipo:** montagem. **Limite conhecido**, registrado em 2 testes automáticos como falha
esperada.

```
caixas:   "New game" (200 px) / "Continue" (180) / "Options" (160) / "Quit" (80)
app:      "New game Continue" / "Options" / "Quit"
esperado: "New game" / "Continue" / "Options" / "Quit"
```

**Por que falha.** A margem direita é a da linha mais larga, "New game", então nada
"cabe" depois dela. A regra de menu exige uma palavra por linha, e "New game" tem duas.

**O que pesquisar.** Sinais de menu vertical: linhas curtas, alinhadas à esquerda,
espaçamento regular, sem pontuação, todas começando com maiúscula. A regra precisa
funcionar em qualquer língua.

### Problema 9: ordem ambígua e a forma de medir

**Tipo:** métrica. **Print:** resumo do personagem no Caves of Qud, com 65% de erro de
letras e 0% sem contar a ordem.

**O que acontece.** O app lê a caixa de tutorial depois das colunas, e o gabarito a põe
antes. As duas ordens fazem sentido. A métrica de ordem conta como erro o que um humano
leria de qualquer um dos dois jeitos.

**O que pesquisar.** Métricas de ordem de leitura que aceitem ordens alternativas
válidas, como comparar blocos em vez da sequência inteira, ou gabaritos com mais de uma
ordem aceita. A medida de linhas inteiras já ajuda, porque não depende da ordem entre
linhas.

### Problema 10: outras línguas sem prints reais

**Tipo:** validação. Todos os 90 prints são em inglês. O app lê 83 línguas: 43 pelo
RapidOCR e 40 pelo EasyOCR. As regras de montagem só foram conferidas com 29 casos e 10 testes de abas
simulados.

**O que pesquisar:**
- prints reais em japonês, chinês, espanhol e árabe;
- os modelos do RapidOCR por escrita (PP-OCRv5 mobile para cirílico, árabe, coreano,
  devanágari e tailandês, cerca de 8 MB cada), que poderiam substituir o EasyOCR nessas
  línguas.

## 4. O que já foi testado e não funcionou

Para não pesquisar de novo o que já tem resposta:

| Ideia | Resultado |
|---|---|
| Tratar a imagem (binarizar, inverter cores, suavizar, CLAHE, nitidez, ampliar o print todo) | Sempre pior que a imagem em cinza |
| Outros motores (EasyOCR, PaddleOCR maiores, OCR do Windows, Tesseract) | O RapidOCR v6 small ganhou de todos |
| Combinar dois motores (votação, escolha por confiança, união de caixas) | Teto de 0,5 ponto de CER, com o dobro do tempo |
| Corretores de texto (pyspellchecker, SymSpell, BERT sozinho, regex agressivo) | Erravam termos de jogo; teto de cerca de 1% das palavras |
| Dicionário + BERT exigindo acordo | Funciona, mas ganhou 0,07 ponto com o EasyOCR e quase nada com o RapidOCR; fica opcional e desligado |
| Separar itens pelo vão grande | O vão não separa: rótulo e valor têm vãos maiores que itens |
| Proteger cabeçalho de tabela pela linha de 3+ títulos | Barrava o mercado do EVE, um dos maiores ganhos |
| Contraste entre nome e etiqueta em maiúsculas | 5 quebras certas e 8 erradas |
| Margem do bloco no "cabia" | Perdeu nas duas versões testadas e de novo nas propostas do Copilot e do Gemini (percentil 80 e mediana do bloco) |
| Margem por "apoio" de 2 linhas longas sem folga até o print (Grok) | Juntou linhas de tabela que terminam no mesmo x |
| Quebrar pares de linhas que terminam em número ou têm ":" (Gemini) | Sem exigir repetição, quebrou legendas e diálogos |
| Lista pela geometria só (mesmo x, larguras parecidas, Copilot) | Todo parágrafo alinhado à esquerda vira lista: 119 quebras erradas |
| Veto de "tabela embaixo" para abas (ChatGPT, Grok, DeepSeek) | Toda barra de abas fica em cima de uma lista: o veto travou as abas reais |
| Sublinhado como sinal de barra de abas | Passa embaixo das abas e do cabeçalho de tabela; não diferencia |
| Fundo medido fora da caixa (faixa acima ou abaixo da letra) | Com as caixas altas do RapidOCR, a faixa cai fora do retângulo da aba |
| Qualquer linha de título quebra | Estragava falas em maiúsculas |
