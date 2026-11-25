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

