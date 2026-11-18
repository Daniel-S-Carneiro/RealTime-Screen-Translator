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
| OCR | RapidOCR com os modelos PP-OCRv6 small do PaddleOCR, no ONNX Runtime, na CPU. O detector lê o print no tamanho original (`limit_type=max`, até 2016 px). Caixas com confiança abaixo de 0,7 são descartadas. Em língua latina, caracteres chineses lidos em ícones são apagados. Depois, as caixas pequenas de menor confiança são relidas e o lixo que não se confirma sai (`releitura.py`); nos inventários, a célula de quantidade que o detector pulou é relida, e ícones lidos como letra saem pela forma (`quantidades.py`). Escritas que o modelo não lê (cirílico, árabe, coreano, devanágari, tailandês…) vão para o EasyOCR | `ocr_engine.py` |
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
- **Testes automáticos:** 29 casos simulados em várias línguas, 17 testes com telas
  desenhadas (abas e barras de menu) e 23 com um leitor de mentira (segunda leitura,
  quantidades e ícones), em `tests/`. Uma regra nova não pode quebrá-los.
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
| Acerto de letras | 95,8% |
| Acerto de palavras | 91,4% |
| Quebras achadas / certas | 91% / 91% (679 de 744 achadas, 69 a mais) |
| Linhas inteiras | 81% (535 de 661) |
| Das que não chegam inteiras | 37 com sobra (quebra perdida), 22 partidas, 67 com palavra faltando ou diferente |

| Tipo de tela | Prints | Acerto de letras | Linhas inteiras | Quebras a mais |
|---|---|---|---|---|
| texto | 28 | 99,5% | 92% | 3 |
| legenda | 21 | 99,4% | 81% | 1 |
| menu | 9 | 98,8% | 80% | 1 |
| ficha | 24 | 90,5% | 76% | 59 |
| letreiro | 8 | 85,9% | 78% | 5 |

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

### Problema 4: itens que o OCR lê numa caixa só (resolvido)

**Resolvido em 18/11/2026, na 2ª rodada.** Uma caixa com 6 palavras ou mais, todas só
letras, com 3 letras ou mais e nenhuma só minúscula, vira uma linha por palavra quando o
MENOR espaço entre as palavras, medido na tinta, é 1,5 vez a mediana do espaço da fala do
mesmo print e maior que o p90 dela (fala de 0,5 a 2 vezes a altura da caixa, 5 espaços
medidos ou mais). Proposta do Grok; as duas barras do Doki Doki se separam inteiras (670
→ 680 quebras certas), sem nenhuma quebra errada nos 90 prints, nas duas leituras. O
teste está em `laboratorios/quebras/experimentos/menus2.py`. Abaixo, o registro da 1ª
rodada e dos dados corrigidos.


**Rodada de 18/11/2026: sem solução, e com dois dados meus corrigidos.** Mandei o
problema a cinco IAs (ChatGPT, Grok, DeepSeek, Mistral e Qwen). Ao medir as propostas,
achei dois erros nos números que eu tinha passado:

- **O "buraco" entre "Auto" e "Save" não existe.** Na barra, "Skip" está apagado (item
  desabilitado) e, num dos prints, "Auto" está em branco (item ativo). A medida antiga (Otsu
  dentro da caixa) separa a tinta em duas cores e jogava essas palavras no fundo; o vão
  "de 1,8 a 3,7" era a largura delas. Medindo a tinta pela distância ao tom mais comum da
  caixa (20 níveis, 3 pixels por coluna), os cinco vãos da barra ficam entre 0,31 e 0,45.
- **A fala não fica sempre abaixo de 0,35.** Isso valia para o Doki Doki e o Mass Effect.
  Mediana do espaço entre palavras da fala, por jogo (em alturas da caixa):

  | Jogo | Mediana | p90 | | Jogo | Mediana | p90 |
  |---|---|---|---|---|---|---|
  | Immortal Clan | 0,16 | 0,21 | | Morrowind | 0,37 | 0,45 |
  | Doki Doki | 0,18 | 0,20 | | Persona 4 | 0,40 | 0,56 |
  | Mass Effect | 0,20 | 0,34 | | EVE Online | 0,41 | 0,50 |
  | Danganronpa | 0,22 | 0,34 | | Caves of Qud | 0,52 | 0,69 |
  | Fallout | 0,26 | 0,55 | | Undertale | 0,63 | 0,67 |
  | Night in the Woods | 0,31 | 0,39 | | | | |

  Os 0,4 da barra do Doki Doki estão abaixo da fala de cinco jogos. Só uma comparação com
  a fala **do mesmo print** pode funcionar.

