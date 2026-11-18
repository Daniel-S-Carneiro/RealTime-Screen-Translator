# Plano dos próximos testes: validação com jogos novos

*Escrito em 17/11/2026, depois das regras de colunas, itens lado a lado, quebras verticais
e da base de testes. Os problemas que continuam em aberto estão em
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
e valor (17/11/2026) e as abas pelo fundo (18/11/2026), as últimas regras que entram antes
da coleta. Antes delas, a
referência era o commit `235b28e`. Nos 90 prints atuais:

| Medida | Resultado |
|---|---|
| Acerto de letras | 95,1% |
| Acerto de palavras | 91,1% |
| Quebras achadas / certas | 90% / 89% (79 a mais) |
| Linhas inteiras | 80% (529 de 661) |

| Tipo de tela | Acerto de letras | Linhas inteiras |
|---|---|---|
| texto | 99,5% | 92% |
| legenda | 99,4% | 81% |
| menu | 98,8% | 80% |
| ficha | 90,3% | 75% |
| letreiro | 79,4% | 74% |

Nenhuma regra muda até a validação ser medida. A validação também vai dizer se a margem
do painel, a regra das listas e a das abas, medidas só nestes 90 prints, valem em jogos
novos.

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
- **Opcional:** um dos jogos em espanhol ou japonês, com o app configurado nessa língua.
- **Inclua telas difíceis:** letra pequena, fundo colorido, painéis. Não escolha só as
  que parecem fáceis.
- **Abas:** se o jogo tiver uma barra de abas (inventário, mapa, opções), inclua um print
  dela. A regra das abas só foi medida nas abas do EVE.
- *O que esperar:* cerca de 30 prints numa ou duas pastas de dia, sem precisar renomear.

## Fase 2: organização e descarte

**2.1 Organização: pasta de validação.** Os prints vão para `benchmark/dataset/validacao/`,
para o benchmark poder medir só eles (`--periodo validacao`). Os nomes seguem o padrão
`<jogo>_<tipo>_<n>`.
- *O que esperar:* uma pasta só, com nomes que dizem o jogo e o tipo de tela.

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
gabarito ao que o app faz.
- *O que esperar:* um `.txt` por print. Prints em outra língua com gabarito incerto são
  sinalizados.

**2.4 Organização: tipo de tela.** Cada print entra em `benchmark/categorias.json`.
- *O que esperar:* o benchmark já mostra a validação por tipo de tela.

## Fase 3: teste de validação, sem mudar nada

**3.1 Teste: critério fixado antes de medir.** As regras "valem para jogos novos" se:
- o acerto de letras for de **93% ou mais** e as linhas inteiras, de **75% ou mais**;
- nenhum tipo de tela ficar mais de **5 pontos** abaixo do mesmo tipo nos 90 prints.

**3.2 Teste: benchmark da validação** (`benchmark.py --periodo validacao`), com a versão de
referência.
- *O que esperar:* as mesmas medidas da régua, por jogo e por tipo de tela. A expectativa
  é ficar um pouco abaixo dos 90 prints, que foram usados para ajustar as regras: algo
  entre 92% e 95% nas letras e entre 70% e 78% nas linhas inteiras. Muito abaixo disso,
  alguma regra decorou o dataset.

**3.3 Teste: testes automáticos.** Os 45 testes continuam passando.

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

1. **Fichas:** 75% das linhas inteiras e 63 das 79 quebras a mais.
2. **Letreiros:** 79,4% das letras. A ideia que restou é super-resolução só nas caixas
   pequenas; ampliar o print inteiro piorou, mas ampliar só as caixas pequenas não foi
   testado.
3. **Pacote de GPU:** uma decisão de produto, já que agora a placa só ajuda nas línguas do
   EasyOCR.
4. **Modelos do RapidOCR para outras escritas**, se vierem prints em outra língua.
5. **Qualidade da tradução:** fora por decisão do dono do projeto, até ele pedir.

## O que já foi abandonado, e por quê

| Jogo ou caso | O que não será mais tentado | Por quê |
|---|---|---|
| Doki Doki: barra "History Skip Auto Save Load Settings" | Separar os itens | O OCR lê a barra numa caixa só, e o espaço entre os itens é igual ao espaço normal de outras fontes |
| EVE: abas de uma palavra encostadas | Separar pelas caixas | Sem uma caixa de duas palavras na linha, não há sinal; só voltaria com uma ideia pelo desenho da tela |
| Night in the Woods: letreiro miúdo da banca | Ler o letreiro | Texto pequeno e borrado vira lixo; é limite do OCR |
| Caves of Qud: resumo do personagem | Acertar a ordem | As duas ordens fazem sentido; o gabarito não muda para agradar o app |
| Persona 4: quantidades do inventário | Ler as quantidades | O OCR não lê esses números pequenos |
| Danganronpa: título inclinado | Acertar as quebras do título | O texto inclinado mistura as linhas |
| Caves of Qud: descrições curtas sem pontuação | Separar as frases | Nenhum sinal as distingue de uma frase que continua |
| Correção de palavras (SymSpell, KenLM, JamSpell, LanguageTool, LLM, BERT por padrão) | Tudo | Teto de cerca de 1% das palavras |
| Tratar a imagem (inverter, suavizar, binarizar, ampliar o print todo, CLAHE, nitidez) | Tudo | Todos perderam para a imagem em cinza |
| Outros motores (OCR do Windows, modelos maiores, Tesseract, combinar motores) | Tudo | O RapidOCR v6 small ganhou de todos |
| Margem por bloco no "cabia" | A regra, do jeito testado | Perdeu nas duas versões testadas |

Ainda **não** foram abandonados:
- o diálogo e a subida de nível do Morrowind, a grade e o overview do EVE e a reputação do
  Caves of Qud: entram na fase das fichas;
- o menu em que o primeiro item é o mais largo: é o limite conhecido nos testes;
- as quebras verticais difíceis, com prioridade baixa.
