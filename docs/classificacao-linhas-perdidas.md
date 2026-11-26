# Por que as linhas se perderam: a validação, linha por linha

*Fase 4.2 do [plano de validação](plano-de-validacao.md), feita em 24/11/2026. Cada linha
que não chegou inteira ao tradutor na rodada 1 ganhou uma causa: 100 em inglês e 13 em
espanhol. Usei o texto que o app montou e, nos casos duvidosos, a imagem do print. Os
números são os da medida com os gabaritos corrigidos, descrita em [Resultados da
validação](resultados-validacao.md).*

A lista completa, com a linha do gabarito, o que o app entregou e a causa, fica fora do git,
em `relatorios/validacao/linhas_perdidas.txt` e `relatorios/validacao/classificacao.csv`.
Os scripts que geram as duas ficam em `laboratorios/validacao/`.

## O resumo

Das 100 linhas perdidas em inglês, **46 são de leitura** e **54 são de montagem**.

- **Mais da metade das perdas de leitura não muda o sentido.** Em 27 linhas, o texto está
  todo lá, e só um espaço, uma pontuação ou um traço saiu diferente ("forwork", "2.-",
  hífen no lugar de travessão).
- **Três padrões explicam 41 das 54 perdas de montagem:** a grade de atributos do Disco
  Elysium (19), as descrições centralizadas do Path of Exile (12) e itens de lista e
  parágrafos seguidos colados (10).

| Causa | Linhas | Jogos | Já era conhecido? |
|---|---:|---|---|
| **Leitura** | **46** | | |
| L1. Texto não lido ou ilegível | 12 | The Big Con 6, Disco 6 | Letreiros: [Problema 5](problemas-em-aberto.md). Texto com desenho por cima: novo |
| L2. Letra trocada | 3 | Disco 2, Path of Exile 1 | |
| L3. Espaço, pontuação ou traço | 27 | Disco 15, Katawa 7, Path of Exile 3, The Big Con 2 | Novo para a medida ([Problema 9](problemas-em-aberto.md), a forma de medir) |
| L4. Ícone ou lixo colado ao texto | 4 | The Big Con 2, Butterfly 1, Disco 1 | [Problema 6](problemas-em-aberto.md) |
| **Montagem** | **54** | | |
| M6. Atributo com número e rótulo em grade | 19 | Disco 19 | Novo |
| M2. Linhas centralizadas de uma descrição coladas | 12 | Path of Exile 12 | Novo, família do [Problema 7](problemas-em-aberto.md) |
| M3. Itens de lista ou parágrafos seguidos colados | 10 | Disco 7, Butterfly 2, Path of Exile 1 | Família do Problema 7 |
| M1. Itens lado a lado colados | 6 | Katawa 2, Path of Exile 2, Butterfly 2 | Família dos Problemas 3 e 4 |
| M4. Última linha curta de uma fala separada | 4 | The Big Con 4 | Novo, família do [Problema 1](problemas-em-aberto.md) |
| M5. Frase ou rótulo quebrado em duas linhas | 2 | Disco 1, Katawa 1 | Família do Problema 1 |
| M7. Palavras espalhadas pelo desenho da placa | 1 | The Big Con 1 | Limite (veja abaixo) |

Por tipo de tela, as perdas ficam assim:

| Tipo | Perdidas | Leitura | Montagem |
|---|---:|---:|---:|
| ficha | 53 | 19 | 34 |
| menu | 28 | 14 | 14 |
| letreiro | 9 | 6 | 3 |
| texto | 6 | 4 | 2 |
| legenda | 4 | 3 | 1 |

## As causas de leitura

**L1. Texto não lido ou ilegível (12).** Metade são os letreiros do The Big Con: o Mallton
Mall em arco, o Cooper's Market em cursiva, o Costume Cave e as duas frases da Crystal Horm.
Isso é o Problema 5, um limite da leitura. A outra metade é do Disco Elysium. Na lista de
pensamentos, cinco itens não foram lidos ou saíram truncados, e quatro deles têm o desenho
do fundo passando por cima das letras (White Mourning, Caustic Echo, Detective Costeau,
Apricot Chewing Gum). A sexta linha é o nome do idioma em russo, que o OCR em inglês não
lê, como esperado.

**L2. Letra trocada (3).** "René" lido como "Tené", "or" como "o", "ACTUAL" como "AQTUAL"
e o zero de "has 0 Charges" como a letra "o".

**L3. Espaço, pontuação ou traço (27).** O texto chega ao tradutor com o mesmo sentido,
mas a medida conta a linha como perdida, porque compara palavra por palavra:
- espaço engolido (8 linhas): "forwork", "waslike", "youmight", "dayever", "consumes7",
  "regenerate1.8life", "speed:80%", "pistols(9mm)";
- espaço antes dos dois-pontos (7): os bônus do inventário do Disco ("Inland Empire : +1"
  virou "Inland Empire: +1");
- travessão "–" lido como hífen "-", ou o contrário (4);
- aspas, reticências e ponto (4): "cold..." com aspa simples, aspa final que sumiu,
  "missed.." e o ponto de "SHAKESPEARE.";
- número de opção (3): "2. -" virou "2.-";
- o "x" de "2560 x 1440" lido como "×" (1).

O mesmo tipo de perda também existe nos 90 prints da referência, então ele não explica a
diferença entre os dois resultados.

**L4. Ícone ou lixo colado ao texto (4).** A bolinha de marcar do Butterfly Soup virou "o"
("ounseen"), o botão do controle virou "*" depois de "quit.", o "NOTES" do caderno colou no
aviso de tarefa e um "A" solto colou na última opção do Disco. É o Problema 6.

## As causas de montagem

