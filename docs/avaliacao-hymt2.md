# O Hy-MT2 1.8B, avaliado para o app

*27/11/2026. Continua [Os tradutores, lado a lado](comparacao-tradutores.md), de 26/11, que
mediu a qualidade e deixou o Hy-MT2 como candidato a offline de qualidade. Aqui entram as
medidas que faltavam para decidir: a velocidade em cada modo de pedido, as placas de vídeo,
a memória, o tamanho e a licença. A ideia do dono do projeto é ter o Hy-MT2 ao lado do
Argos, sem tirar o Argos.*

## Resumo

| | Argos | Hy-MT2 1.8B |
|---|---|---|
| Nota média (26/11) | 3,83 | **4,08** |
| Erros graves, nota 1 ou 2 (26/11) | 20% | **11%** |
| Uma tela típica (mediana dos 30 prints) | **0,5 s** | 4,5 s, com 4 pedidos ao mesmo tempo |
| As telas mais longas (1 em cada 10) | – | 10 s ou mais |
| Download | **81 MB por par** | 1,13 GB, mais 25 MB do llama.cpp |
| Memória | – | 1,9 a 2,6 GB de RAM |
| Licença | MIT; modelos CC-BY 4.0 (crédito) | Apache 2.0 (aviso de copyright) |

- **O Hy-MT2 pode entrar ao lado do Argos**, como um segundo modo offline, de download
  opcional: o Argos fica como o rápido e leve, e o Hy-MT2 como o de qualidade. A licença
  permite, inclusive num app vendido sob a GPL-3.0.
- **O melhor modo é mandar as linhas da tela ao mesmo tempo**, em 4 pedidos: 0,50 s por
  linha, 31% menos que uma linha por vez, com a mesma qualidade.
- **Mandar a tela inteira num pedido só não compensa agora.** Fica quase igual em tempo
  (−5%) e, em 2 dos 30 prints, o modelo juntou duas linhas numa e deslocou todas as de
  baixo.
- **Mais threads não ajudam.** Com 8 em vez de 4, o tempo ficou igual.
- **Neste PC, nenhuma placa de vídeo ganha do processador.** A MX350 está sendo freada pela
  temperatura do notebook (de 139 a 531 MHz, de um máximo de 1.594), e a Iris Xe gera o
  texto mais devagar que o processador. As placas vão para o bloco de aceleração, separado
  em 27/11.
- **Serve para ler com calma** (menus, fichas, diálogos), não para legendas que passam
  rápido. O cache do bloco 1 deixa instantâneas as linhas que já apareceram.

## Como foi medido

- **O texto:** os gabaritos de 30 dos 150 prints do benchmark (um a cada 5, na ordem da
  medida de 26/11), com 305 linhas: 10 fichas, 7 textos, 7 legendas, 3 menus e 3 letreiros;
  28 em inglês e 2 em espanhol. A mediana é de 5,5 linhas por print, e o maior tem 44.
- **O modelo:** o mesmo `Hy-MT2-1.8B-Q4_K_M.gguf` de 26/11, no servidor local do llama.cpp
  (b12751), com 4.096 de contexto, a instrução e os parâmetros do README do modelo
  (temperature 0,7, top_p 0,6, top_k 20, repetition_penalty 1,05) e um pedido de
  aquecimento antes de medir.
- **O PC:** o mesmo de 26/11 (Intel de 11ª geração, 4 núcleos e 8 threads, 11 GB de RAM),
  com a Intel Iris Xe e a NVIDIA GeForce MX350 de 2 GB, ligado na tomada. Nada mais rodava,
  e nenhum jogo estava aberto.
- **Os modos:**
  - **linha:** uma linha por pedido, uma depois da outra, como em 26/11;
  - **4 ao mesmo tempo:** as linhas de um print em 4 pedidos simultâneos, em 4 vagas do
    servidor;
  - **tela:** o print inteiro num pedido, uma linha do original por linha da tradução.
- **As placas:** o processador (versão CPU do llama.cpp, 25 MB), a Iris Xe e a MX350 pelo
  Vulkan (39 MB) e a MX350 pelo CUDA 12.4 (359 MB, mais 391 MB das bibliotecas da NVIDIA).
  O CUDA 13 não serve para a MX350: ele deixou de atender a geração dela (Pascal).
- **O tempo da geração pura**, sem o servidor, pelo `llama-bench`: 128 tokens de entrada e
  64 de saída, 3 repetições.

## A velocidade no processador

| Modo | Segundos por linha | Mediana por print | 3 em cada 4 prints até | 9 em cada 10 até | Pior print | Linhas no lugar |
|---|---:|---:|---:|---:|---:|---:|
| linha, 4 threads | 0,73 | 5,5 s | 10,7 s | 19,6 s | 27,5 s | 30/30 |
| linha, 8 threads | 0,74 | 6,6 s | – | – | 28,3 s | 30/30 |
| **4 ao mesmo tempo** | **0,50** | **4,5 s** | **6,9 s** | **10,5 s** | **18,2 s** | 30/30 |
| tela | 0,70 | 5,2 s | 8,7 s | 14,8 s | 34,6 s | 28/30 |

