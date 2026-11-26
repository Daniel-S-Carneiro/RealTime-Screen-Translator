# Quinze problemas, cinco IAs e uma régua

*Anexo do [estudo de caso](estudo-de-caso-ocr.md). Rodadas de 17 a 25/11/2026. Cada
problema, com os dados reais e a tabela de cada proposta, está em [problemas em
aberto](problemas-em-aberto.md). A numeração aqui é a do arquivo de perguntas às IAs; nos
problemas em aberto, o 7 e o 8 estão trocados (lá, o Problema 7 é o das quebras verticais,
que inclui os itens em duas linhas, e o 8 é o do menu vertical).*

## Resumo

Entre 17 e 19/11/2026, mandei a outras IAs oito problemas de montagem e de leitura que eu
não sabia resolver. Nos dois primeiros, perguntei ao ChatGPT, ao Grok, ao Copilot e ao
Gemini. Do terceiro em diante, ao ChatGPT, ao Grok, ao DeepSeek, ao Mistral e ao Qwen.

Nenhuma resposta entrou no app só porque parecia boa. Cada proposta virou uma variante no
laboratório e foi medida em três lugares antes de qualquer mudança no app:
- nos 90 prints, sobre as caixas guardadas do RapidOCR (a leitura do app);
- nos mesmos prints, sobre as caixas do EasyOCR (outra geometria);
- em casos simulados em várias línguas.

Entraram regras nos oito problemas: dois ficaram resolvidos em parte, e um só se resolveu
na 2ª rodada. Em quatro, a regra que entrou junta peças de duas IAs.

| Medida (90 prints, RapidOCR) | Antes (17/11) | Depois (19/11) | Diferença |
|---|---|---|---|
| Acerto de letras | 95,1% | 95,8% | +0,7 ponto (o erro caiu 14%) |
| Acerto de palavras | 91,1% | 91,4% | +0,3 ponto |
| Quebras achadas | 662 de 744 (89,0%) | 684 de 744 (91,9%) | +22 |
| Quebras certas | 88,6% | 90,8% | +2,2 pontos |
| Quebras a mais | 85 | 69 | −16 (−19%) |
| Linhas que chegam inteiras ao tradutor | 519 de 661 (78,5%) | 539 de 661 (81,5%) | +20 |
| Linhas que saem junto de outra | 47 | 33 | −14 |
| Linhas cortadas ao meio | 30 | 22 | −8 |

"Antes" é o benchmark de 17/11, logo depois da base de testes (commit `235b28e`), quando
comecei as perguntas. "Depois" é o de 19/11, com as regras dos oito problemas.

## Antes e depois por tipo de tela

| Tipo de tela | Prints | Letras (antes → depois) | Linhas inteiras (antes → depois) | Quebras a mais (antes → depois) |
|---|---|---|---|---|
| Ficha (tabelas, inventários, grades, painéis) | 24 | 90,3% → 90,5% | 72% → 77% | 69 → 59 |
| Letreiro (placas, cartazes, títulos de cena) | 8 | 79,4% → 85,9% | 74% → 78% | 11 → 5 |
| Texto (descrições, tomos, diário, tutorial) | 28 | 99,5% → 99,5% | 92% → 92% | 3 → 3 |
| Legenda (falas e avisos) | 21 | 99,4% → 99,4% | 81% → 81% | 1 → 1 |
| Menu (opções, abas, diálogos com escolhas) | 9 | 98,8% → 98,8% | 80% → 80% | 1 → 1 |

O ganho foi todo em fichas e letreiros, que eram os tipos de tela onde estava o erro.
Texto corrido, legendas e menus já estavam bons e não pioraram em nenhuma rodada. Essa era
a condição de entrada de qualquer regra.

As linhas inteiras não mostram tudo. As regras das abas e da barra de menu renderam 14
quebras certas e nenhuma linha inteira, porque a medida só conta linhas do gabarito com
duas palavras ou mais, e cada aba ou item de menu é uma palavra só. Para essas duas, a
medida que conta é a das quebras. (Observação do Grok na avaliação de 19/11.)

## Rodada a rodada

