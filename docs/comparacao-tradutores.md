# Os tradutores, lado a lado

*26/11/2026. A primeira medida da qualidade da tradução no projeto: os três motores pagos
que o app já usa (nas cotas grátis), o Argos, que é o offline de hoje, e três modelos
offline novos. Até aqui, o benchmark só media a leitura (OCR) e a montagem do texto.*

## Resumo

| Motor | Nota média (1 a 5) | Notas 5 | Erros graves (nota 1 ou 2) | Segundos por linha |
|---|---:|---:|---:|---:|
| Google Cloud | **4,52** | 73% | 6% | 0,07 (rede) |
| Azure | 4,40 | 72% | 9% | 0,20 (rede) |
| DeepL | 4,38 | 71% | 9% | 0,14 (rede) |
| **Hy-MT2 1.8B** (offline) | **4,08** | 55% | **11%** | 0,66 |
| Argos (offline de hoje) | 3,83 | 47% | 20% | 0,08 |
| OPUS-MT en→pt (offline) | 3,75 | 48% | 27% | 0,06 |
| M2M100 418M (offline) | 2,80 | 27% | 52% | 0,15 |

- **Os pagos empatam.** Entre o Google Cloud, a Azure e o DeepL, a diferença (0,14 ponto)
  é pequena para uma amostra de 132 linhas.
- **O Hy-MT2 é o melhor offline.** Erra feio em 11% das linhas, perto dos pagos e metade
  do Argos. No espanhol, teve a maior nota de todos (4,59). Custa um download de 1,13 GB,
  uns 3 GB de RAM e 0,66 s por linha no processador, 8 vezes o Argos.
- **O Argos continua útil** como offline leve: 81 MB por par e 0,08 s por linha.
- **O M2M100 e o OPUS-MT saem.** O M2M100 erra feio em metade das linhas. O OPUS-MT só
  traduz do inglês e fica abaixo do Argos.

As notas são minhas, dadas às cegas. O dono do projeto conferiu 30 linhas, também às
cegas, e a ordem dos motores se manteve (veja "A conferência do dono do projeto").

## Como foi medido

**O texto.** Os gabaritos dos 150 prints do benchmark, linha a linha: 1.233 linhas em
inglês e 67 em espanhol (o Stardew Valley). Partir do gabarito tira da conta os erros do
OCR e mede só a tradução. Cada linha é um parágrafo ou item, como o app manda. O destino é
o português do Brasil.

**Os motores.**
- **Pagos (Azure, DeepL e Google Cloud):** com as chaves do app, pelas mesmas funções
  do app (`motores_traducao.py`), um pedido por print, com um item por linha. Rodaram uma
  vez só, depois de conferir o uso do mês, e as traduções ficaram guardadas para as
  próximas comparações. Cada motor gastou 38.781 caracteres da cota grátis. O Google
  grátis ficou de fora, porque a rede do dono do projeto está bloqueada.
- **Argos:** o do app (`tradutor_offline.py`), uma linha por vez. O espanhol passa pelo
  inglês; o par espanhol→inglês foi baixado para a medida (304 MB).
- **Hy-MT2 1.8B** (Tencent, Apache 2.0): o arquivo `Hy-MT2-1.8B-Q4_K_M.gguf` (1,13 GB) no
  servidor local do llama.cpp (b12751), uma linha por pedido, com a instrução e os
  parâmetros do README do modelo (temperature 0,7, top_p 0,6, top_k 20,
  repetition_penalty 1,05).
- **M2M100 418M** (Meta, MIT) e **OPUS-MT tc-big en-pt** (Helsinki-NLP, CC-BY 4.0):
  convertidos para o CTranslate2 em int8, o motor que o Argos já usa (471 MB e 226 MB),
  com beam 4. O OPUS-MT recebe o rótulo `>>pob<<`, do português do Brasil.

**O PC:** Intel de 11ª geração (4 núcleos, 8 threads) e 11 GB de RAM, sem GPU nos
offline (4 threads). O tempo dos pagos inclui a rede.

**A qualidade, de dois jeitos:**
1. **Checagens automáticas**, em todas as 1.300 linhas: tradução vazia, igual ao original
   (linhas de 3+ palavras), números perdidos ou trocados, colchetes perdidos e tamanho fora
   do normal.
2. **Avaliação cega**, numa amostra de 132 linhas: 22 de cada tipo de tela (ficha,
   legenda, letreiro, menu e texto) e 22 em espanhol, sorteadas. As traduções de cada
   linha aparecem com letras sorteadas, e a chave (que letra é que motor) só foi aberta
   depois de todas as notas. A escala vai de 1 a 5:
   - 5: correto e natural;
   - 4: correto, com algum estranhamento;
   - 3: dá para entender, mas tem um erro;
   - 2: o sentido mudou ou falta uma parte importante;
   - 1: errado, sem sentido ou sem traduzir.

   Nome próprio mantido em inglês não perde ponto.