Nos mesmos 30 prints, para comparar:

| Motor | Segundos por linha | Mediana por print | Pior print |
|---|---:|---:|---:|
| Argos (26/11) | 0,14 | 0,5 s | 14,5 s (a carga do modelo) |
| Hy-MT2, linha (26/11) | 0,61 | 4,5 s | 27,2 s |
| Google Cloud (26/11, com a rede) | 0,06 | 0,6 s | 0,8 s |
| DeepL (26/11, com a rede) | 0,12 | 1,1 s | 1,8 s |
| Azure (26/11, com a rede) | 0,17 | 1,3 s | 3,2 s |

- **O tempo está em gerar a tradução**, não em ler o pedido. No `llama-bench`, o
  processador lê 117 tokens por segundo e gera 25. É por isso que a tela num pedido só
  quase não ganha: o texto a gerar é o mesmo.
- **8 threads não ajudam** porque a geração é limitada pela velocidade da memória, não
  pelos núcleos.
- **4 ao mesmo tempo ajudam** porque a cada leitura dos pesos do modelo na memória saem 4
  tokens em vez de 1: o servidor passou de 15 para 22 tokens por segundo de saída.
- **A mesma medida variou 20% de um dia para o outro:** nos mesmos 30 prints, o modo linha
  deu 0,61 s por linha em 26/11 e 0,73 s hoje. As diferenças pequenas entre os modos devem
  ser lidas com essa margem; a dos 4 ao mesmo tempo (−31%) passa dela.

## A tela num pedido só

Antes da medida, um piloto de 10 prints testou quatro jeitos de separar as linhas. As
linhas ficaram no lugar em 10 dos 10 prints com a instrução normal e uma linha por linha;
em 10 com a instrução "Delimiters" do README e a barra ( | ); em 9 com o `<br>`; e em 5 com
a instrução "Delimiters" e a quebra de linha. A medida usou o primeiro, o mais simples.

Nos 30 prints, o modelo juntou duas linhas numa em 2:
- numa ficha do EVE Online, o nome de um plano e a duração dele, que no jogo ficam lado a
  lado;
- na ficha de criação do Stardew Valley em espanhol, dois rótulos seguidos, que viraram um
  só.

Depois da junção, cada tradução fica uma linha acima do original até o fim da tela. No
app, que mostra a tradução de cada linha, isso põe o texto errado em todas as de baixo.

O contexto da tela mudou as palavras de muitas linhas: só 109 das 233 linhas dos prints
que ficaram no lugar saíram iguais às de 26/11, contra 245 de 305 na nova rodada linha a
linha. Se o contexto melhora ou piora a tradução, só uma avaliação às cegas diz. Fica para
o bloco 2, que vai mandar contexto aos modelos: o README do Hy-MT2 tem uma instrução que
manda as linhas vizinhas como informação de fundo e traduz uma linha só, sem o risco de
deslocar as outras.

## As placas de vídeo

| Placa | linha | tela | 4 ao mesmo tempo | Leitura (tokens/s) | Geração (tokens/s) |
|---|---:|---:|---:|---:|---:|
| **Processador** (4 threads) | **0,73** | **0,70** | **0,50** | 117 | **24,7** |
| Iris Xe, pelo Vulkan | 1,00 | 0,89 | 0,69 | **239** | 16,9 |
| MX350, pelo Vulkan | 1,64 | 1,26 | 1,38 | 107 | 9,7 |
| MX350, pelo CUDA | 3,04 | 3,30 | 1,82 | 200 | 4,8 |

Segundos por linha nos 30 prints; leitura e geração pelo `llama-bench`.

- **A MX350 está freada pela temperatura.** Durante a medida, o driver da NVIDIA informou
  `SW Thermal Slowdown` o tempo todo, com a placa a 67 °C: o relógio ficou entre 139 e 531
  MHz (o máximo é 1.594) e a memória caiu várias vezes para 810 MHz (o máximo é 3.504). O
  notebook estava na tomada, com a bateria em 100%. É um limite deste notebook, que
  segura a placa abaixo dessa temperatura, e não do CUDA nem do modelo.
- **A Iris Xe lê o pedido duas vezes mais rápido** que o processador, mas gera o texto mais
  devagar, e a geração é a maior parte do tempo.
- **A primeira carga pelo CUDA levou 32 s**; as seguintes, de 2 a 3 s.
- **Este PC não diz nada sobre placas maiores.** Uma placa de jogo atual tem memória muito
  mais rápida, e a conta muda. Mas, com um jogo aberto, a placa está ocupada com o jogo.
- **O tamanho conta para o instalador:** o llama.cpp para o processador tem 25 MB; para o
  Vulkan, 39 MB; para o CUDA, 750 MB, quase tudo das bibliotecas da NVIDIA, que têm licença
  própria.

