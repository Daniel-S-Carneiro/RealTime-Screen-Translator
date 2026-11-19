# Plano dos próximos testes: validação com jogos novos

*Escrito em 17/11/2026, depois das regras de colunas, itens lado a lado, quebras verticais
e da base de testes; atualizado em 19/11/2026 com as avaliações do ChatGPT e do Grok. O que
fica congelado, a régua e o que reprovaria cada regra estão na [referência da
validação](referencia-validacao.md). Os problemas que continuam em aberto estão em
[problemas-em-aberto.md](problemas-em-aberto.md).*

Em dois dias entraram mais de dez regras novas de montagem do texto, todas medidas nos
mesmos 90 prints. Antes de corrigir mais coisas, o próximo passo é medir se elas valem
para jogos que o app nunca viu. Um conjunto que serve para ajustar não serve para provar
(lição 1 do [estudo de caso](estudo-de-caso-ocr.md)).

## Os tipos de passo

| Tipo | O que é | Quem faz |
|---|---|---|
| **Coleta** | Tirar prints de jogos com o modo de coleta do app | O dono do projeto |
| **Organização** | Renomear, separar em pastas, escrever gabaritos, classificar o tipo de tela | Claude, com conferência por amostra |
| **Descarte** | Tirar do teste os prints que não podem ou não devem ter gabarito | Claude, pelas regras combinadas |
| **Teste** | Medir sem mudar nada: benchmark, testes automáticos, comparação com a versão anterior | Claude |
| **Laboratório** | Investigar erros e testar regras novas sobre as caixas guardadas, fora do app e do git | Claude |
| **Produção** | Passar para o app o que foi aprovado: commit, PR e `main` | Claude, quando pedido |

## Ponto de partida

A versão de referência é a `main` com a margem do painel estreito, as listas de rótulo
e valor (17/11/2026), as abas pelo fundo, a barra de menu numa caixa só, a segunda
leitura das caixas pequenas, as quantidades e ícones e o menu vertical (18/11/2026) e os
itens em duas linhas (19/11/2026), as últimas regras que entram antes da coleta. Ela está
marcada com a tag `referencia-validacao-2026-11-19` (commit `81b612e`). Antes delas, a
referência era o commit `235b28e`. Nos 90 prints atuais:

| Medida | Resultado |
|---|---|
| Acerto de letras sem ordem (as linhas lidas na ordem do gabarito) | 97,0% |
| Acerto de letras | 95,8% |
| Acerto de palavras | 91,4% |
| Quebras achadas / certas | 92% / 91% (69 a mais) |
| Linhas inteiras | 82% (539 de 661) |
| Tempo por print (média / p95) | 0,8 s / 2,5 s |

| Tipo de tela | Letras sem ordem | Letras | Linhas inteiras |
|---|---|---|---|
| texto | 99,5% | 99,5% | 92% |
| legenda | 99,4% | 99,4% | 81% |
| menu | 98,8% | 98,8% | 80% |
| ficha | 95,2% | 90,5% | 77% |
| letreiro | 85,9% | 85,9% | 78% |

Nenhuma regra muda até a validação ser medida. A validação também vai dizer se a margem
do painel, a regra das listas, a das abas, a da barra de menu, a segunda leitura, a das
quantidades e ícones, a do menu vertical e a dos itens em duas linhas, medidas só nestes
90 prints, valem em jogos novos.

## Fase 1: coleta

**1.1 Coleta: abrir o app pelo código.** O modo de coleta só aparece rodando pelo código
(`env\Scripts\python.exe main.py`). No menu da bandeja, "Salvar prints para o benchmark"
grava o print e o rascunho do OCR na pasta do dia.
- *O que esperar:* um `.png` e um `.rascunho.txt` por captura, em
  `benchmark/dataset/AAAA-MM-DD/`.

**1.2 Coleta: os prints.**
- **Quantidade:** 5 jogos novos, que ainda não estão no dataset, com cerca de 6 prints
  cada: uns 30 no total.
- **Por jogo:** 2 fichas ou inventários, 2 legendas ou falas, 1 menu e 1 texto longo.
- **Variedade:** de preferência estilos diferentes entre si, como estratégia, RPG 3D,
  indie em pixel art, visual novel e roguelike.