## As checagens automáticas

| Motor | Linhas | Iguais ao original | Números | Colchetes | Tamanho |
|---|---:|---:|---:|---:|---:|
| DeepL | 1.300 | 28 | 14 | 0 | 0 |
| Azure | 1.300 | 33 | 1 | 0 | 0 |
| Google Cloud | 1.300 | 15 | 4 | 0 | 0 |
| Argos | 1.300 | 40 | 25 | 42 | 4 |
| Hy-MT2 1.8B | 1.300 | 40 | 3 | 0 | 0 |
| M2M100 418M | 1.300 | 7 | 19 | 14 | 0 |
| OPUS-MT | 1.233 | 43 | 11 | 24 | 1 |

Nenhum motor devolveu tradução vazia. As checagens acham erros de verdade, mas também
alarmes falsos:
- **Erros de verdade:**
  - o DeepL trocou linhas curtas sem contexto ("Jita (0.9)" virou "Você", "HP 129" virou
    "Alta pressão", "Ego: 16" virou "Dezesseis");
  - o Argos apaga os efeitos entre colchetes ("[Sleep]" some da frase);
  - o M2M100 troca "320d" por "3D".
- **Alarmes falsos:**
  - "1 buff" vira "um bônus";
  - a data muda de formato;
  - nomes próprios ficam em inglês, como "Azure Blade Tome" e "Bifang Skyflame Lv.10".

## A avaliação cega

| Motor | Geral | Espanhol | Ficha | Legenda | Letreiro | Menu | Texto |
|---|---:|---:|---:|---:|---:|---:|---:|
| Google Cloud | 4,52 | 4,55 | 4,55 | 4,77 | 4,14 | 4,64 | 4,45 |
| Azure | 4,40 | 4,27 | 4,05 | 4,59 | 4,55 | 4,64 | 4,32 |
| DeepL | 4,38 | 4,45 | 4,36 | 4,00 | 4,50 | 4,82 | 4,14 |
| Hy-MT2 1.8B | 4,08 | 4,59 | 4,05 | 4,14 | 3,86 | 4,23 | 3,64 |
| Argos | 3,83 | 3,77 | 4,41 | 4,23 | 3,64 | 3,82 | 3,14 |
| OPUS-MT | 3,75 | – | 3,82 | 4,23 | 2,95 | 4,14 | 3,59 |
| M2M100 418M | 2,80 | 3,95 | 2,77 | 2,41 | 2,59 | 2,59 | 2,45 |

**O que separou os motores:**
- **Termos de jogo.** "turns" virou "voltas" em vários motores, quando é "turnos"; "Deals
  320% P.DMG" virou "lida com", "negocia" ou "dê"; "DMG RED" (redução de dano) virou "Dano
  Vermelho". Os pagos e o Hy-MT2 erraram menos esses termos.
- **Botões de uma palavra, sem contexto.** "Auto" virou "carro", "Skip" virou
  "Escavação", "Nombre" virou "Número", "Recurso" virou "Apelação". Esse erro aparece
  em vários motores, inclusive nos bons.
- **Frases cortadas.** O M2M100 e o Argos às vezes deixam fora a última frase de uma fala.
- **O letreiro "THIS WAY TO TRAIN"** (o caminho para o trem) saiu errado em todos: todos
  leram "treinar".

## A conferência do dono do projeto (27/11)

O dono do projeto deu notas, também às cegas, a 30 das 132 linhas: 5 de cada tipo de tela,
205 traduções ao todo. A página não mostrava a chave nem as minhas notas.

| | Resultado |
|---|---|
| Nota igual à minha | 48% |
| Diferença de até 1 ponto | 85% (88% sem a linha "Auto") |
| Correlação entre as notas | 0,60 (0,70 sem a linha "Auto") |
| Média das notas | 3,86 a dele, 3,93 a minha |
| Erro grave (nota 1 ou 2) | nos dois em 22 traduções; só eu em 15; só ele em 13 |

Nas mesmas 30 linhas, a média de cada motor:

| Motor | Dele | Minha |
|---|---:|---:|
| Google Cloud | 4,50 | 4,70 |
| Azure | 4,43 | 4,30 |
| Hy-MT2 1.8B | 3,93 | 3,87 |
| DeepL | 3,90 | 4,10 |
| Argos | 3,53 | 3,87 |
| OPUS-MT | 3,44 | 3,92 |
| M2M100 418M | 3,20 | 2,77 |