Resultado das propostas (RapidOCR; antes: 670 quebras certas, 79 a mais):

| Proposta | Medida antiga: certas / a mais | Medida corrigida: certas / a mais | O que aconteceu |
|---|---|---|---|
| ChatGPT (espaço 1,35x o das vizinhas, macroespaço, regularidade) | 672 / 88 | 670 / 125 | As vizinhas nem sempre são fala da mesma fonte: picou textos do Qud e do Immortal Clan |
| Grok (2x a mediana da fala do print e acima do p90; sem fala, só vão de 1,5h) | 674 / 83 | 672 / 86 | Não pegou a barra com a medida corrigida; separou "Hifumi \| Yamada" e linhas de tabela do EVE |
| DeepSeek (gatilho: vão de 1,5h e 2,5x o segundo; corta em 0,35h) | 677 / 79 | 670 / 79 | Só funcionou por causa do buraco falso, e deixou "History Skip" junto; com a medida certa, não faz nada |
| Mistral (linha isolada; pedaços com todos os vãos de 0,35h ou mais) | 673 / 81 | 675 / 80 | Separou a barra inteira num print; no outro, "Skip" tem vão de 0,31. No EasyOCR, +8 erradas ("Unassigned \| Attribute \| Points") |
| Qwen (desvio dos vãos, maior vão de 0,35, larguras, maiúsculas) | 674 / 101 | 671 / 103 | Cortou falas, menus de contexto e fichas |
| Grok com a referência aberta (fala de 0,5 a 2 vezes a altura da barra) | — | 681 / 86 | Separou quase todos os itens das duas barras (11 quebras certas a mais), mas pôs 7 erradas em outros jogos ("Perimeter IX - \\| Ca", "4 \\| SP") e perdeu 2 linhas inteiras |

Nenhuma entrou. A mais promissora é a do Grok, que compara com a fala do mesmo print: ela
só falhou porque exigia a fala com altura parecida (25%), e no Doki Doki a letra da fala é
1,4 a 1,6 vez maior que a da barra. Aberta essa tolerância, quase todos os itens se separam, mas a regra
ainda precisa de vetos para não cortar linhas de tabela e pares como "4 SP". O sinal que sobrou, e que nenhuma IA viu porque eu não mandei, é a **cor
de cada item**: na barra, um item apagado e outro em branco. É parecido com o fundo da aba
selecionada do Problema 3, mas na tinta. O risco é que jogos também pintam palavras
dentro da fala (nome de item, tecla). Medido: na barra, a tinta de "Skip" tem tom 122-129 e
a das outras palavras 66-81; no print 2, "Auto" tem 226. Mas, nos 90 prints, 268 palavras
(em 809 caixas de 2 ou mais palavras) ficam a 40 níveis ou mais da mediana das outras da
mesma caixa: a cor sozinha não basta. Esses dados foram para a segunda rodada com as IAs
(pasta `rodada2-problema4`, fora do repositório). O teste está em
`laboratorios/quebras/experimentos/menus.py`. O texto abaixo é o registro original, com os
dados errados.

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

### Problema 5: texto miúdo e borrado em letreiros (resolvido em parte)

**Resolvido em parte em 18/11/2026.** 65% do erro dos letreiros era texto a mais (lixo
lido em capas de revista), e 5 dos 8 prints já estavam perfeitos. Uma segunda leitura do
recorte (`releitura.py`) tira o lixo: as 8 caixas pequenas de menor confiança de cada
print (menos de 32 px e menos de 0,6 da altura típica) são relidas pelo reconhecedor,
ampliadas com Lanczos; se a releitura não confirma e a confiança é menor que 0,85, a
caixa sai do texto. Proposta do Grok. Acerto de letras de 95,13% para 95,73%; letreiros
de 79,4% para 85,9%; texto a mais nos letreiros de 112 para 33 caracteres; nenhum outro
tipo de tela piorou. Custo: cerca de 35 ms por caixa relida, até 0,3 s nos prints com 8
candidatas.