- **Outra língua:** um dos jogos em japonês ou espanhol, com o app configurado nessa
  língua. Os 90 prints são todos em inglês, e as regras de escrita sem espaço e de árabe só
  foram vistas em casos simulados; as avaliações do ChatGPT e do Grok de 19/11 puseram isso
  no topo. O japonês testa mais regras diferentes; o espanhol é mais fácil de achar.
- **Inclua telas difíceis:** letra pequena, fundo colorido, painéis. Não escolha só as
  que parecem fáceis.
- **Abas:** se o jogo tiver uma barra de abas (inventário, mapa, opções), inclua um print
  dela. A regra das abas só foi medida nas abas do EVE.
- *O que esperar:* cerca de 30 prints numa ou duas pastas de dia, sem precisar renomear.

**1.3 Coleta: um tipo de jogo para cada regra nova (18/11/2026).** As regras que
entraram por último foram medidas em um ou dois jogos cada. Cada jogo novo deve testar uma
delas (os títulos são exemplos; qualquer jogo do mesmo tipo serve):

| Tipo de jogo | Exemplos | O que testa | Os 6 prints |
|---|---|---|---|
| Visual novel feita em Ren'Py | Katawa Shoujo, Butterfly Soup (grátis), Slay the Princess | Barra de menu numa caixa só | 3 falas com a barra de menu embaixo (de preferência com um item apagado ou destacado), menu principal, preferências, tela de salvar |
| RPG com diálogo em painel e ficha | Disco Elysium, Pillars of Eternity, Baldur's Gate 3, Skyrim | Margem do painel estreito, listas de rótulo e valor, listas com item em duas linhas | 2 diálogos longos no painel (de preferência com uma lista de tópicos ou de respostas ao lado), 2 fichas de atributos, 1 inventário, 1 diário |
| Jogo com inventário em abas | Stardew Valley, Terraria, Fallout 4, Path of Exile | Abas pelo fundo | 2 telas com a barra de abas (uma aba selecionada), 2 inventários, 1 fala, 1 descrição de item |
| Jogo 3D com placas no cenário | Firewatch, Life is Strange, Persona 5, Cyberpunk 2077 | Letreiros (Problema 5) | 3 placas ou letreiros (pequenos, de longe, inclinados), 2 legendas, 1 menu |
| Estratégia ou simulação | Civilization VI, Stellaris, Crusader Kings III, Football Manager | Tabelas, painéis, menus | 2 tabelas, 2 painéis de informação, 1 menu, 1 texto de enciclopédia |
| JRPG com inventário em lista (se der) | Final Fantasy X, Dragon Quest XI, Octopath Traveler, Persona 5 | Quantidades e ícones (Problema 6) | 3 inventários ou lojas com a quantidade à direita ("× 3"), de preferência com um item destacado; 1 menu; 2 falas |

O jogo em outra língua (veja 1.2) pode ser um sexto jogo, com 2 legendas, 2 menus e 2
fichas.

**1.4 Coleta: voltar a jogos que já estão no dataset (opcional).** Não serve para a
validação, que só vale com jogos novos. Serve para os problemas que continuam abertos, e
os prints vão para a pasta do dia, como os outros 90, não para `validacao/`:
- Persona 4: 2 telas de inventário com quantidades ("x 5"), para o Problema 6;
- Night in the Woods: 2 letreiros de rua, para o Problema 5;
- Caves of Qud: 1 ou 2 telas de criação de personagem com listas de características, para
  o Problema 7 (descrições curtas sem pontuação; é o Problema 8 no arquivo de perguntas
  para as IAs).

## Fase 2: organização e descarte

**2.1 Organização: pasta de validação.** Os prints vão para `benchmark/dataset/validacao/`,
para o benchmark poder medir só eles (`--periodo validacao`). Os nomes seguem o padrão
`<jogo>_<tipo>_<n>`.
- Os prints são **movidos** da pasta do dia, não copiados: o benchmark varre todas as
  pastas, e uma cópia contaria duas vezes.
- O `.rascunho.txt` de cada print (o que o app leu na hora da coleta) **fica para trás**,
  na pasta do dia, e não é aberto antes do gabarito (veja 2.3).