**A ordem se mantém.** O Google Cloud e a Azure ficam no topo, e o M2M100 embaixo. O
Hy-MT2 fica à frente do Argos, e nas notas dele a distância é maior (3,93 contra 3,53). Em
30 linhas por motor, diferenças de poucos décimos não separam os motores.

**Onde discordamos:**
- **O botão "Auto"**, que pesou mais que todas as outras. No Doki Doki Literature Club,
  ele liga o avanço automático das falas. Eu dei 5 a "Auto" e 1 a "Carro"; ele fez o
  contrário, lendo a palavra fora do jogo. Sem contexto, até uma pessoa traduz errado: é o
  mesmo problema que os motores têm com os botões de uma palavra.
- **Termos de jogo sem traduzir** ("Dao Spell", "Sword Art"): ele foi mais rígido (1) que
  eu (3).
- **Sentido próximo:** ele aceitou "Total obtido" para "Total Obtainable", e eu tirei
  ponto, porque "obtido" não é "que dá para obter". Ele também tirou pontos de "Saldo
  atual" para "Fondos actuales", e eu dei 5.

**O critério dele foi outro, e explica a maior parte das diferenças.** Ele avaliou se a
tradução dá para entender: quando não conhecia o contexto ou se confundia com um nome,
preferiu a tradução literal, e as notas 1 e 2 marcam o que atrapalharia o entendimento.
Eu avaliei também se a tradução está certa para a tela do jogo (o "Auto" como botão, o
termo de jogo). Mesmo assim, os erros graves coincidiram em 22 traduções. Nas próximas
conferências, a página vai mostrar o contexto de cada linha: o jogo, as linhas vizinhas
e se ela é um botão ou um nome.

## O custo de cada offline

| Motor | Download | No disco | Memória | Carga | Segundos por linha |
|---|---:|---:|---:|---:|---:|
| Argos | 81 MB por par (304 MB o es→en) | o mesmo | não medida | – | 0,08 |
| Hy-MT2 1.8B (Q4_K_M) | 1,13 GB + llama.cpp 25 MB | 1,2 GB | 3,2 GB (servidor) | 2,0 s | 0,66 |
| M2M100 418M | 1,9 GB (convertido aqui) | 471 MB | 505 MB | 0,6 s | 0,15 |
| OPUS-MT en→pt | 465 MB (convertido aqui) | 226 MB | 252 MB | 0,3 s | 0,06 |

Com 0,66 s por linha no processador, uma tela de 10 linhas leva uns 7 s no Hy-MT2. A
próxima medida dele é com a GPU (a MX350 tem 2 GB, e o llama.cpp roda com CUDA ou
Vulkan) e com a tela inteira num pedido só, em vez de um pedido por linha.

## As ressalvas

- **As notas são minhas.** A avaliação foi cega, com um avaliador nas 132 linhas. O dono
  do projeto conferiu 30 delas, e a concordância foi boa, mas não total.
- **O texto é o gabarito.** No app, a tradução recebe o texto do OCR, com os erros dele.
- **Cada linha vai sozinha**, sem as vizinhas e sem o contexto do jogo, como o app manda
  hoje. Os botões de uma palavra sofrem mais com isso. O contexto para os LLMs está no
  bloco 2 da primeira build.
- **O Hy-MT2 sorteia as palavras** (temperature 0,7, a recomendada). Duas rodadas podem dar
  traduções um pouco diferentes.
- **A amostra é pequena** para separar os pagos entre si: 132 linhas e diferenças de
  décimos.

## O que isso muda

1. **No app, por enquanto, nada.** Os pagos continuam sendo a melhor escolha, e o Argos,
   o offline leve.
2. **O Hy-MT2 é o candidato a offline de qualidade**, para download opcional, depois das
   medidas com a GPU e com a tela num pedido só. A licença (Apache 2.0) permite vender o
   app com ele.
3. **O M2M100 e o OPUS-MT ficam de fora.**
4. **A instrução para os LLMs** (bloco 2) deve pedir "turnos" e os termos de jogo, e
   mandar as linhas vizinhas para os botões de uma palavra.

## Onde estão os arquivos

Fora do git:
- os scripts, em `laboratorios/traducao/`: `medir_traducao.py`, `avaliar_traducao.py` e
  `baixar_modelos.py`;
- os modelos, em `laboratorios/traducao/modelos/`;
- as traduções de cada motor, a amostra cega, a chave, as notas e a página da
  conferência, em `benchmark/dataset/_traducoes/`. As traduções dos pagos ficam guardadas
  para as próximas comparações, sem gastar a cota de novo.