| # | Problema | Data | Quem respondeu | O que entrou (de quem) | Linhas inteiras | Quebras achadas / a mais | Letras |
|---|---|---|---|---|---|---|---|
| — | Antes | 17/11 | — | — | 519 | 662 / 85 | 95,13% |
| 1 | Parágrafo de painel estreito cortado ao meio | 17/11 | ChatGPT, Grok, Copilot, Gemini | Margem do painel pelas linhas longas vizinhas (**ChatGPT**) | 524 | 662 / 79 | igual |
| 2 | Lista "rótulo valor" numa linha só | 17/11 | as mesmas quatro | 3+ campos curtos empilhados, sem quebrar antes de minúscula (**Grok**) | 529 | 666 / 79 | igual |
| 3 | Abas de uma palavra encostadas | 18/11 | ChatGPT, Grok, DeepSeek, Mistral, Qwen | Fundo da aba selecionada medido dentro da caixa (**Mistral**) + vetos de texto (**Grok**) | 529 | 670 / 79 | igual |
| 4 | Barra de menu lida numa caixa só | 18/11 | as mesmas cinco, em duas rodadas | Espaço entre as palavras na tinta contra o da fala do mesmo print (**Grok**, 2ª rodada) | 529 | 680 / 79 | igual |
| 5 | Texto miúdo e borrado (letreiros) | 18/11 | as mesmas cinco | Segunda leitura das caixas pequenas; o que muda na releitura sai (**Grok**) | 532 | 679 / 72 | 95,73% |
| 6 | Quantidades que o detector pula e ícones lidos como letra | 18/11 | as mesmas cinco | Recorte da quantidade relido (**Grok**) + ícones pela forma e pela coluna (**Qwen**) | 535 | 679 / 69 | 95,79% |
| 7 | Menu em que o primeiro item é o mais largo | 18/11 | as mesmas cinco | Pilha de itens curtos com uma borda alinhada (**Grok**) + até 5 palavras e reticências (**Qwen**) | 538 | 681 / 69 | igual |
| 8 | Lista em que um item quebrou em duas linhas | 19/11 | as mesmas cinco | 2+ itens com caixas sobrepostas (**Grok**) + "modo fraco" para um item só (**ChatGPT**) | 539 | 684 / 69 | igual |

Os benchmarks de cada linha estão em `relatorios/benchmark/` (fora do git):
`benchmark_20261117_165155.csv` (antes), `_182013`, `_235146`, `_20261118_005037`,
`_021104`, `_175342`, `_190353`, `_194533` e `benchmark_20261119_011848.csv`.

No problema 6, o acerto de palavras caiu de 91,50% para 91,41%. É a régua, não a leitura:
as quantidades do inventário passaram a sair "×1" e o gabarito diz "x 1".

A 1ª versão do problema 8 (as descrições curtas do Caves of Qud) foi resolvida pela regra
do problema 7 antes de as respostas serem medidas. A 2ª versão trouxe a lista de tópicos do
Morrowind.

**Depois da validação (24/11).** Os erros que a validação com jogos novos revelou voltaram
para a consulta. A régua passou a ser de 140 prints (os 90 e os 50 da validação), e a
pergunta passou a pedir que cada IA aplicasse a própria regra, à mão, a cada caso real.