**M6. Atributo com número e rótulo em grade (19), só no Disco Elysium.** Na escolha de
arquétipo e no inventário, cada atributo é um número grande em cima de uma sigla (5 sobre
INT, 1 sobre PSY). O app lê os números numa linha ("2 5 4") e as siglas em outra ("INT PSY
FYS MOT"). Os números "1" em caixa preta com letra branca nem são lidos. Na tela de
atributos, "GOOD 4 INTELLECT" sai em três pedaços, sem o número. Os 90 prints não tinham
esse desenho.

**M3. Itens de lista ou parágrafos seguidos colados (10).** Linhas que estão uma embaixo
da outra e saem numa linha só:
- no Butterfly Soup, o título "Screen Motion" com as duas opções embaixo dele, três
  linhas de larguras quase iguais encostadas na borda direita;
- no Disco, "SORT THOUGHTS BY" com as abas embaixo, dois pensamentos seguidos, a fala do
  personagem com o "+5 XP" da linha de baixo e a fala da Klaasje com a primeira opção de
  resposta;
- no Path of Exile, "Sell Items" com "Goodbye", que tem uma linha divisória no meio.

**M2. Linhas centralizadas de uma descrição coladas (12), no Path of Exile.** Nas
descrições de item e de habilidade, cada propriedade é uma linha centralizada de largura
diferente ("Requires Level 17, 21 Dex, 21 Int" e embaixo "+92 to Accuracy Rating"). O app
junta essas linhas como se fossem um parágrafo quebrado. O mesmo acontece com a nota em
itálico embaixo de um efeito. No Stardew Valley, o painel do jogador tem o mesmo desenho
e o mesmo erro.

**M4. Última linha curta de uma fala separada (4).** A fala quebra porque não cabe, e a
última linha tem uma palavra só: "want." no diário do The Big Con, "INFORMATION." no balão
do guia. O app deixa essa palavra sozinha numa linha. O balão "REWIND / FOR / HUMANKIND!",
de três linhas curtas, sai em três pedaços pelo mesmo motivo.

**M1. Itens lado a lado colados (6).** O menu do título do Butterfly Soup é horizontal, e
o OCR entrega os cinco itens numa caixa só ("New Game Load Game Settings About Quit"). É o
caso da barra de menu numa caixa só (Problema 4), mas a regra dela não dispara, porque a
tela não tem fala para servir de medida do espaço normal. As abas do Katawa Shoujo ("Act 1 Emi Hanako...")
saem numa linha só e ainda levam junto o primeiro item da lista embaixo delas.
"Completion: 100%" cola no "Return", que está no outro canto da mesma linha. No Path of
Exile, um tópico da coluna da esquerda cola na opção da direita que está na mesma altura.

**M5. Frase ou rótulo quebrado em duas linhas (2).** A dica longa do Disco ("TAP Q OR L TO
SEAMLESSLY SWITCH / LANGUAGES IN GAME") sai em duas linhas, e uma fala do Katawa Shoujo é
cortada antes da última frase.

**M7. Palavras espalhadas pelo desenho da placa (1).** Na placa do trem, "THIS" e "TO" ficam
de um lado da locomotiva e "WAY" e "TRAIN" do outro. Nenhuma regra de montagem deve tentar
juntar isso.

## O espanhol

Das 13 linhas perdidas no Stardew Valley:
- **4 são a última linha curta de uma fala** (M4): "llegada.", "quieres.",
  "conversación!" e a assinatura "-Alcalde Lewis»". É o mesmo erro do The Big Con.
- **4 são rótulos de formulário em duas linhas** (M5): "Tu cosa / favorita", "Tu animal /
  preferido", "Color de / ojos:" e "Color de / pelo:". O "Nombre de / la granja", do mesmo
  formulário, saiu inteiro.
- **2 são letra trocada** (L2): o "¡" lido como "i" em "iHas recibido" e "total" lido como
  "totol". O "¡" virou "i" também na fala do Elliott ("iAh!"), que conta como linha curta
  porque também saiu partida. É um erro de leitura próprio do espanhol, que o inglês não
  tinha como mostrar.
- As outras 3 são uma de cada: espaço a mais ("Spanish Boost"), o painel centralizado do
  jogador (M2) e o nome do personagem colado na data, que está na mesma altura (M1).

## O que isso diz para as correções (fase 4.3)

A regra do plano é que **um erro que aparece num jogo só não vira regra**. Contando o
espanhol, os candidatos ficam nesta ordem:

| Ordem | Padrão | Linhas | Jogos |
|---|---|---:|---|
| 1 | M3. Itens de lista ou parágrafos seguidos colados | 10 | Disco, Butterfly Soup, Path of Exile |
| 2 | M4 e M5. Fala ou rótulo quebrado que não é juntado | 14 | The Big Con, Stardew, Disco, Katawa |
| 3 | M2. Linhas centralizadas de uma descrição | 13 | Path of Exile, Stardew |
| 4 | M1. Itens lado a lado colados | 7 | Katawa, Path of Exile, Butterfly Soup, Stardew |

O menu do Butterfly Soup estava em M3 na primeira versão desta tabela. As caixas do OCR
mostraram que ele é horizontal, e ele passou para M1.

Ficam de fora por enquanto:
- **M6, a grade de atributos (19 linhas),** só aparece no Disco Elysium. É o maior bloco,
  mas é de um jogo só. A rodada 2 tem outros RPGs (Pillars of Eternity, Baldur's Gate 3,
  Skyrim), mas ela só pode ser olhada depois das correções.
- **Os letreiros estilizados (L1 e M7)** são limite da leitura, o Problema 5.
- **Espaço e pontuação (L3)** vêm do próprio OCR. Uma medida nova, que não contasse essas
  diferenças, ajudaria a separar o que atrapalha a tradução do que não atrapalha. Pela
  regra da régua, ela entraria ao lado das medidas atuais, sem mudar nenhuma delas.

Cada correção segue os passos da fase 4.3: achar um caso reproduzível, medir o sinal nos
140 prints (os 90 e os 50 da validação) antes de escrever a regra, comparar com a `main`
nas duas leituras e olhar o resultado por tipo de tela. Ela também não pode estragar o
espanhol.

## A primeira correção: o vão maior entre itens

*Feita em 24/11/2026 no branch `regra-passo-grande`, a partir do candidato 1 (M3).*

**O que os casos tinham em comum.** Entre itens de lista e entre parágrafos seguidos, o
passo vertical (do topo de uma linha ao topo da seguinte) é maior que entre as linhas de
um mesmo parágrafo. Na fala do Disco Elysium, as linhas estão a 31 px e o "+5 XP" a 44 px.
No Path of Exile, "Sell Items" e "Goodbye" estão a 42 px, contra 20 px dentro de cada caixa
de opções. O app não usava esse sinal: um vão só quebra a linha acima de 0,8 altura de
letra, e nesses prints ele fica entre 0,5 e 0,7.

**O sinal, medido antes da regra.** Em cada bloco, o passo de cada par de linhas foi
comparado com o passo típico do bloco, nos 140 prints e nas duas leituras (script
`laboratorios/validacao/passos_grandes.py`). Nenhuma emenda de linha do gabarito tem passo
acima de **1,21** do típico. As quebras que o app perdia ficam entre **1,26 e 1,78**.

**A regra** (`_quebras_por_passo`, em `paragrafos.py`). Num bloco, o passo típico é a
mediana dos passos entre fileiras diferentes, ignorando linhas da mesma altura. Um passo
de **1,35 vez o típico** ou mais quebra o parágrafo.

O limite fica no meio de um platô estreito:
- com 1,25, aparecem dois ganhos e a primeira quebra errada (Caves of Qud, no EasyOCR);
- entre 1,3 e 1,4, o resultado é o mesmo;
- com 1,45, os ganhos dos prints novos começam a sumir.

Uma segunda versão aceitava 1,2 quando a linha de cima termina frase. Ela só ganhava uma
linha a mais, num print só, e ficou de fora.

**O resultado, sem nenhuma perda e nenhuma quebra a mais:**

| Leitura | Linhas inteiras | Quebras certas |
|---|---:|---:|
| RapidOCR, 90 prints | +2 | +1 |
| RapidOCR, 60 prints novos | +5 | +3 |
| EasyOCR, 90 prints | +3 | +5 |
| EasyOCR, 60 prints novos | +1 | +2 |

No benchmark do app, as letras não mudaram em nenhum print:
- 90 prints: linhas inteiras de 539 para 541;
- validação: de 190 para 195 (65,5% → 67,2%);
- espanhol: igual.

Entraram três casos simulados nos testes, com as proporções dos prints reais. Dois falham
com o código da `main` e passam com a regra, e o terceiro garante que um passo de 1,19 não
quebra. Agora são 109 testes.

**O que sobrou do M3:**
- "Screen Motion" e as duas opções do Butterfly Soup têm o mesmo passo. O problema é a
  regra de menu, que exige uma linha bem mais curta que as outras, um limite conhecido.
- "SORT THOUGHTS BY" com as abas embaixo, no Disco, também tem o mesmo passo. Lido junto,
  faz sentido como frase.
- A fala da Klaasje com a primeira opção de resposta tem passo 1,26, abaixo do limite.

**Uma armadilha do laboratório.** O modo `cinza2` do `cache_motores.py` chama o motor de
OCR do app, que desde 16/11 é o RapidOCR em inglês. Os 90 prints têm uma leitura `cinza2`
antiga, feita com o EasyOCR. Nos prints novos, a leitura do EasyOCR veio do modo
`easyocr_cpu`.

## O diagnóstico dos candidatos 2 e 3

*Feito em 24/11/2026. O script `laboratorios/validacao/por_que_quebrou.py` mostra, para
cada emenda do gabarito que o app quebra, quais condições pediram a quebra.*

O candidato 2 (fala ou rótulo quebrado que não é juntado) tinha **duas causas diferentes**.

**A última palavra da fala, sozinha na linha.** "llegada.", "quieres.", "conversación!" e
"want." O app só reconhece que a frase continua quando a linha de baixo tem duas palavras
ou mais. A trava existe para não juntar tópicos de uma palavra só ("duties", "rules" no
Morrowind). Fora desse caminho, o app testa se a palavra "caberia" na linha de cima. Ele
mede isso pela borda do print, e não pela da caixa de diálogo, então a palavra cabe e a
linha quebra.

**A frase que termina no fim da linha.** O app quebra sempre que uma linha termina com
ponto e a de baixo começa com maiúscula. A regra foi feita para avisos seguidos do
Morrowind ("...increased to 66." / "Item does not have enough charge."), mas também corta
parágrafos em que uma frase acaba bem no fim da linha. Isso acontece em 7 lugares, de 5
jogos (Katawa Shoujo, Fallout, Morrowind, Night in the Woods e Caves of Qud), e 6 deles
estão nos 90 prints. É um erro antigo que a validação ajudou a enxergar.

Medi duas correções nos 140 prints e nas duas leituras (`sinais_fala.py`):

| Correção | Ganhos | Perdas |
|---|---:|---:|
| **F1.** Palavra só, com minúscula e fim de frase, conta como continuação | 5 | 0 |
| **F2.** Fim de sentença só quebra junto com outra condição | 11 | 10 |

A F2 quase empata, e as perdas caem em telas que hoje saem certas. O fim de frase separa tanto avisos, títulos e respostas curtas ("Yeah, of
course." / "Why?") quanto corta parágrafos, e nenhuma condição que o app já tem distingue
uma coisa da outra.

O candidato 3 (descrições centralizadas) também não tem solução simples. A ideia era
medir o "caberia" pela linha mais larga do grupo centralizado, e não pela borda do print
(`sinais_centro.py`). Ela ganha 1 ou 2 quebras no Path of Exile e perde 2 nos cartazes do
Night in the Woods, que são frases centralizadas quebradas de propósito pelo desenho. As
descrições do Path of Exile ainda vêm em versalete, e o OCR lê tudo em maiúscula, então a
maiúscula também não ajuda.

## A segunda correção: a última palavra da fala

*Feita em 24/11/2026 no branch `regra-palavra-final`.*

A F1 entrou em `_continua_frase`: uma linha de uma palavra só também é continuação quando
começa com minúscula e termina a frase (`PALAVRA_FINAL`). Um tópico de menu de uma palavra
não tem pontuação no fim, então continua separado.

| Conjunto | Linhas inteiras | Quebras a mais |
|---|---|---|
| 90 prints | 541 → 541 | 69 → 69 |
| Validação | 195 → 196 | 32 → 31 |
| Espanhol | 8 → 10 (38% → 48%) | 17 → 14 |

As letras não mudaram, e nada mudou nos 90 prints, nas duas leituras. Na fala do Elliott,
a linha continua perdida porque o "¡" foi lido como "i". Entrou um caso nos testes, com a
fala do Stardew numa caixa mais estreita que a tela, que falha na `main` e passa com a
correção. Agora são 110 testes.

**Ficam para a consulta às outras IAs:** a frase que termina no fim da linha (F2) e as
descrições centralizadas. Os dois têm casos reais em vários jogos, contraexemplos claros e
nenhum sinal simples que os separe.

## A terceira correção: as linhas coladas (com as outras IAs)

*Feita em 24/11/2026 no branch `regra-fim-de-frase`, a partir do problema 9 do arquivo de
perguntas, respondido por ChatGPT, Grok, DeepSeek, Mistral e Qwen.*

As cinco propostas mantêm a regra do fim de frase e abrem uma exceção quando o par tem
cara de parágrafo. Cada uma virou uma variante do código
(`laboratorios/validacao/variantes_p9.py`) e foi medida nos 140 prints, nas duas leituras:

| Proposta | A regra não quebra quando… | Ganhos | Perdas |
|---|---|---:|---:|
| ChatGPT | o passo é até 1,16 da altura média das duas linhas, e as alturas diferem menos de 1,4x | 7 | 0 |
| Grok | a linha tem 14 h ou mais e o passo é menor que 1,35 h, salvo par centralizado longe da borda | 7 | 2 |
| Grok, sem a cláusula da borda | | 5 | 0 |
| DeepSeek | a linha tem 14 h ou mais e não é título nem resposta centralizada | 7 | 4 |
| **Mistral** | **o vão entre as caixas é menor que 0,18 h, e as alturas diferem menos de 1,4x** | **7** | **0** |
| Qwen | a linha tem 15 h ou mais e termina a até 2 h da margem | 7 | 6 |

O que separou as propostas foi o título do cartaz da festa do Night in the Woods. Na
leitura do EasyOCR, o passo dele é 1,23 h e a largura, 18 h, então quem usa a largura ou o
passo o toma por prosa. O vão entre as caixas, não: 0,24 h. Nos pares em que o fim de
frase é a única quebra, as emendas têm vão de -0,20 a 0,10 h, e as quebras, de 0,24 a
0,57 h. O limite do Mistral, 0,18, fica quase no meio. O ChatGPT achou o mesmo sinal por
outra conta, mas com o limite a 0,01 da legenda do Fallout.

Um dado que eu não mandei pesou contra duas propostas. Na resposta do Katawa Shoujo, o app
calcula a margem do painel em 1566 px, e eu informei a largura do print (1852 px). O Grok
pediu a borda do print, e foi medido com ela; o DeepSeek pediu a margem do painel.

Entrou a regra do Mistral (`_linhas_coladas`, em `paragrafos.py`), com os limiares dele.

| Conjunto | Linhas inteiras | Quebras a mais |
|---|---|---|
| 90 prints | 541 → 546 | 69 → 63 |
| Validação | 196 → 197 | 31 → 30 |
| Espanhol | igual | igual |

As letras não mudaram, e nenhuma linha se perdeu nas duas leituras. Os 5 jogos com o erro
saíram certos. Entraram dois casos nos testes: um parágrafo com linhas coladas, que falha
na `main`, e um título de letra 1,45x maior colado ao subtítulo, que falha se a trava de
fonte for tirada. Agora são 112 testes.

## A quarta correção: as descrições centralizadas (com as outras IAs)

*Feita em 24/11/2026 no branch `regra-descricao-centralizada`, a partir do problema 10,
respondido pelas mesmas cinco IAs.*

As cinco chegaram à mesma ideia: propriedade de item não termina em ponto, frase de
descrição termina, e uma trava de "linha cheia" protege a frase quebrada no meio. As
propostas viraram variantes (`laboratorios/validacao/variantes_p10.py`) e foram medidas
nos 140 prints, nas duas leituras:

| Proposta | Ganhos | Perdas |
|---|---:|---:|
| Mistral | 19 | 3 |
| Grok | 19 | 4 |
| Qwen | 19 | 6 |
| ChatGPT, como escrito | 17 | 19 |
| DeepSeek, como escrito | 27 | 23 |

O ChatGPT e o DeepSeek definem o grupo centralizado só pelo centro das linhas, e um
parágrafo comum, alinhado à esquerda, também tem os centros perto. Com a prova de
centralização do Grok (a margem esquerda varia em algum par), as perdas caem para 3 e 6.

As perdas que sobraram vinham de dois casos que nenhuma IA tratou:
- uma frase centralizada que continua depois de vírgula, com nome próprio embaixo
  ("...Funeral Parlor," / "Cattrosser & Cattrosser Attorneys,", no cartaz do Night in the
  Woods): **vírgula no fim da linha não quebra**;
- um rótulo curto quebrado em duas linhas, sem pontuação ("POINTS / TO GO", no Fallout):
  **o grupo precisa de alguma linha com 8 alturas de letra ou mais**. Qualquer valor de 6
  a 9,7 dá o mesmo resultado.

Com as duas travas, nenhuma das três melhores perde linha nas duas leituras:

| Proposta com as travas | Ganhos | Quebras a mais |
|---|---:|---:|
| Mistral | 18 | 2 |
| Grok | 19 | 5 |
| ChatGPT (só em grupo centralizado) | 17 | 3 |

A do Grok ganha o painel do Stardew inteiro, mas põe mais quebras erradas (um menu do Disco
Elysium e o Path of Exile no EasyOCR). Entrou a estrutura do Mistral
(`_quebras_centralizadas`, em `paragrafos.py`), com a prova de centralização do Grok e as
duas travas. As travas foram escolhidas depois de ver os resultados; a rodada 2 é que vai
dizer se a regra generaliza.

Ficou um erro no painel do Stardew: "Granja SpanishBoost" e "Fondos actuales: 280o"
continuam juntas. As duas são cheias (9,4 e 9,7 alturas) e o vão entre elas é 0,43 altura,
logo abaixo do limite de 0,45. Baixar o limite só por esse caso seria ajustar a regra a
um print.

| Conjunto | Linhas inteiras | Quebras certas | Quebras a mais |
|---|---|---|---|
| 90 prints | igual (546) | igual | igual |
| Validação | 197 → 207 | 289 → 297 | igual |
| Espanhol | igual | 19 → 20 | igual |

As letras não mudaram, e nenhuma linha se perdeu nas duas leituras. Na leitura do
EasyOCR, apareceram 2 quebras a mais, e as duas vêm de erro de leitura dele: um "wielding"
lido com maiúscula e um ponto final que sumiu. Entraram três casos nos testes: uma
descrição do Path of Exile (falha na `main`), um cartaz com vírgula (falha sem a trava da
vírgula) e o rótulo "POINTS / TO GO" (falha sem a trava da largura). Agora são 115 testes.

**Desde a medida da validação, quatro correções:** nos 90 prints, as linhas inteiras foram
de 539 para 546; na validação, de 190 para 207 (65,5% para 71,4%); no espanhol, de 8 para
10. Nenhuma perdeu linha nas duas leituras.

## O M1, itens lado a lado: diagnóstico sem regra segura

*Feito em 25/11/2026 depois da quarta correção. Nenhuma regra entrou; o menu numa caixa só
foi às outras IAs como problema 11.*

As 7 linhas do M1 (6 na validação e 1 no espanhol) continuam perdidas. Olhando as caixas e
os prints, elas vêm de cinco jeitos diferentes, e quase todos aparecem num jogo só:

| Caso | Linhas | O que acontece | Jogos com o padrão |
|---|---:|---|---|
| Menu do título do Butterfly Soup | 2 | O OCR lê os cinco itens numa caixa só, e dois têm duas palavras ("New Game", "Load Game") | Butterfly Soup e Katawa Shoujo |
| Abas do Katawa Shoujo | 1 | Também numa caixa só: "Act 1 Emi Hanako Lilly Rin Shizune" | (o mesmo padrão) |
| "Completion: 100%" e "Return" (Katawa) | 1 | Duas caixas na mesma linha, a 7,3 alturas uma da outra | Katawa Shoujo |
| Path of Exile | 2 | Um texto apagado no fundo ("AILITH, FIRST OF THE KEEPERS") fica entre as duas colunas e impede o corte | Path of Exile |
| Stardew | 1 | O nome do personagem e a data na mesma linha, a 2,1 alturas | Stardew Valley |

**O menu numa caixa só (Butterfly e Katawa).** É o único padrão de dois jogos. A regra da
barra de menu (Problema 4) não pega: ela corta uma palavra por item e mede o espaço normal
pela fala do print, e essas telas não têm fala. Testei uma versão que usa a própria caixa
como medida: os espaços entre as palavras, medidos na tinta, formam dois grupos (dentro do
item e entre os itens), com um salto de 2,5x ou mais entre eles. A regra também pede 3 ou
mais espaços grandes, parecidos entre si, e itens de até 2 palavras. Nos 140 prints, em
todos os limiares testados, ela não cortou nenhuma outra caixa (`laboratorios/validacao/barra_de_itens.py`).

O problema é medir o espaço no Butterfly. O menu é lilás claro sobre fundo branco, com
traços do desenho passando atrás das letras. Com a medida de tinta do app (20 níveis de
cinza, 3 pixels por coluna), os traços enchem os espaços e a medida falha. Das 15
combinações de limiar testadas, só 3 acertam os dois prints: tinta de 45 a 50 níveis com
coluna de 12% a 15% da altura. Um limiar relativo ao contraste da caixa acerta o
Butterfly e perde o Katawa, porque a aba escolhida é preta e as outras são cinza. Uma
janela tão estreita, ajustada em dois prints, é a definição de regra que não generaliza.
Com a medida do app, a regra só pega o Katawa: 1 linha, de um jogo.

**Duas caixas longe uma da outra.** O vão não separa os casos. O gabarito junta pares de
configuração como "VOICE OVER MODE | Psychological" (5,6 alturas, Disco Elysium),
"Default Mouse Cursor | Regular" (4,8, Path of Exile) e o cabeçalho "Spells | Cost/Chance"
(8,0, Morrowind). E separa "Completion: 100% | Return" (7,3, Katawa) e "The Keepers |
Purchase Graft" (12,7, Path of Exile). O alinhamento com as linhas vizinhas também não
separa: "Return" e "Psychological" estão soltos do mesmo jeito. Medido com
`laboratorios/validacao/sinais_lado_a_lado.py`. Isso confirma uma medida antiga: o vão
sozinho não separa itens de rótulo e valor.

**Uma medida que não olha a tinta.** O reconhecedor do RapidOCR é CTC: cada letra sai de
uma faixa de colunas da imagem. A versão 3.10 usa esse alinhamento para dar uma caixa a
cada palavra (`return_word_box=True`), quase sem custo de tempo (15 ms por print, medidos
depois; ver a quinta correção). Por ela, o menu do Butterfly sai limpo, com o
desenho atrás: espaços de 0,25 altura dentro do item e de 0,75 entre os itens. Mas a
medida é grossa. Os espaços vêm em degraus, 0,00 aparece em texto comum, e a mesma
palavra muda 11 px entre a leitura em cores e a em cinza. No texto comum dos 150 prints,
a mediana do espaço é 0,28 altura e o p99 é 0,63, então os espaços entre os itens (0,48 a
0,79) não se separam por um limite fixo. A regra do salto, com os espaços pequenos
levados a no mínimo 0,17 altura, só corta o Butterfly e o Katawa nos 150 prints; com
0,08, corta também uma legenda do Night in the Woods, um nome do Disco Elysium e uma
propriedade do Path of Exile. Medido com `laboratorios/quebras/cache_palavras.py` e
`laboratorios/validacao/espacos_por_palavra.py`.

**Conclusão.** Nenhuma regra entrou. São 7 linhas (cerca de 2% da validação), em cinco
mecanismos, e o único que se repete depende de limiares escolhidos olhando os dois
exemplos. O menu numa caixa só foi para as outras IAs como problema 11 (25/11), com as
duas medidas, a da tinta e a das palavras. Se nada seguro vier, ele espera a rodada 2:
com outro jogo com o mesmo menu, a regra pode ser medida de novo com mais exemplos. (Veio uma
regra segura: ver a quinta correção, abaixo.)

## A quinta correção: o menu numa caixa só (com as outras IAs)

*Feita em 25/11/2026 no branch `regra-menu-numa-caixa`, a partir do problema 11. Responderam
o Grok, o Mistral e o Qwen; o ChatGPT e o DeepSeek comentaram outro texto.*

As três propostas usam as palavras do reconhecedor e a própria caixa como régua: os
espaços se dividem em pequenos (dentro do item) e grandes (entre os itens). Medidas nos
150 prints (`laboratorios/validacao/variantes_p11.py`), contra o app de hoje:

| Proposta | Ganhos | Perdas | Quebras a mais |
|---|---:|---:|---:|
| Mistral: piso de 0,15 altura, salto de 2,2x, 3+ grandes regulares, itens com maiúscula | 3 | 0 | 0 |
| Qwen: limites fixos (grande acima de 0,45, pequeno até 0,30) | 3 | 2 | 10 |
| Grok: salto pela diferença (0,15) e mediana dos grandes de 0,50 | 3 | 6 | 61 |

As três ganham as mesmas linhas: "New Game" e "Load Game" no Butterfly Soup e "Act 1" no
Katawa Shoujo. O que separou as propostas foi uma trava de forma, e não de medida. O Grok
e o Qwen aceitam item que começa com minúscula. Na fonte de largura fixa do Caves of Qud,
os espaços de uma frase alternam 0,35 e 0,5 altura, e "Welcome to the Caves of Qud
tutorial." virava cinco itens. O Mistral exige que cada item comece com letra que não é
minúscula; sem essa trava, a regra dele também corta uma ficha do EVE Online.

**Se a regra depende dos limites.** Varri o piso (0,08 a 0,25), o salto (1,8 a 2,8) e a
regularidade (1,5 a 2,5): 48 das 140 combinações cortam só os dois menus, e certo. Pela
tinta, eram 3 de 15. Os valores do Mistral ficam dentro dessa região, mas a regularidade
de 1,7 estava colada no Katawa (1,65x). Com os 2x do Grok, nenhuma combinação da região
corta outra caixa. Entrou a regra do Mistral com a regularidade do Grok
(`_menu_pelas_palavras`, em `paragrafos.py`). O motor de OCR (`ocr_engine.py`) passou a
pedir as palavras e a entregá-las como 4º elemento de cada caixa, casadas pelo texto,
porque a lista do RapidOCR pula as caixas sem palavra.

| Conjunto | Linhas inteiras | Quebras certas | Quebras a mais |
|---|---|---|---|
| 90 prints | igual (546) | igual | igual |
| Validação | 207 → 210 | 297 → 307 | igual |
| Espanhol | igual (10) | igual | igual |

As letras não mudaram. Na leitura do EasyOCR, que não tem palavras, nada muda. Entraram 11
testes (`tests/test_menu_palavras.py`): os dois menus, seis casos que não podem ser
cortados e o casamento das palavras com as caixas. Agora são 126 testes.

**O tempo.** A primeira medida, no cache, dizia que pedir as palavras não custava nada
(0,79 s por print com elas e 0,91 s sem). Ela estava viciada: lia cada print duas vezes,
sempre na mesma ordem, e a segunda leitura sai favorecida. O benchmark desta rodada deu o
contrário (0,92 s contra 0,81 s ontem), mas compara dias diferentes. Com a mesma máquina,
na mesma rodada e a ordem alternada (30 prints, duas vezes cada), a diferença é de 15 ms
por print, com a mediana até menor: dentro do ruído.

Ficam 4 linhas do M1, de três mecanismos de um jogo só cada: "Completion: 100%" e
"Return" (Katawa), o texto apagado entre as colunas do Path of Exile e o nome com a data
no Stardew.

**Desde a medida da validação, cinco correções:** nos 90 prints, as linhas inteiras foram
de 539 para 546; na validação, de 190 para 210 (65,5% para 72,4%); no espanhol, de 8 para
10. Nenhuma perdeu linha nas duas leituras.

## O que ficou em aberto antes do congelamento (25/11/2026)

Depois das cinco correções, revisei tudo o que ainda se perde nos 150 prints, para fazer
uma última rodada de perguntas às outras IAs antes de congelar o código para a rodada 2
(`laboratorios/validacao/abertas.py`). São 206 linhas: 115 nos 90 prints, 80 na validação
e 11 no espanhol.

Na validação e no espanhol, pela causa da classificação de 24/11:

| Causa | Linhas | Jogos |
|---|---:|---|
| L1. Texto não lido | 12 | The Big Con 6, Disco Elysium 6 |
| L2. Letra trocada | 5 | Disco Elysium 2, Stardew 2, Path of Exile 1 |
| L3. Espaço ou pontuação | 28 | Disco Elysium 15, Katawa 7, Path of Exile 3, The Big Con 2, Stardew 1 |
| L4. Ícone colado | 4 | The Big Con 2, Butterfly Soup 1, Disco Elysium 1 |
| M1. Itens lado a lado | 4 | Path of Exile 2, Katawa 1, Stardew 1 |
| M2. Descrição centralizada | 3 | Path of Exile 2, Stardew 1 |
| M3. Itens de lista colados | 5 | Disco Elysium 3, Butterfly Soup 2 |
| M4. Última linha curta separada | 5 | The Big Con 3, Stardew 2 |
| M5. Rótulo quebrado em duas linhas | 5 | Stardew 4, Disco Elysium 1 |
| M6. Grade de atributos | 19 | Disco Elysium 19 |
| M7. Palavras espalhadas pela placa | 1 | The Big Con 1 |

Nos 90 prints, 67 das 115 linhas faltam palavras (leitura, sobretudo nas tabelas miúdas do
EVE Online), 31 saem com sobra e 17 saem partidas.

Juntando os 150 prints, quatro padrões se repetem em vários jogos e foram para as IAs como
problemas 12 a 15:

| Problema | Ocorrências | Jogos |
|---|---|---:|
| 12. O OCR engole o espaço entre duas palavras ("youmight", "CONSUMES7") | 33 espaços, 31 linhas | 10 |
| 13. Duas caixas na mesma linha: dois itens, ou rótulo e valor? | 7 linhas, contra 121 pares que têm de continuar juntos | 6 |
| 14. Ícone lido como símbolo e colado à linha ("+", "8", "≡", ">") | 16 linhas | 6 |
| 15. Frase ou rótulo quebrado em linhas curtas e coladas ("REWIND / FOR / HUMANKIND!") | 14 pares, contra 56 que só o "caberia" separa | 7 |

Os dados vêm de três medidas novas: as letras do reconhecedor
(`laboratorios/quebras/cache_letras.py`, `laboratorios/validacao/espacos_engolidos.py`), as
linhas com caixas distantes e a vizinhança delas (`pares_na_linha.py`) e os pares de linhas
coladas, com o motivo de cada quebra (`pares_colados.py`). Duas descobertas mudaram a
classificação de 24/11:
- **O M1 não era de um jogo só.** Contando os 90 prints, as duas caixas distantes que
  deviam se separar aparecem também no EVE Online, no Caves of Qud e no Fallout.
- **O espaço engolido é a maior causa que se repete.** Ele estava espalhado por L3 e M5, e
  aparece em 10 jogos.

Ficaram de fora: a grade do Disco Elysium (19 linhas, um jogo só); o texto não lido (12
linhas, leitura nos letreiros tortos do The Big Con e num menu do Disco); as colunas
misturadas da reputação do Caves of Qud (um jogo só); o "¡" lido como "i" no espanhol
(pequeno, dá para corrigir sem as IAs); e o travessão lido como hífen e as aspas trocadas,
que quase não mudam a tradução.

## A sexta correção: o espaço engolido (com as outras IAs)

*Feita em 25/11/2026 no branch `regra-espaco-engolido`, a partir do problema 12, respondido
pelas cinco IAs.*

As propostas foram medidas nos 150 prints (`laboratorios/validacao/variantes_p12.py`),
sobre as letras do reconhecedor e a tinta, contando cada espaço inserido contra o gabarito
e as linhas inteiras:

| Proposta | Espaços certos | Espaços errados | Linhas inteiras |
|---|---:|---:|---|
| Grok: vão de tinta dominante, passo fora do normal com tinta, palavra colada a número | 22 | 686 | +3, −167 |
| Qwen: tinta acima de 0,15 altura ou passo 1,5x a mediana | 27 | 2.663 | +3, −424 |
| DeepSeek: passo 1,15x o maior do resto da palavra, ou tinta com passo perto dele | 30 | 2.918 | +0, −545 |
| Mistral: gatilho pelo passo, decisão pela releitura do trecho ampliado | 4 | 1 | +1, −1 |
| ChatGPT: candidatos pela geometria, decisão pela probabilidade do CTC (limite 0) | 5 | 0 | +2, −0 |
| ChatGPT, limite −1 | 13 | 0 | +6, −0 |
| ChatGPT, limite −2 | 19 | 0 | +8, −1 |

As regras geométricas cortaram palavras como "New", "Investor" e "removed": em muitas
fontes, o vão normal entre duas letras passa de 0,15 altura. O único sinal que separou foi
o do próprio reconhecedor. Para cada candidato, a diferença de log-probabilidade entre o
texto com e sem o espaço ficou em −2,0 ou menos nos 4.564 errados, e com mediana −0,4 nos
certos.

Entrou a proposta do ChatGPT (`espacos.py`), numa versão barata. Em vez do algoritmo
forward na linha inteira, ela olha a margem do espaço, log p(espaço) − log p(melhor
classe), na melhor coluna do CTC entre as duas letras. Com o limite −1, deu o mesmo
resultado que o forward. Os candidatos são os do ChatGPT: passo 1,15 vez a mediana dos
passos da palavra, ou um vão de tinta de 0,20 altura. Ficam fora o apóstrofo, o hífen, o
"×", a "/", dígito com dígito, o separador decimal e a escrita sem espaço. O limite −1
foi escolhido olhando os resultados; o limite natural, 0, ganha 2 linhas.

No laboratório, a conta custava 435 ms por print, porque relia cada caixa. No app, as
probabilidades são as da leitura principal: o motor de OCR envolve o reconhecedor do
RapidOCR (`GravadorDoReconhecedor`) e guarda cada lote antes de o RapidOCR descartá-lo. Não
há segunda chamada, e o tempo ficou dentro do ruído. A posição de cada letra sai da coluna
do CTC, como o RapidOCR faz nas caixas por letra, sem pedir essas caixas: as caixas por
palavra do problema 11 continuam iguais.

No benchmark real, que lê as caixas em lotes como o app, o resultado foi melhor que no
laboratório:

| Conjunto | Linhas inteiras | Letras | Quebras |
|---|---|---|---|
| 90 prints | 546 → 550 | 95,79% → 95,85% | iguais |
| Validação | 210 → 213 | 91,33% → 91,35% | iguais |
| Espanhol | igual (10) | igual | iguais |

O app inseriu 17 espaços. Quinze estão certos ou deixam o texto mais perto do gabarito:
"they sound", "Press to", "day ever", "ACE'S LOW", "Archaeology I", "& Boosters",
"NPC 2,500" e "PISTOLS (9MM)". Os outros dois caem em texto que já estava errado: o OCR
leu "Agily" no lugar de "Agility", e o app separou "Agil y"; e "★New!★" virou "★New! ★".
Nenhuma linha se perdeu. Ficam de fora os casos sem sinal nenhum, como "Rest easy." (Mass
Effect) e "WHITE MOURNING" (Disco Elysium). Entraram 9 testes (`tests/test_espacos.py`);
agora são 135.

**Desde a medida da validação, seis correções:** nos 90 prints, as linhas inteiras foram
de 539 para 550; na validação, de 190 para 213 (65,5% para 73,4%); no espanhol, de 8 para
10. Nenhuma perdeu linha.

## A sétima correção: duas caixas na mesma linha (em duas rodadas com as outras IAs)

*Feita em 25/11/2026 no branch `regra-itens-distantes`, a partir do problema 13: duas
caixas na mesma linha, longe uma da outra, são dois itens ou rótulo e valor?*

Na 1ª rodada, as cinco IAs (o Qwen deu duas respostas) propuseram o mesmo caminho: contar,
nas colunas em volta, quantas linhas têm par no mesmo y. Medidas nas quatro leituras
(`laboratorios/validacao/variantes_p13.py`), todas perderam linhas:

| Proposta, 1ª rodada | Ganhos | Perdas | Quebras a mais |
|---|---:|---:|---:|
| Grok | 13 | 5 | 60 |
| Qwen, 2ª resposta | 11 | 18 | 59 |
| ChatGPT | 9 | 22 | 63 |
| Mistral | 9 | 53 | 97 |
| DeepSeek | 13 | 54 | 161 |
| Qwen, 1ª resposta | 5 | 76 | 121 |

Os erros caíam em cinco desenhos que a pergunta não mostrava
(`laboratorios/validacao/erros_p13.py`):
- **E1:** o nome e o nível das técnicas do Immortal Clan ("Kunlun Seal | Lv.10"), em 11
  prints;
- **E2:** uma opção com o valor escrito ("Default Mouse Cursor | Regular");
- **E3:** o título de uma dica com o nível ("Dream of Realms | lv5");
- **E4:** os cabeçalhos de tabela do EVE Online;
- **E5:** frases que o EasyOCR lê em pedaços, com vão de cerca de 1 altura.

Na 2ª rodada, a pergunta mostrou esses erros com as coordenadas
(`laboratorios/validacao/variantes_p13b.py`):

| Proposta, 2ª rodada | Ganhos | Perdas | Quebras a mais |
|---|---:|---:|---:|
| Grok | 7 | 1 | 9 |
| Qwen | 7 | 1 | 11 |
| ChatGPT | 3 | 0 | 0 |
| DeepSeek | 9 | 8 | 28 |
| Mistral | 0 | 0 | 0 |

Todas adotaram as mesmas três travas: um vão mínimo de cerca de 2 alturas (acaba com E5),
um valor curto como "Lv.10" contado como número (E1 e E3) e o cabeçalho que o app já
marca (E4). A proposta do Mistral não mudou nada: na regra dele, a barra de abas do
Katawa e o título da janela do Path of Exile atravessam as duas colunas e bloqueiam a
separação.

Entrou a regra do Grok (`_pares_distantes` e `_itens_distantes`, em `paragrafos.py`):
- **Quais linhas entram:** só a linha que, cortada nos vãos de 2,1 alturas, dá
  exatamente dois segmentos.
- **Junta:** valor curto; o cabeçalho de tabela; a tabela de rótulo e valor (pares em 2+
  linhas, rótulos fechando à direita e valores abrindo à esquerda); e o rótulo de 2+
  palavras com um valor de uma palavra, sem par em outra linha.
- **Separa:**
  - duas listas alinhadas à esquerda (Caves of Qud);
  - duas colunas com pares em até metade das linhas (Path of Exile);
  - a caixa sozinha ao lado de uma coluna (o "Return" do Katawa);
  - duas caixas sozinhas quando a maior é frase de 4+ palavras com número (Stardew).

As colunas são encadeadas pela mesma borda (1 altura) com passo de até 3 alturas.

| Conjunto | Linhas inteiras | Quebras certas | Quebras a mais |
|---|---|---|---|
| 90 prints | 550 → 550 | 685 → 687 | 63 → 65 |
| Validação | 213 → 216 | 307 → 309 | 30 → 32 |
| Espanhol | 10 → 11 | igual | 14 → 15 |

As letras não mudaram. A única linha perdida é da loja do Immortal Clan, onde o gabarito
junta "Lasts 30 days Cat Ledger". No print, são dois itens: o texto embaixo do botão de
investir e o rótulo de outro ícone, no canto. O mesmo gabarito junta "Become Investor
Enjoy Privileges", dois títulos sobre ícones diferentes. Pela regra de uma linha por
item, esse gabarito precisa ser relido; fica para a releitura dos gabaritos antes da
rodada 2. (Relido em 25/11: veja [A releitura dos gabaritos](#a-releitura-dos-gabaritos-25112026).)

Entraram 5 casos nos testes: a galeria com o botão no canto, duas listas com uma placa no
meio, o nome com a data, a opção com o valor escrito e o nome da técnica com o nível.
Agora são 140 testes.

## A oitava correção: o ícone lido como símbolo (com as outras IAs)

*Feita em 25/11/2026 no branch `regra-icones-colados`, a partir do problema 14: o OCR lê
um ícone da interface como símbolo do tamanho do texto, e ele chega ao tradutor colado à
linha.*

Os casos da pergunta, em 6 jogos:
- **uma caixa só para o ícone:**
  - os "+" no fim de cada linha da fila de skills do EVE Online, em duas colunas;
  - o "8" antes do nome da técnica do Immortal Clan;
  - um "A" baixo, 5 alturas depois de uma opção de diálogo do Disco Elysium;
- **o ícone dentro da caixa da palavra:**
  - o "≡" do menu do EVE ("≡ Overview (General)");
  - o cursor ">" do Caves of Qud ("> [2] Do you live here?");
  - a caixinha de marcar do Butterfly Soup, lida como "o" ("oUnseen Text");
  - o "*" de enfeite do The Big Con ("quit.*").

A regra de ícones que já existia (`quantidades.tirar_icones`) não os pega:
- o "8" e os "+" têm a altura do texto;
- a coluna de "+" é toda igual, e não mista de letra e não-letra;
- o "A" está longe da borda do print;
- a confiança dos "+" é de 0,97 a 0,99.

Cada proposta entrou como foi escrita, logo depois do filtro de desenhos, e foi medida nas
quatro leituras (`laboratorios/validacao/variantes_p14.py`). Cada caractere tirado foi
conferido contra o gabarito (`erros_p14.py`): é certo quando o texto lido tinha mais dele
do que o gabarito.

| Proposta | Linhas ganhas | Perdidas | Caracteres tirados | Que eram texto |
|---|---:|---:|---:|---:|
| **Grok** | **11** | **0** | 14 | **0** |
| DeepSeek | 8 | 1 | 21 | 6 ou mais |
| ChatGPT | 4 | 0 | 4 | 0 |
| Qwen | 3 | 1 | 7 | 1 |
| Mistral | 5 | 11 | 20 | 4 ou mais |

O que separou as propostas:
- **O ">" do Persona 4 é texto.** No gabarito, "> Obtained Peach Seed x 5" começa com ">".
  Qwen, DeepSeek e Mistral tiram todo ">" no começo da linha. O Grok só tira o cursor que
  vem antes de um atalho entre colchetes, como os do Caves of Qud.
- **"O" seguido de maiúscula é normal em maiúsculas.** Para pegar a caixinha do Butterfly
  Soup, o DeepSeek e o Mistral tiram o "o" ou o "O" antes de uma maiúscula. Nas telas em
  maiúsculas do Disco Elysium, saíram "PTIONS", "STEAU" e "VERPRODUCTIVE". A trava de
  repetição (2+ caixas) não segura, porque uma tela em maiúsculas repete o padrão.
- **Tirar um ícone certo pode desmontar a tela.** O Mistral tirou o "1" antes de "Missiles"
  na grade de skills do EVE, que é mesmo um ícone. Sem essa caixa, as regras de colunas
  montaram a grade de outro jeito, e 9 linhas se perderam. A régua das linhas inteiras
  pegou o que a conta das remoções não pegaria.
- **A ponta da linha.** O ChatGPT só tira o símbolo na ponta da linha, e não errou nada.
  Mas a coluna de "+" da esquerda fica no meio da linha, antes da segunda coluna da fila,
  e ficou.

Entrou a regra do Grok, como ele escreveu (`_tirar_icones_colados`, em `paragrafos.py`, logo
depois do filtro de desenhos):
- **Coluna de ícones:** 3+ caixas do mesmo símbolo ou dígito (Unicode Sm, So ou Nd), com a
  borda esquerda a até 1 altura e passo de até 3 alturas, cada uma a menos de 0,8 altura de
  um texto com letra. O dígito só sai quando vem antes do texto: depois dele, é valor
  ("Missiles 1").
- **Glifo longe:** letra latina ou símbolo de uma caixa só, mais baixo que 0,75 do texto e
  a 2,1 alturas ou mais da caixa mais perto da linha.
- **Pontas da linha:** o "≡" no começo, o cursor (">", "›", "▶"...) só antes de um atalho
  entre colchetes, e o enfeite ("*", "+", "★"...) logo depois de ".", "!", "?" ou "…" no
  fim.

Marcador de lista, letra em coluna ("A Route" do EasyOCR, uma caixa por palavra), o ">" no
meio ("Extras > Library") e o hífen da opção ("4. - Not now.") ficam.

No laboratório, o app reproduziu a variante do Grok print a print, nas quatro leituras. No
benchmark do app:

| Conjunto | Linhas inteiras | Linhas com sobra | Acerto de letras | Quebras a mais |
|---|---|---|---|---|
| 90 prints | 550 → 560 | 30 → 21 | 95,85% → 95,91% | 65 → 64 |
| Validação | 216 → 217 | igual | 91,35% → 91,42% | 32 → 31 |
| Espanhol | igual (11) | igual | igual | igual |

Nenhum print piorou. As 10 linhas dos 90 prints são 6 da fila de skills do EVE, o overview
do EVE e as três falas do Caves of Qud com o cursor. Na validação, a linha é a do The Big
Con. O "A" do Disco já saía numa linha à parte: com ele fora, sai uma quebra a mais.

**O que ficou de fora, e por quê:**
- **O "8" do Immortal Clan.** Ele aparece uma vez por print, e uma coluna de 3 não se
  forma. Com um "8" sozinho a 0,3 altura do nome, nada o separa de uma quantidade ("8 Lotus
  Heart"). Só o Mistral o tirou, pela altura e pela confiança juntas, e só num dos dois
  prints: no outro, a altura ficou dentro da faixa protegida (1,09 do texto).
- **A caixinha "oUnseen" do Butterfly Soup.** Medi a sugestão do Grok: o passo do CTC da
  1ª letra até a 2ª, contra a mediana das outras. No "oUnseen", ele é 1,83 vez a mediana,
  e o vão é de 0,27 altura. Nas 522 palavras de 4+ letras dos 150 prints que começam com
  uma letra seguida de maiúscula, "MELEE" (2,07), "TEMKET" (1,91) e "MONSTERS" (1,83)
  chegam a esse passo ou passam dele. O passo não separa.

Os dois são de um jogo só cada, e pela regra do projeto não viram regra.

Entraram 13 testes (`tests/test_icones_colados.py`): 6 com os casos que saem, a maioria
com as coordenadas dos prints, e 7 com o que tem de ficar. Sem a regra, os 6 primeiros
falham. Agora são 153 testes.

## A nona correção: a frase quebrada em linhas curtas (com as outras IAs)

*Feita em 25/11/2026 no branch `regra-frases-quebradas`, a partir do problema 15: letreiros,
balões e rótulos quebram a frase de propósito em linhas curtas e coladas, e o app deixava
cada pedaço numa linha.*

Eram 14 pares em 7 jogos:
- "Tu cosa / favorita", no formulário do Stardew em espanhol;
- "REWIND / FOR / HUMANKIND!", num letreiro do The Big Con;
- "Mercenary's Grenade / Rifle", na lista do Pip-Boy do Fallout.

Na maioria, só o "caberia" pedia a quebra: o letreiro é mais estreito que o print, então a
primeira palavra de baixo cabia na margem do print.

O vão sozinho não separa os casos. No mesmo formulário, "la granja / Tu cosa" (tem de
separar) tem vão de 0,00, e "Tu cosa / favorita" (tem de juntar), de −0,12. Nos 150 prints,
entre os pares de linhas coladas, 275 o app já separava certo, e 56 deles só pelo
"caberia".

Cada proposta entrou como foi escrita (`laboratorios/validacao/variantes_p15.py`): quando o
app quebraria o par e a proposta pede a junção, junta. Cada par juntado foi conferido contra
o gabarito (`erros_p15.py`). As linhas ganhas e perdidas são das quatro leituras.

| Proposta | Pares juntados | Certos | Errados | Linhas ganhas | Perdidas |
|---|---:|---:|---:|---:|---:|
| **Grok, com a trava do dígito** | 14 | 10 | **0** | **9** | **0** |
| Grok, como escrita | 15 | 10 | 1 | 9 | 1 |
| DeepSeek | 43 | 10 | 15 | 8 | 6 |
| ChatGPT, só os padrões que ele mandou testar primeiro | 32 | 6 | 9 | 6 | 20 |
| Qwen | 99 | 9 | 53 | 5 | 63 |
| ChatGPT, todos os padrões | 177 | 14 | 104 | 9 | 141 |
| Mistral | 210 | 15 | 139 | 9 | 165 |

Dos 4 pares sem veredito do Grok com a trava, 3 são leituras do EasyOCR que não batem letra
por letra com o gabarito ("Tu coso / fovorito"), e o quarto junta um "C" de lixo a
"Configure", no menu do EVE, sem mudar nenhuma linha.

**Por que as propostas largas perderam linhas.** Juntar é mais arriscado que separar: um
menu ou uma lista são pares colados do mesmo jeito que um letreiro.
- **Mistral e ChatGPT com todos os padrões:** os dois juntam o par colado quando a linha de
  cima é bem mais larga que a de baixo, e o Mistral também quando a de baixo fecha a frase.
  Isso pega menus e listas inteiras: as fichas do Morrowind, o menu do Butterfly Soup e as
  tarefas do Disco Elysium.
- **ChatGPT, só a palavra minúscula e o passo da lista:** o passo curto juntou atributos do
  Morrowind ("Willpower 40 / Agility 73").
- **Qwen:** a "palavra curta em minúscula" e o bloco centralizado de 2 linhas juntam menus
  do EVE e do Butterfly Soup.
- **DeepSeek:** a palavra única sobreposta junta itens de menu de uma palavra ("Planets /
  Stargates", "Display / Window").

**A proposta do Grok**, por outro lado, tem uma regra estreita para cada formato e
sempre pede um segundo sinal além das caixas coladas.

Entrou a regra do Grok (`_frases_quebradas`, em `paragrafos.py`), com uma trava minha. As
junções valem mais que o "caberia", o menu de uma palavra, o recuo e o marcador, como as dos
itens em duas linhas:
- **Minúscula colada (R1):** uma palavra minúscula, sem dígito, sobreposta a uma linha de 2+
  palavras que não fecha a frase, com a mesma esquerda (1 altura) e alturas a até 1,4 vez
  ("Tu cosa / favorita", "Color de / pelo:").
- **Letreiro (R2):** 3 ou 4 linhas com menos de 8 alturas, centralizadas (centros a 1
  altura, as duas bordas variando mais de 0,5), sobrepostas em 0,15 altura ou mais, sem
  marcador; só a última fecha a frase ("REWIND / FOR / HUMANKIND!").
- **Balão (R2b):** duas linhas assim, em que a de baixo fecha a frase em até 3 palavras.
- **Item que quebrou na lista (R3):** na coluna (borda a 1 altura, passo de até 3), o par
  sobreposto em 0,10 altura ou mais, com passo de até 0,80 do passo dos outros itens (2+
  pares com vão de 0,20 ou mais). A linha de baixo tem até 2 palavras, letra e nenhum
  dígito, e até 0,85 da largura da de cima ("Mercenary's Grenade / Rifle").
- **Cauda em maiúsculas (R4):** uma frase de 8+ alturas e 4+ palavras em maiúsculas, com
  vírgula ou aspas, e uma cauda de até 4 palavras embaixo, sem outra linha da coluna a 3
  alturas ("TAP "Q" OR "L" TO SEAMLESSLY SWITCH / LANGUAGES IN GAME").
- **Título deslocado (R6):** duas caixas de 1,30 altura ou mais, sobrepostas, a de baixo
  deslocada mais de 1,5 altura para a direita e com 1 ou 2 palavras.

**A trava minha:** a única perda do Grok veio da R1. Ela juntou "Harvest Magic Paper" com
"x300,000(152K/300K)", na lista de missões do Immortal Clan, porque a quantidade começa com
"x" minúsculo. A R3 do próprio Grok já exigia linha de baixo sem dígito; a mesma exigência
na R1 tirou a perda sem mudar nenhum ganho.

No laboratório, o app reproduziu a variante print a print, nas quatro leituras. No
benchmark do app:

| Conjunto | Linhas inteiras | Linhas partidas | Quebras a mais |
|---|---|---|---|
| 90 prints | 560 → 562 | 19 → 17 | 64 → 61 |
| Validação | 217 → 219 (75,5%) | 20 → 18 | 31 → 28 |
| Espanhol | 11 → 14 | 4 → 1 | 15 → 12 |

As letras não mudaram, e nenhum print piorou. As linhas ganhas são:
- os três rótulos do formulário do Stardew;
- o letreiro do The Big Con;
- a dica do Disco Elysium;
- o "Rifle" do Pip-Boy;
- "Neural Remap Available: Now", da ficha do EVE, que não estava entre os casos da
  pergunta.

Os 50 prints da validação entram no ajuste desde 24/11, então os 75,5% não valem como
aprovação no portão de 75%: quem prova as correções é a rodada 2, com jogos novos.

**O que ficou de fora:**
- **O balão "Whoa, I'm / INFORMATION."** A linha de baixo começa só 27 px abaixo, menos de
  meia altura típica do print (67 px), e o par não conta como linhas empilhadas. O Grok
  tinha previsto isso.
- **"HISTORICAL, BUT HER FRIEND / DOESN'T."** A R4 pede o par isolado na coluna, e há outras
  linhas perto. Também previsto.
- **O título da loja do Immortal Clan.** A caixa de baixo tem 1,298 da altura típica, contra
  o mínimo de 1,30 da R6. Na leitura do EasyOCR, o par se junta.
- **"SOCIAL SECURITY / ADMINISTRATION".** Fica no limite do vão (0,18) e as duas linhas têm
  quase a mesma largura, como dois itens; o Grok deixou de fora de propósito.

Entraram 9 testes (`tests/test_frases_quebradas.py`): 5 do que junta, com as coordenadas dos
prints, e 4 do que tem de continuar separado (a quantidade com "x", os tópicos de uma
palavra, o menu centralizado com respiro e o item de lista só encostado). Agora são 162
testes.

**Desde a medida da validação, nove correções:** nos 90 prints, as linhas inteiras foram de
539 para 562; na validação, de 190 para 219 (65,5% para 75,5%); no espanhol, de 8 para 14.

## A releitura dos gabaritos (25/11/2026)

Antes de congelar o código para a rodada 2, os 150 gabaritos (os 90 prints, a validação e
o espanhol) foram relidos contra as imagens, pela regra do [README do
benchmark](../benchmark/README.md): uma linha por parágrafo ou item. Primeiro, um script
apontou onde o app e o gabarito discordam de um jeito que pode ser erro do gabarito: 22
sinais em 16 prints. Depois, cada print foi aberto e comparado com o gabarito.

**12 gabaritos estavam fora da regra, todos do Immortal Clan, da primeira coleta (02/11):**
- **A loja do investidor** juntava itens de lugares diferentes da tela: o título com o selo
  "15x Earnings", os títulos sobre ícones diferentes ("Become Investor" e "Enjoy
  Privileges"), as legendas de quatro ícones, os rótulos de dois ícones com o "Limit Up"
  da seta, e o texto embaixo do botão com o rótulo do ícone do canto ("Lasts 30 days" e
  "Cat Ledger"). Foi de 9 para 18 linhas.
- **A lista de missões** juntava o rótulo embaixo do ícone com a barra de progresso
  ("Exile Decree" e "7/12"). Também separava um objetivo que não coube na caixa: "Harvest
  Magic Paper x300,000 (152K/300K)" é um item só, como o "Repair Sumeru Tower (0/1)" logo
  abaixo.
- **Os 10 tomos de técnica** juntavam a etiqueta do elemento com o selo do tipo, que é
  outro desenho ("Wood Technique" e "Sword Art").

Os outros 138 já seguiam a regra. Nos outros prints, os sinais eram erros do app ou
alarmes falsos:
- **Erros do app:** as abas juntadas no EVE Online; o título com a primeira opção no Disco
  Elysium e no Butterfly Soup; a assinatura do prefeito separada da fala no Stardew.
- **Alarmes falsos:** os tópicos em minúscula do Morrowind.

**O que ficou como estava, por convenção:**
- o nome da técnica com o nível na mesma barra ("Azureblade Array Lv.15", "Lotus Heart
  Unlocks: Lv.6"), como no gabarito de referência da pasta `base` ("Dream of Realms
  Lv.5");
- a linha de tabela, com o nome e os valores (EVE Online, Morrowind, Persona 4);
- a opção de configuração com o valor ao lado ("DISPLAY MODE Fullscreen", no Disco
  Elysium).

As versões antigas estão em `relatorios/validacao/gabaritos_antes_da_releitura/`. Um
script conferiu, em cada um dos 12, que as palavras continuam as mesmas e na mesma ordem:
só mudou onde a linha quebra. Por isso as letras não mudaram.

| Conjunto | Linhas inteiras | Quebras achadas | Quebras a mais |
|---|---|---|---|
| 90 prints | 562 de 661 (85,0%) → 549 de 671 (81,8%) | 688 de 744 → 689 de 763 | 61 → 60 |
| Validação | 219 de 290, igual | igual | igual |
| Espanhol | 14 de 21, igual | igual | igual |

O número caiu porque o gabarito antigo concordava com erros do app. O app junta a
etiqueta e o selo nos 10 tomos, e "Exile Decree 7/12" nas missões. Na loja, "Lasts 30 days"
e "Cat Ledger" agora contam como certas. O CSV é o `benchmark_20261125_234919.csv`.

**O laboratório guardava o gabarito no cache.** O `testar_regras.py` lia o gabarito copiado
para o cache de cada leitura, e as duas leituras dos 90 prints ainda tinham a versão
antiga dos 12. Agora ele lê o gabarito do dataset; o do cache só vale para um print que
saiu do dataset. Nos outros 138, as duas versões já eram iguais.

**Duas peças da nona correção perderam o caso que as sustentava.** As duas foram feitas em
cima de gabaritos que a releitura mostrou errados:
- **A trava do dígito (minha).** O único par que ela barrava, "Harvest Magic Paper" com
  "x300,000(152K/300K)", agora é uma junção certa. Sem a trava, com a R1 como o Grok
  escreveu, o laboratório põe uma quebra errada a menos nesse print, na leitura do app.
  Nada muda nas outras três leituras nem nos outros 149 prints. A linha não passa a contar
  inteira porque o OCR lê "x300,000(152K/300K)" sem o espaço.
- **O título deslocado (R6, do Grok).** O caso dela era o título da loja, que o gabarito
  antigo juntava como "Noble Investor 15x Earnings" e que foi às IAs na pergunta do
  problema 15. No print, "Noble Investor" é o título e "15x Earnings" é o selo. O OCR põe
  "Noble Investor 15x" numa caixa só, e juntar "Earnings" a ela não acerta nenhum dos dois
  itens. A R6 só muda a decisão do app nesse print, na leitura do EasyOCR, sem mudar
  nenhuma medida.

Os testes `test_quantidade_com_x_minusculo` e `test_titulo_grande_deslocado`
(`tests/test_frases_quebradas.py`) foram escritos sobre esses dois casos e guardam a
resposta do gabarito antigo.

**As duas peças saíram (26/11).** Antes, cada uma foi medida sozinha e junto com a outra,
nas quatro leituras dos 150 prints (`laboratorios/validacao/variantes/p15_sem_trava`,
`p15_sem_r6` e `p15_sem_trava_sem_r6`):

| Variante | O que muda |
|---|---|
| Sem a trava do dígito | Missões do Immortal Clan, leitura do app: uma quebra errada a menos |
| Sem a R6 | Loja do Immortal Clan, leitura do EasyOCR: uma quebra certa a mais |
| Sem as duas | As duas melhoras; nenhum print piora |

O risco fora do dataset é pequeno:
- **Sem a trava:** a R1 passa a juntar uma palavra minúscula com dígito ("x5", "v2") colada
  embaixo de um nome. É o nome com a quantidade ou o nível, que o gabarito já trata como uma
  linha só ("Medicine x 1", "Azureblade Array Lv.15"). Um número puro ("300", "5m") não
  entra, porque não começa com minúscula. A trava da R3 continua.
- **Sem a R6:** um título estilizado em duas linhas, com a de baixo deslocada, volta a
  sair em dois pedaços. Se a rodada 2 mostrar esse formato com casos reais, ele volta às
  IAs.

No laboratório, o código do app reproduziu a variante print a print. O benchmark do app
não mudou em nenhum dos três conjuntos (549 de 671, 219 de 290 e 14 de 21). Nas missões,
o app lê "x300,000 (152K/300K)" com o espaço que o reconhecedor devolve (problema 12).
São duas palavras, e a R1 só junta uma; o cache do laboratório guardou esse trecho sem o
espaço. A leitura do EasyOCR não entra no benchmark do app.

Os dois testes mudaram:
- **A quantidade agora junta:** `test_objetivo_com_quantidade`, com as coordenadas do
  print, espera "Harvest Magic Paper x300,000(152K/300K)".
- **O título deslocado saiu.** No lugar dele, `test_atributo_com_multiplicador` garante que
  a R1 não junta uma linha minúscula de mais de uma palavra ("Intelligence 42 / x2
  Willpower 40", desenhado colado). Sem a exigência de uma palavra, ele falha.

Continuam 162 testes.

**As propostas das IAs com o gabarito corrigido.** As propostas dos problemas 9 a 15,
menos as do 12 (que conta espaços), foram medidas de novo, cada uma contra o app da época,
nas mesmas leituras, com o gabarito antigo e com o corrigido. O `GABARITO_DO_CACHE=1` faz
o `testar_regras.py` usar o antigo, e o script é o
`laboratorios/validacao/remedir_propostas.py`. Com o gabarito antigo, a medida reproduz os
números de cada rodada.
- **Os problemas 9, 10, 11 e 14** não mudam.
- **No 13**, a regra do Grok, que entrou, vai de +7 −1 para +10 −0: a única perda era
  "Lasts 30 days | Cat Ledger".
- **No 15**, a regra do Grok como ele escreveu vai de +9 −1 para +9 −0.

As outras mudanças estão em [Quinze problemas, cinco IAs e uma
régua](consulta-outras-ias.md); os relatórios, em `relatorios/releitura/`.