- Cada print ganha uma linha em `validacao/manifesto.csv`: o jogo, o tipo de tela, a
  regra que ele testa (aba, barra de menu, placa, ficha, quantidade, lista, outra língua)
  e se o gabarito foi escrito antes de olhar o resultado do app. Sem isso, na fase 4 não
  dá para saber qual regra falhou.
- *O que esperar:* uma pasta só, com nomes que dizem o jogo e o tipo de tela, e o
  manifesto preenchido.

**2.2 Descarte: o que sai do teste.** Vai para `_fora/`, sem gabarito:
- letra de música, ou texto completo de terceiros (poema, carta inteira, página de livro);
- telas sem texto legível (carregamento, tela preta, só ícones);
- prints repetidos da mesma tela.

Texto cortado pela borda do print **não** é descartado: segue a regra de ficar fora do
gabarito.
- *O que esperar:* de 0 a 5 descartes, cada um com o motivo anotado.

**2.3 Organização: gabaritos.** Com as regras de sempre:
- ordem de leitura de uma pessoa, um painel de cada vez;
- uma linha por parágrafo ou item;
- ícones e cursores ficam fora;
- texto cortado pelo próprio jogo entra como aparece.

Os gabaritos são escritos **antes** de olhar o resultado do app, para não ajustar o
gabarito ao que o app faz: olhando só o `.png`, sem abrir o `.rascunho.txt` e sem rodar o
benchmark. Nos 90 prints, o rascunho era corrigido (é o que o
[README do benchmark](../benchmark/README.md) ensina); na validação, isso seria olhar a
resposta antes da prova.
- *O que esperar:* um `.txt` por print. Prints em outra língua com gabarito incerto são
  sinalizados.

**2.4 Organização: tipo de tela.** Cada print entra em `benchmark/categorias.json`.
- *O que esperar:* o benchmark já mostra a validação por tipo de tela.

## Fase 3: teste de validação, sem mudar nada

**3.1 Teste: critério fixado antes de medir.** As regras "valem para jogos novos" se:
- o acerto de letras sem ordem for de **93% ou mais** e as linhas inteiras, de **75% ou
  mais**;
- nenhum tipo de tela ficar mais de **5 pontos** abaixo do mesmo tipo nos 90 prints, nas
  letras sem ordem e nas linhas inteiras.

O portão de letras usa a medida sem ordem desde 19/11/2026, decidido antes da coleta: um
painel lido na outra ordem, quando as duas fazem sentido, não é regra que decorou o
dataset. A medida de sempre continua registrada ao lado. Os motivos estão na [referência
da validação](referencia-validacao.md).

**Abas e barra de menu são provisórias.** Foram medidas em um jogo cada. Se o jogo novo não
tiver o sinal, a regra não dispara, e isso não a reprova. Se ela cortar errado, a decisão
é estreitar ou desligar, nunca reajustar os limites em cima da validação.

**3.2 Teste: benchmark da validação** (`benchmark.py --periodo validacao`), com a versão de
referência.
- *O que esperar:* as mesmas medidas da régua, por jogo e por tipo de tela. A expectativa
  é ficar um pouco abaixo dos 90 prints, que foram usados para ajustar as regras: algo
  entre 93% e 96% nas letras sem ordem e entre 70% e 78% nas linhas inteiras. Muito abaixo
  disso, alguma regra decorou o dataset. O tempo por print (média e p95) também é
  registrado.

**3.3 Teste: testes automáticos.** Os 102 testes continuam passando, e o `git diff` da
[referência da validação](referencia-validacao.md) sai vazio.

**3.4 Organização: registro.** O resultado vai para um anexo próprio,
`docs/resultados-validacao.md`, e para o estudo de caso, sem sobrescrever os resultados
antigos.

A validação vale **uma vez**. Depois que os erros dela forem usados para ajustar regras,
ela passa a fazer parte do conjunto de ajuste (cerca de 120 prints), e uma próxima
validação precisa de prints novos.

## Fase 4: laboratório

**4.1 Laboratório: guardar a leitura.** O OCR roda uma vez nos prints novos, e as caixas vão
para o cache. A partir daí, cada teste de regra leva segundos.