Hoje, o app só usa o CUDA no EasyOCR, pelo PyTorch com CUDA, que o usuário baixa depois da
instalação. A escolha das placas para o OCR e para a tradução fica para o bloco de
aceleração (veja [O que entra na primeira build](estudo-de-concorrentes.md#o-que-entra-na-primeira-build)).

## A memória e o tamanho

| Contexto | RAM depois de uma tradução | Memória própria do servidor | Carga |
|---:|---:|---:|---:|
| 4.096 | 2.117 MB | 1.150 MB | 1,6 s |
| 2.048 | 1.989 MB | 1.020 MB | 1,3 s |
| 1.024 | 1.925 MB | 954 MB | 1,3 s |

- **Depois dos 30 prints**, o servidor estava com 2,3 a 2,4 GB de RAM; com 4 pedidos ao
  mesmo tempo, 2,6 GB. Em 26/11, depois das 1.300 linhas, estava com 3,2 GB.
- **Um contexto menor poupa uns 200 MB.** Uma linha de jogo cabe com folga em 1.024.
- **No disco:** 1,13 GB do modelo e 64 MB do llama.cpp para o processador (25 MB
  compactado).

## A licença

- **O modelo é Apache 2.0.** Os dois repositórios da Tencent no Hugging Face
  (`tencent/Hy-MT2-1.8B` e `tencent/Hy-MT2-1.8B-GGUF`) têm um `LICENSE.txt` com o texto da
  Apache 2.0 sem mudanças, depois de uma abertura da Tencent e da linha "Copyright (C) 2026
  Tencent. All rights reserved." Não há termos extras: nenhum país excluído, nenhum limite
  de usuários, nenhuma política de uso. Não há arquivo NOTICE. Conferido em 27/11.
- **Dá para usar num app GPL-3.0 vendido.** A Apache 2.0 é compatível com a GPL-3.0. O que
  ela pede é levar uma cópia da licença e manter o aviso de copyright, como o crédito do
  OPUS-MT que já está no README e na tela de configurações.
- **O llama.cpp é MIT**, que também pede o aviso de copyright. A versão para o processador
  traz o `libomp.dll`, do LLVM, com licença própria (`LICENSE-LLVM-OpenMP`), que vai junto.
- **Um concorrente já usa o Hy-MT2:** o Screen Translator, da JinSoft, que ainda não está à
  venda ([Os concorrentes](estudo-de-concorrentes.md#os-concorrentes)).

## O que isso muda

1. **No app, por enquanto, nada.** O Argos continua sendo o offline.
2. **O Hy-MT2 pode entrar como um segundo offline**, de download opcional (1,1 GB), com as
   linhas da tela em 4 pedidos ao mesmo tempo e o llama.cpp para o processador. A decisão
   de quando entra fica com o dono do projeto.
3. **Junto com o cache do bloco 1**, as linhas que já apareceram saem na hora. Outra ideia,
   ainda não medida: mostrar a tradução do Argos na hora e trocar pela do Hy-MT2 quando ela
   chegar.
4. **O sorteio das palavras** (temperature 0,7, a recomendada) muda 20% das linhas de uma
   rodada para outra. No modo automático, a mesma tela poderia mudar de tradução a cada
   leitura. O cache resolve; a temperature 0, que sempre dá a mesma tradução, precisaria de
   uma avaliação da qualidade antes.
5. **A tela num pedido só fica de fora.** O contexto entra no bloco 2, pela instrução que
   manda as linhas vizinhas sem pedir a tradução delas.
6. **As placas de vídeo vão para o bloco de aceleração.** Neste PC, o processador é o mais
   rápido.

## O que não foi medido

- **Com um jogo aberto.** O Hy-MT2 ocupa 4 threads por alguns segundos a cada tela, e o
  jogo pode engasgar. Precisa de um teste com o dono do projeto jogando.
- **Com o texto do OCR**, que tem os erros da leitura. A medida parte do gabarito.
- **A qualidade dos modos novos**, às cegas. As checagens automáticas deram os mesmos
  problemas na linha e nos 4 ao mesmo tempo (8 linhas iguais ao original em 305) e 6 na
  tela (em 233 linhas no lugar).
- **As versões menores do modelo.** A Tencent publica o Hy-MT2 1.8B também em Q6_K (1,47
  GB) e Q8_0 (1,91 GB), e em repositórios à parte, em 2 bits e em 1,25 bit (440 MB). Uma
  versão menor gera mais rápido no processador, mas a qualidade precisa ser medida.

## Onde estão os arquivos

Fora do git:
- o script, em `laboratorios/traducao/velocidade_hymt2.py`;
- os resultados de cada modo e placa, em
  `benchmark/dataset/_traducoes/hymt2_<modo>_<placa>_t<threads>.json`;
- o llama.cpp para o Vulkan e para o CUDA, em `laboratorios/traducao/modelos/llama.cpp-vulkan`
  (107 MB) e `laboratorios/traducao/modelos/llama.cpp-cuda` (1,4 GB), baixados em 27/11 do
  GitHub do ggml-org, com os hashes conferidos.