| Proposta | Letras (90 prints) | Letreiros | Por que ganhou ou perdeu |
|---|---|---|---|
| Antes | 95,13% | 79,4% | — |
| **Grok** (concordância entre leituras, descarte abaixo de 0,85) | **95,73%** | **85,9%** | Tira o lixo que muda na releitura; mantém o que se confirma |
| Qwen (releitura com contraste esticado, troca com +0,10) | 95,13% | 79,4% | Só troca, nunca descarta: o lixo fica |
| Mistral (detector + reconhecedor de novo no recorte x2) | 95,03% | 79,5% | O detector novo cria e muda caixas em fichas e legendas |
| DeepSeek (reler as caixas de confiança 0,30-0,70) | 94,91% | 78,3% | Traz de volta caixas que o app descartava, com mais lixo |
| ChatGPT (discordou, sai; sem limite de confiança) | 94,80% | 79,1% | Descarta texto real das tabelas do EVE |

**O que continua aberto:** letras trocadas que as duas leituras erram igual ("SOCIAL
SECUPITY", "ADIMANISTRATION") e parte do lixo da banca (52% de erro). O teste está em
`laboratorios/quebras/experimentos/letreiros2.py`. O texto abaixo fica como registro.


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

### Problema 6: números pequenos e ícones perto do texto (resolvido em parte)

**Resolvido em parte em 18/11/2026**, com duas regras novas em `quantidades.py`, ligadas
no motor de OCR logo depois da segunda leitura dos letreiros:
- **Quantidades (proposta do Grok).** Uma coluna de quantidade são 2+ caixas só de
  número ou de "×" (até 2,5 alturas de largura, 0,6+ de altura), cada uma com o item mais
  perto à esquerda a 1+ altura de distância. Colunas a menos de 1,5 altura uma da outra
  viram um campo (o "×" e o número). Cada linha da coluna de itens que ficou sem
  quantidade tem o recorte do campo (15% de margem) relido só pelo reconhecedor, se houver
  um traço de tinta de 0,4+ altura; a leitura entra se for número ou "× N" com confiança
  0,7, no lugar dos pedaços da célula. No máximo 8 recortes por print.
- **Ícones (proposta do Qwen).** Saem: uma coluna de 3+ caixas de até 2 glifos com letra
  e não-letra misturadas (ou alturas 1,5x diferentes); um glifo solto (não dígito) fora
  de 0,6 a 1,5 altura do texto, sem vizinho do mesmo tamanho na linha; e até 2 glifos,
  abaixo de 0,7 altura, encostados na borda do print e sem vizinho. As caixas de um campo
  de quantidade não são tocadas (sozinha, a regra tirava um "X" do Persona).

As 8 linhas do inventário do Persona saem com "× N" (eram 0), o "Level 6" do Morrowind
aparece, e os 5 ícones do overview do EVE saem do texto. No benchmark completo, só
mudaram esses três prints: erro de letras de 4,27% para 4,21%, linhas inteiras de 532
para 535, quebras a mais de 72 para 69. O erro de palavras subiu de 8,50% para 8,59%
porque o app escreve "×1" e o gabarito, "x 1". Três
ajustes à proposta do Grok vieram da medição: o item de cada quantidade é o mais perto à
esquerda (pegando o primeiro da linha, os dois painéis do Morrowind se misturavam e
saíam "Class 30" e "Endurance 20"); uma célula com outro texto não é relida ("Reputation:
-475" virava "-475 75"); e a leitura nova passa pelo corte de 0,7 (entrava um "3" com
0,12). O resultado é o mesmo com o vão mínimo de 0,5 a 1,5 altura.

| Proposta | Linhas certas do Persona (de 8) | Ícones do EVE (de 5) | Nos outros prints |
|---|---|---|---|
| **Grok** (campo inteiro relido; micro < 0,55H) | **8** | 0 | + "Level 6" no Morrowind |
| **Qwen** (âncoras de um token; coluna misturada, glifo solto, borda) | 1, mais um "7" no lugar do "1" | **5** | Um "20" a mais no Morrowind |
| Mistral (zona à direita dos itens; pontos) | 6 | 0 | "1" errado em 6 linhas do Morrowind, lixo no Fallout |
| ChatGPT (células previstas; coluna de ícones <= 0,65H) | 3, mais um "7" no lugar do "5" | 0 | Nada muda |
| DeepSeek (componentes de Otsu a até 2h; confiança >= 0,9 + forma) | 0 | 0 | Dígitos de lixo em 10 prints |

**Correção dos dados.** Os três "0" do Caves of Qud em x 828 a 844, listados antes como
ícones, são os valores de "Reputation: 0" e estão no gabarito. O ChatGPT e o Qwen
desconfiaram disso, e a regra do Grok protege números.

**O que continua aberto:** o "D" do Qud (1,45 altura, dentro da faixa do glifo solto) e
"po" / "on" na borda direita (0,85 e 0,80 altura; com o limite em 0,9 sai só o "po", em
1,2 a regra tira texto real do EVE); o "HP" / "SP" claro do primeiro personagem do
Persona; e a quantidade à esquerda do item, em línguas da direita para a esquerda (as do
RapidOCR são todas da esquerda para a direita). O teste está em
`laboratorios/quebras/experimentos/quantidades.py`. O texto abaixo fica como registro.


**Tipo:** leitura. **Prints:** inventário do Persona 4, overview e skills do EVE,
reputação do Caves of Qud.

**O que acontece** (conferido no app em 18/11/2026):
- no inventário do Persona, as quantidades somem ou se deformam: "Medicine x 1" sai
  "Medicine", "Soul Drop x 5" sai "Soul Drop X", "Peach Seed x 6" sai "Peach Seed 6". No
  mesmo print, para um personagem, "HP 136" / "SP 31" saem só "136" / "31";
- ícones viram letras soltas e entram no texto: "i", "n", "0" e "△" no overview do EVE;
  "D", "0", "po" e "on" na reputação do Caves of Qud (ícones das facções); "+" nos botões
  das skills do EVE. A segunda leitura dos letreiros (18/11) já tira os ícones de
  confiança baixa ("D", "0" e "☑ - ×" no EVE); estes ficam porque o reconhecedor os lê do
  mesmo jeito duas vezes, com confiança alta. (Uma revisão de 18/11 tinha tirado "n" e
  "△" desta lista por engano: a conferência olhou só os primeiros 14 itens.)

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
RapidOCR e 40 pelo EasyOCR. As regras de montagem só foram conferidas com 29 casos e 17 testes de telas desenhadas (e a releitura, com 9 testes de leitor de mentira)
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
| Letreiros: detector + reconhecedor de novo no recorte ampliado (Mistral) | O detector novo cria e muda caixas em fichas e legendas |
| Letreiros: reler as caixas que o corte de 0,7 descarta (DeepSeek) | Traz de volta mais lixo do que texto |
| Letreiros: descartar sempre que as leituras discordam (ChatGPT) | Descarta texto real de tabelas |
| Separar itens numa caixa por um limite fixo de vão (0,35h) | A fala de cinco jogos tem vão maior que o da barra do Doki Doki (0,4) |
| Separar itens pelo "buraco" grande da barra do Doki Doki | O buraco era um erro de medida: palavras de outra cor que o Otsu jogava no fundo |
| Qualquer linha de título quebra | Estragava falas em maiúsculas |
| Quantidades: reler só a célula do "×" (ChatGPT) | O "×" sozinho sai com confiança de 0,5; junto com o número, de 0,74 a 0,99 |
| Quantidades: procurar em toda a zona à direita dos itens (Mistral, DeepSeek) | Pega outras colunas e lê "1", "#" e ")" em fichas |
| Trocar "×" por "x", ou pôr espaço ("× 1"), na saída | Com "x" minúsculo, a coluna parece texto corrido; com duas palavras, vira um bloco separado. Nos dois casos, as quantidades saem juntas depois dos itens |
| Ícones: só caixas bem menores que o texto (0,55H ou 0,65H) | O "n" do EVE tem 0,61H e os outros ícones são maiores: não dispara |