| # | Problema | Data | Quem respondeu | O que entrou (de quem) | Linhas inteiras (90 prints) | Quebras a mais |
|---|---|---|---|---|---|---|
| 9 | Frase que termina no fim da linha corta o parágrafo | 24/11 | ChatGPT, Grok, DeepSeek, Mistral, Qwen | Fim de frase não quebra se as linhas estão coladas (**Mistral**; o mesmo sinal do **ChatGPT**) | 541 → 546 | 69 → 63 |
| 10 | Descrição de item centralizada, uma propriedade por linha | 24/11 | as mesmas cinco | Pontuação e linha cheia (**Mistral**) + prova de centralização (**Grok**) + travas da vírgula e da largura (minhas) | igual nos 90; validação 197 → 207 | igual |
| 11 | Menu inteiro lido numa caixa só, itens de mais de uma palavra | 25/11 | Grok, Mistral, Qwen | Espaços pelas palavras do reconhecedor, salto de 2,2x e itens com maiúscula (**Mistral**) + regularidade de 2x (**Grok**) | igual nos 90; validação 207 → 210 | igual |
| 12 | O OCR engole o espaço entre duas palavras | 25/11 | as cinco | Candidatos pela geometria e decisão pela probabilidade do CTC (**ChatGPT**), na versão barata (a margem do espaço na coluna) | 546 → 550; validação 210 → 213 | igual |
| 13 | Duas caixas na mesma linha: dois itens ou rótulo e valor? | 25/11, duas rodadas | as cinco (o Qwen com duas respostas) | Censo de colunas com valor curto, cabeçalho e vão de 2,1 h (**Grok**, 2ª rodada) | 550 → 550; validação 213 → 216; espanhol 10 → 11 | 63 → 65 |
| 14 | Ícone lido como símbolo e colado à linha | 25/11 | as cinco | Coluna de 3+ símbolos iguais, glifo baixo e longe, e o cursor só antes de atalho (**Grok**) | 550 → 560; validação 216 → 217 | 65 → 64 |
| 15 | Frase ou rótulo quebrado em linhas curtas e coladas | 25/11 | as cinco | Uma regra estreita por formato: minúscula colada, letreiro, balão, item que quebrou na lista, cauda em maiúsculas e título deslocado (**Grok**) + a palavra de baixo sem dígito (minha); a trava e o título deslocado saíram em 26/11 | 560 → 562; validação 217 → 219; espanhol 11 → 14 | 64 → 61 |