**4.2 Laboratório: classificar os erros.** Para cada linha que não chega inteira:
- é leitura (palavra faltando), montagem (com sobra ou partida) ou ordem?
- em que tipo de tela?
- é um erro conhecido ou de um tipo que os 90 prints não tinham?
- *O que esperar:* uma tabela dos erros novos por tipo e os prints que mais perdem.

**4.3 Laboratório: corrigir, um erro por vez.**
1. Achar um caso reproduzível.
2. Medir o sinal nos cerca de 120 prints antes de escrever a regra.
3. Fazer o teste diferencial contra a `main` (`laboratorios/quebras/testar_regras.py
   --comparar main`), nas leituras dos dois motores.
4. Olhar o resultado por tipo de tela.
5. Criar um caso simulado novo, se a regra puder afetar outra língua.

## Fase 5: produção

**5.1 Teste: critério de entrada.** Uma regra só entra se:
- melhora a média;
- não piora a maioria dos prints;
- passa nos testes automáticos;
- não estraga a leitura do EasyOCR.

**5.2 Produção: entrada no app.** Benchmark completo, documentos atualizados (estudo de
caso, anexos, README), commit, PR e `main`.

## Fase 6: alvos depois da validação, nesta ordem

1. **Fichas:** 77% das linhas inteiras e 59 das 69 quebras a mais. Só vira regra o
   desenho que se repetir nas fichas dos jogos novos.
2. **Letreiros:** 85,9% das letras. Sobram letras que as duas leituras erram igual
   ("SECUPITY"). A ideia que restou é super-resolução só nas caixas pequenas (FSRCNN ou
   ESPCN, modelos leves do OpenCV): ampliar o print inteiro piorou, mas ampliar só as
   caixas pequenas não foi testado. Roda no laboratório, sobre as caixas guardadas, com o
   critério escrito antes: letras dos letreiros sobem, nenhum outro tipo desce, poucas
   centenas de milissegundos a mais.
3. **Pacote de GPU:** uma decisão de produto, já que agora a placa só ajuda nas línguas do
   EasyOCR.
4. **Modelos do RapidOCR para outras escritas**, se vierem prints em outra língua.
5. **Qualidade da tradução:** fora por decisão do dono do projeto, até ele pedir.

## O que já foi abandonado, e por quê

| Jogo ou caso | O que não será mais tentado | Por quê |
|---|---|---|
| Night in the Woods: letreiro miúdo da banca | Ler o letreiro | Texto pequeno e borrado vira lixo; é limite do OCR |
| Caves of Qud: resumo do personagem | Acertar a ordem | As duas ordens fazem sentido; o gabarito não muda para agradar o app |
| Danganronpa: título inclinado | Acertar as quebras do título | O texto inclinado mistura as linhas |
| Correção de palavras (SymSpell, KenLM, JamSpell, LanguageTool, LLM, BERT por padrão) | Tudo | Teto de cerca de 1% das palavras |
| Tratar a imagem (inverter, suavizar, binarizar, ampliar o print todo, CLAHE, nitidez) | Tudo | Todos perderam para a imagem em cinza |
| Outros motores (OCR do Windows, modelos maiores, Tesseract, combinar motores) | Tudo | O RapidOCR v6 small ganhou de todos |
| Margem por bloco no "cabia" | A regra, do jeito testado | Perdeu nas duas versões testadas |

Três casos que estavam nesta lista foram resolvidos depois, com propostas de outras IAs
medidas nos 90 prints (17 e 18/11): a barra do Doki Doki (pelo espaço medido na tinta), as
abas do EVE (pelo fundo da aba selecionada) e as quantidades do Persona (relendo a célula
que o detector pulou). Os detalhes estão em [problemas em aberto](problemas-em-aberto.md).

Ainda **não** foram abandonados:
- o diálogo e a subida de nível do Morrowind, a grade e o overview do EVE e a reputação do
  Caves of Qud: entram na fase das fichas;
- o menu de só 2 itens em que o primeiro é o mais largo: é limite conhecido nos testes (o
  de 3 ou mais, e as descrições curtas do Caves of Qud, foram resolvidos em 18/11; a lista
  de tópicos do diálogo do Morrowind, em 19/11);
- as quebras verticais difíceis, com prioridade baixa.