**Depois da releitura dos gabaritos (26/11).** A releitura achou 12 gabaritos do Immortal
Clan fora da regra de uma linha por item ([A releitura dos
gabaritos](classificacao-linhas-perdidas.md#a-releitura-dos-gabaritos-25112026)). Por isso,
as propostas dos problemas 9 a 15 foram medidas de novo, cada uma contra o app da época e
nas mesmas quatro leituras, com o gabarito antigo e com o corrigido. Ficou de fora o 12,
cuja medida é a dos espaços certos e errados. Com o gabarito antigo, a medida reproduz os
números de cada rodada. Os problemas 9, 10, 11 e 14 não mudam. No 13 e no 15, as mudanças
são todas a favor da regra que entrou (linhas ganhas e perdidas):

| Proposta | Gabarito antigo | Gabarito corrigido |
|---|---|---|
| 13, 2ª rodada: **Grok** (entrou) | +7 −1 | **+10 −0** |
| 13, 2ª rodada: Qwen | +7 −1 | +7 −1 |
| 13, 2ª rodada: DeepSeek | +9 −8 | +12 −5 |
| 13, 1ª rodada: Grok, DeepSeek e Mistral | +13 −5, +13 −54, +9 −53 | +16 −4, +16 −51, +12 −50 |
| 15: **Grok, como escreveu** | +9 −1 | **+9 −0** |
| 15: DeepSeek | +8 −6 | +7 −5 |
| 15: ChatGPT (padrões 1 e 4), Qwen | +6 −20, +5 −63 | +6 −18, +4 −63 |
| 15: ChatGPT (todos os padrões), Mistral | +9 −141, +9 −165 | +8 −139, +9 −163 |

No 13, a única perda do Grok era "Lasts 30 days | Cat Ledger", na loja: o gabarito
antigo juntava os dois itens. Com ele relido, a regra separa os dois e não perde nenhuma
linha, e o Grok desempata com o Qwen. No 15, a trava do dígito, que era minha, só barrava
uma junção certa. Ela saiu, e o título deslocado também, porque tinha sido feito para o
título da loja, outro gabarito errado. A regra que está no app é a do Grok como ele
escreveu, menos o título deslocado. O ChatGPT e o DeepSeek não responderam o problema 11:
colei o texto errado nas duas conversas.

As cinco disseram acertar os 13 casos da pergunta. Nos 140 prints, só o Mistral e o
ChatGPT não perderam nenhuma linha; Grok, DeepSeek e Qwen perderam de 2 a 6, quase sempre
no mesmo título de cartaz e numa resposta do Katawa Shoujo. No problema 10, nenhuma
proposta passou sem perder linhas: a que entrou junta peças de duas IAs e duas travas que
nenhuma propôs, como já tinha acontecido nos problemas 3 e 6. No problema 11, a medida veio
de mim (as palavras que o próprio reconhecedor dá, que o desenho atrás das letras não
atrapalha), e a regra, das IAs. O que separou as três propostas foi uma trava de forma:
item começa com maiúscula. Sem ela, o Grok e o Qwen cortavam frases na fonte de largura
fixa do Caves of Qud. Os detalhes estão em [Por que as linhas se
perderam](classificacao-linhas-perdidas.md).

**Antes do congelamento (25/11).** Depois de revisar tudo o que ainda se perde nos 150
prints, foram para as IAs quatro padrões que se repetem em vários jogos (problemas 12 a 15):
o espaço engolido pelo OCR, duas caixas distantes na mesma linha, o ícone lido como
símbolo e a frase quebrada em linhas curtas e coladas. No problema 12, três das cinco
propostas eram regras de passo e de tinta, e cada uma inseriu centenas de espaços errados;
a que entrou, do ChatGPT, deixa o próprio reconhecedor decidir, pela probabilidade que ele
já calcula. No problema 13, a 1ª rodada não deu regra segura: todas as propostas separavam pares que o gabarito junta. A 2ª rodada mostrou os cinco desenhos em que elas erravam, com as coordenadas, e as perdas caíram de dezenas de linhas para uma. No problema 14, a proposta que entrou, do Grok, foi a mais exigente com o contexto: só tira o ">" de cursor quando vem antes de um atalho entre colchetes. Qwen, DeepSeek e Mistral tiravam todo ">" no começo da linha e apagaram um que, no Persona 4, é texto. No problema 15, juntar linhas coladas se mostrou mais arriscado que separar: as propostas com um sinal largo (a linha de cima bem mais larga, a de baixo fechando a frase) juntaram de 104 a 139 pares que o gabarito separa, quase todos itens de menu e de lista. A do Grok tinha uma regra estreita para cada formato, sempre com um segundo sinal além das caixas coladas, e não juntou nenhum par errado depois de uma trava (a palavra de baixo sem dígito). A releitura dos gabaritos, no mesmo dia, mostrou que dois casos do problema 15 estavam com o gabarito errado: o título da loja do Immortal Clan, que foi às IAs, e a quantidade "x300,000". Com isso, a trava e o título deslocado do Grok ficaram sem caso que os sustente e saíram em 26/11, sem piorar nenhum print (veja [A releitura dos gabaritos](classificacao-linhas-perdidas.md#a-releitura-dos-gabaritos-25112026)).

## O que decidiu cada rodada

1. **Margem do painel.** Três propostas usavam uma margem só para o bloco, uma ideia que eu
   já tinha descartado. A do ChatGPT olhava as linhas longas vizinhas e só valia se a margem
   ficasse bem para dentro do print. Só 4 prints mudaram, todos para melhor.
2. **Listas de rótulo e valor.** Três IAs acharam o mesmo sinal: linhas seguidas terminando
   em número. Ganhou a única que lembrou do freio, que é não quebrar antes de uma linha que
   começa com minúscula. Sem ele, a mesma ideia cortava uma frase do registro do Caves of
   Qud.
3. **Abas.** Nenhuma IA acertou sozinha. Três propunham um veto de "tabela embaixo", e toda
   barra de abas fica em cima de uma lista. A medida do fundo veio do Mistral e os vetos de
   texto vieram do Grok; juntas, separaram as três barras do EVE nas duas leituras.
4. **Barra numa caixa só.** A 1ª rodada não deu nada, por culpa dos meus dados: um "buraco"
   entre as palavras era erro da minha medida, e um limite de fala só valia para dois
   jogos. Com os números corrigidos e o retorno de onde cada proposta tinha errado, o Grok
   mudou a própria regra na 2ª rodada, e ela separou as duas barras do Doki Doki sem
   nenhuma quebra errada.
5. **Letreiros.** Separar o erro em troca, falta e sobra mostrou que 65% era lixo. A regra
   que entrou não lê melhor: ela tira o que muda quando o recorte é relido. As outras
   pioravam ou não mudavam nada: reliam com o detector, traziam de volta caixas
   descartadas, descartavam texto real ou só trocavam letras e deixavam o lixo.
6. **Quantidades e ícones.** Para as quantidades, entrou a do Grok, que relê o campo inteiro:
   junto com o número, o "×" sai com confiança de 0,74 a 0,99, e sozinho, de 0,5. Para os
   ícones, entrou a do Qwen. Na pergunta, eu tinha chamado de ícone três "0" que eram valores
   reais; duas IAs desconfiaram.
7. **Menu vertical.** Duas propostas mediam a linha "curta" contra a largura do print, e num
   print só de menu a linha mais larga é o print. Entrou a do Grok, com travas que vieram da
   medição no EasyOCR e duas ideias do Qwen. A regra resolveu de quebra o problema
   seguinte.
8. **Itens em duas linhas.** Eu mandei só as 10 linhas da lista. No print, um botão fica logo
   acima dela, e duas propostas que acertavam a lista recortada não disparavam no print
   inteiro. Entrou a do Grok, mais o "modo fraco" do ChatGPT: com um item só em duas linhas,
   quem decide é a regra do menu.

## Placar por IA

"Entrou" quer dizer que a regra, ou uma peça dela, está no app hoje. O placar conta os 15
problemas: de 1 a 8 (17 a 19/11, nos 90 prints) e de 9 a 15 (24 e 25/11, nos 150 prints).
Os números de 9 a 15 já são os da medida com os gabaritos relidos.

| IA | Rodadas | Entrou em | Onde acertou | Onde errou, em geral |
|---|---|---|---|---|
| **Grok** | 17 | 12 dos 15 (2 a 8, 10, 11, 13, 14 e 15) | Regras com limiares medíveis e um freio; uma regra estreita para cada formato (15); o cursor só antes de atalho (14); mudou a própria regra com o retorno (4 e 13) | A regra crua às vezes precisava de travas: juntou linhas de tabela na margem (1), partiu uma manchete no EasyOCR (7), juntou o título do cartaz ao convite (9), cortou frases no Caves of Qud com o salto pela diferença (11) e pôs 686 espaços errados pela tinta (12) |
| **Mistral** | 15 | 5 (a medida das abas no 3, a confirmação do modo fraco no 8, e as regras do 9, do 10 e do 11) | A medida do fundo dentro da caixa (3); limiares com folga, que entraram como ele escreveu (9 e 11); a trava da maiúscula, que decidiu o 11 | Sinais largos sem trava: juntou menus e listas inteiras no 15 (163 linhas perdidas); tirou um ícone certo e desmontou a grade do EVE (14); regras sem trava de largura ou de palavras (8), com o detector de novo no recorte (5) e com a linha curta medida contra o print (7) |
| **ChatGPT** | 16 | 3 (1 inteira, 8 como peça, 12 numa versão barata) | Ideias de estrutura: a margem do painel, o modo fraco e a probabilidade do CTC, o único sinal que separou os espaços certos dos errados (12); no 9, o mesmo sinal da regra que entrou | O grupo só pelo centro (10) e os sinais largos para juntar (15); vetos de tabela (3), descarte sem limite (5), pontuação de evidências que deixa passar prosa (7) e regra para o bloco inteiro (8); quando foi cauteloso, não errou nada, mas pegou pouco (13 e 14) |
| **Qwen** | 15 | 2 (ícones no 6, travas no 7) | O diagnóstico mais preciso no problema 8; no 13, os mesmos ganhos do Grok | Limiares fixos que cortam palavras e frases (11 e 12); a tabela da resposta nem sempre batia com a regra que ele escreveu (11, 14 e 15); leu um problema ao contrário (3); regras que cortavam falas (4) ou partiam prosa (8) |
| **DeepSeek** | 14 | nenhum | Os maiores ganhos brutos no 10 e no 13; citou como saída a probabilidade do CTC, que entrou no 12 | Ganhos com perdas grandes: o grupo só pelo centro (10), o "senão: separa" (13), o "O" das telas em maiúsculas e o "×" das quantidades (14), a palavra única que junta itens de menu (15); vetos e sinais que não aparecem nos prints (3), números errados no diagnóstico e, no problema 4, uma regra que só funcionava por causa do meu dado errado |
| **Copilot** | 2 | nenhum | — | Margem por bloco, já descartada; ilustrou a proposta com coordenadas que não estavam no material |
| **Gemini** | 2 | nenhum | — | Margem por bloco; lista sem exigir repetição (12 quebras erradas) |

O Copilot e o Gemini respondiam muito rápido e repetiam ideias que a pergunta dizia já ter
testado. Do problema 3 em diante, entraram no lugar deles o DeepSeek, o Mistral e o Qwen.

O Grok entrou em mais problemas, mas a melhor resposta não veio sempre dele:
- o ChatGPT ganhou o 1 e o 12 e trouxe a peça que faltava no 8;
- o Mistral ganhou o 9 e o 11, deu a estrutura do 10 e trouxe a medida que resolveu as abas;
- o Qwen trouxe as travas do menu.

Em seis problemas, a regra que entrou junta peças de duas IAs (3, 6, 7, 8, 10 e 11). O
DeepSeek não entrou em nenhum: as propostas dele ganhavam muito e perdiam muito.

## O que aprendi sobre perguntar a outras IAs

1. **A régua decide, não o tom da resposta.** Todas as respostas vinham seguras, com
   limiares e exemplos. De mais de 40 propostas, entrou uma por problema (ou peças de duas),
   quase sempre com ajustes. Sem a medida nos 90 prints e nas duas leituras, várias teriam
   entrado e piorado o app.
2. **Mande números reais, o que já falhou e o entorno do caso.** As respostas melhoraram
   quando a pergunta trazia caixas de verdade e a lista do que não funcionou. E pioraram
   quando faltava contexto: no problema 8, o recorte sem o botão de cima.
3. **Confira os próprios dados antes de perguntar.** No problema 4, as cinco IAs
   trabalharam sobre dois números meus que estavam errados. A rodada inteira foi perdida,
   e a 2ª, com os dados certos, resolveu.
4. **O freio vale tanto quanto o sinal.** Nos problemas 2, 7 e 8, várias IAs acharam o
   mesmo sinal. Ganhou a que trouxe a trava que protege a prosa.
5. **Junte peças de respostas diferentes.** Em quatro dos oito problemas, a regra que
   entrou combina duas IAs (em seis dos 15, contando de 9 a 15). Medir cada peça
   separada mostra o que manter e o que tirar.
6. **Devolva o resultado.** Depois de cada rodada, cada IA recebeu a tabela de todas e uma
   nota sobre a própria proposta. As respostas seguintes repetiram menos ideias já
   descartadas, e o Grok mudou a própria regra a partir do retorno.
7. **Teste onde a regra não devia disparar.** Regras que pareciam limpas no RapidOCR erravam
   no EasyOCR ou em casos simulados em alemão e japonês. Cada caso desses virou teste
   automático.
8. **O ganho cai a cada rodada.** As duas primeiras rodadas renderam 5 linhas inteiras
   cada; a última, 1. Entre uma linha e a de baixo, o app hoje perde só 2 de 470 quebras. O erro
   que sobra está nas fichas e na leitura, e o próximo passo é medir as regras em jogos
   novos, não perguntar mais. (Foi o que aconteceu: a validação de 24/11 abriu os
   problemas 9 a 15.)
9. **Mostre o erro.** Na 1ª rodada do problema 13, todas as propostas separavam pares que o
   gabarito junta. A 2ª rodada mostrou os cinco desenhos em que elas erravam, com as
   coordenadas, e as perdas caíram de dezenas de linhas para uma. Com o gabarito relido,
   caíram para nenhuma.
10. **Para juntar, peça dois sinais.** No problema 15, as propostas com um sinal largo
    ("a linha de baixo fecha a frase", "a de cima é bem mais larga") juntaram mais de 100
    pares errados, quase todos itens de menu e de lista. A do Grok tinha uma regra estreita
    para cada formato, cada uma com um segundo sinal, e não juntou nenhum par errado.
11. **O gabarito também é dado.** A releitura de 25/11 achou 12 gabaritos do Immortal Clan
    fora da regra. Um caso do problema 15 foi às IAs com a resposta errada, e a regra que
    veio para ele (o título deslocado) saiu depois, junto com uma trava minha feita para
    outro gabarito errado. No problema 13, a única perda da regra que entrou era um desses
    gabaritos. A lição 3 vale para o gabarito: confira antes de perguntar.

## O custo

- De 17 a 19/11, três dias, nove rodadas medidas e mais de 40 propostas testadas.
- De 24 a 25/11, mais oito rodadas (problemas 9 a 15) e 39 propostas, medidas nos 150
  prints e nas duas leituras. Em 26/11, as dos problemas 9 a 15, menos as do 12, foram
  medidas de novo com os gabaritos relidos; cada uma leva de 10 a 20 segundos.
- Cada rodada custou o tempo de colar a pergunta em cinco conversas e guardar as respostas.
  A medida de cada proposta, sobre as caixas guardadas, leva segundos.
- Nenhuma API paga. Nenhum dado pessoal foi enviado: sem chaves de API, sem o arquivo de
  configuração, só a descrição dos prints e as coordenadas das caixas.
- Conversa longa num plano grátis pode perder o contexto. Para isso, cada problema também
  tem um texto pronto para uma conversa nova, com o contexto atualizado.

## O que continua aberto

- **Fichas:** 59 das 69 quebras a mais estão nelas.
- **Leitura:** 67 linhas do gabarito têm alguma palavra que o OCR não leu ou leu diferente.
  Há letras trocadas que as duas leituras erram igual nos letreiros ("SECUPITY"), e o que
  sobrou dos ícones (o "D" e os pedaços "po" e "on" na borda do Caves of Qud, o "HP" e o
  "SP" claros do Persona).
- **Limites conhecidos**, registrados como testes que falham de propósito: menu de só 2
  itens, itens de largura parecida e itens com minúscula no mesmo passo de uma frase. As
  cinco IAs disseram que não há regra segura para eles. Isso não prova que não exista uma:
  mostra que, com o material que mandei, nenhuma proposta sobreviveu. Eles ficam abertos,
  à espera de um print real que os exija.
- **Validação:** as regras dos oito problemas foram medidas só nestes 90 prints, a maioria
  em um ou dois jogos. O [plano de validação](plano-de-validacao.md) diz como medi-las em
  jogos novos.

## O que as avaliações de 19/11 acrescentaram

Depois do balanço, pedi ao ChatGPT e ao Grok uma avaliação do projeto inteiro. Os dois
concordaram: congelar as regras, não abrir outra rodada e ir para a validação com jogos
novos. O que entrou a partir das avaliações, sem mudar nenhuma regra do app:
- a versão de referência marcada com a tag `referencia-validacao-2026-11-19`, e a
  [referência da validação](referencia-validacao.md), com uma linha por regra, o estado
  dela e o que a reprovaria num jogo novo;
- a medida de letras sem ordem no benchmark, que põe as linhas lidas na ordem do gabarito
  antes de comparar. Nos 90 prints, ela dá 97,0% contra 95,8%, e só mudam 4 fichas com
  dois painéis. O portão de letras da validação passou a usar essa medida;
- o fluxo da coleta corrigido: prints movidos para `validacao/`, gabarito escrito antes de
  abrir o rascunho do app, um manifesto com a regra que cada print testa;
- um jogo em outra língua na coleta, porque os 90 prints são todos em inglês;
- o tempo p95 por print como indicador fixo: 2,5 s, contra 0,8 s de média. O que pesa é a
  quantidade de texto; a segunda leitura e as quantidades somam 23 ms na mediana.

## Onde estão os detalhes

- [Problemas em aberto](problemas-em-aberto.md): cada problema, com os dados que mandei, a
  tabela de cada proposta e o que já foi testado e não funcionou.
- [Estudo de caso](estudo-de-caso-ocr.md), seção 7: uma subseção por regra que entrou, e as
  lições 22 a 33.
- Os scripts que mediram cada proposta ficam em `laboratorios/quebras/experimentos/`, fora
  do git: `margens.py`, `fichas.py`, `abas.py`, `menus.py`, `menus2.py`, `letreiros2.py`,
  `quantidades.py`, `menus_verticais.py` e `topicos.py`.
