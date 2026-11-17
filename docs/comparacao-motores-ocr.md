# Comparação de motores de OCR: EasyOCR, RapidOCR e OCR do Windows

*Anexo do [estudo de caso](estudo-de-caso-ocr.md). Medição feita em 16/11/2026, nos 90
prints com gabarito do benchmark, antes de trocar o motor do app.*

> A recomendação abaixo foi aplicada no mesmo dia: o app passou a ler com o RapidOCR
> PP-OCRv6 small. O resultado dele no benchmark completo está em
> [resultados-benchmark.md](resultados-benchmark.md), e o do EasyOCR, em
> [resultados-benchmark-easyocr.md](resultados-benchmark-easyocr.md). O que a troca
> exigiu está em "O que a integração exigiu", mais abaixo.
>
> Os scripts e as saídas desta medição ficam em `laboratorios/`, que não vai para o git,
> assim como os prints dos jogos.

## Recomendação (aplicada)

**Trocar o EasyOCR pelo RapidOCR com o modelo PP-OCRv6 small.** Ele roda na CPU, lê o print no tamanho original, apaga os caracteres chineses, japoneses e coreanos quando a língua de origem usa letras latinas e descarta as caixas com confiança abaixo de 0,7.

| | EasyOCR (até 16/11, GPU MX350) | RapidOCR v6 small |
|---|---|---|
| CER | 10,24% | **7,87%** |
| WER | 22,30% | **12,13%** |
| Palavras do gabarito lidas | 89% | **98%** |
| Palavras de 1 letra | 53% | **91%** |
| Números | 72% | **97%** |
| Quebras de parágrafo achadas / certas | **74%** / 86% | 70% / 86% |
| Tempo por print | 2,88 s (GPU) | **1,08 s (CPU)** |
| Prints melhores / piores (diferença > 0,5 ponto) | – | 58 / 7 |
| Instalador | – | **+27 MB** |
| Licença | Apache-2.0 | Apache-2.0 (código e modelos) |

- **Não combinar os motores.** O teto da combinação, isto é, o melhor dos dois em cada print escolhido com o gabarito na mão, fica só 0,5 ponto de CER abaixo do RapidOCR sozinho. Nenhum seletor prático chega perto disso.
- **Não usar o OCR do Windows**, pelo menos com o pacote pt-BR, o único instalado no PC dos testes. Ele é muito rápido (0,05 s), mas tem 15,8% de CER e só lê 82% das palavras.
- **Os modelos maiores não compensam.** No tamanho original, o PP-OCRv6 medium fica em 8,45% de CER com 10 s por print, e o PP-OCRv5 server em 12,53% com 24 s. Os dois acrescentam de 100 a 150 MB ao instalador e nenhum lê melhor que o small.
- **O PP-OCRv5 mobile en é a alternativa mais leve.** Ele dá 8,77% de CER com 0,86 s por print e acrescenta 13 MB. Mas fica atrás do v6 small em CER, em WER e nos números, e piora mais prints (15 contra 7). O alfabeto dele tem letras acentuadas, só que o modelo foi treinado para inglês, e não medi como ele lê outras línguas. Só vale a pena se os 14 MB a menos pesarem mais que essa diferença.

O que a troca exigiu está em "O que a integração exigiu", mais abaixo.

## Método

- **Prints.** Os 90 prints com gabarito do benchmark, em 12 grupos: `base` mais 11 jogos.
- **Imagem.** Todos os motores recebem a mesma imagem que o app usa, em tons de cinza.
- **Ordem e aquecimento.** Em cada print, os motores rodam um depois do outro, para que o calor da máquina pese igual para todos. Antes de medir, cada motor lê o 1º print uma vez para aquecer. O tempo medido é só a chamada do OCR.
- **EasyOCR.** O cache do EasyOCR (`cinza2`) foi gerado de novo, na mesma execução dos motores novos. O EasyOCR varia um pouco de uma execução para outra. O cache antigo foi preservado em `cinza2_contraste_20261116.json`.
- **Regras do app.** As caixas de cada motor passam pelas mesmas regras do app (`paragrafos.py` + `processador_texto.py`), na variante do `avaliar.py` que reproduz o app: `g+t+h+i+e+c+k2+ap`, `--h-corte 1.0 --v-corte 3.0`. O `comparar.py` confere, print a print, que essa variante aplicada ao EasyOCR dá exatamente o texto do `pipeline_processamento`.
- **Medidas.** CER, WER e quebras saem do `avaliar.py`. Para contar as palavras recuperadas, o texto lido e o gabarito são quebrados em pedaços `[a-z0-9']+` e contados como multiconjunto, sem olhar a ordem. Os casos à parte são as palavras de uma letra e os pedaços que têm algum dígito ("números").
- **Máquina.** O EasyOCR rodou na GPU MX350 e também foi medido na CPU (`easyocr_cpu`). O RapidOCR rodou no ONNX Runtime na CPU, e o OCR do Windows pela API do sistema.
- **Corte de confiança.** O RapidOCR guarda todas as caixas (`text_score 0`), e o corte é aplicado na avaliação (o sufixo `@0.7`). O corte 0,7 foi escolhido antes de olhar os resultados por print. Com 0,8 o CER cai para 7,47%, mas escolher o corte pelo melhor resultado seria ajustar ao próprio dataset.

## Tabela final por motor

As medidas usam as regras do app. "Melhor" e "pior" contam os prints com CER pelo menos 0,5 ponto acima ou abaixo do EasyOCR na GPU. O tempo é a média por print, só do OCR.

"+ Instalador" é o que o motor somaria ao Setup.exe, com os modelos comprimidos em LZMA. O ONNX Runtime (38 MB) já está no build, por causa de outra parte do app. O código do `rapidocr`, mais `omegaconf` e `colorlog`, soma cerca de 1 MB comprimido.

| Motor (modo do cache) | CER | WER | Quebras achadas / certas | Tempo | Melhor / pior | Palavras | 1 letra | Números | + Instalador | Licença |
|---|---|---|---|---|---|---|---|---|---|---|
| **EasyOCR, GPU** (`cinza2`) | 10,24% | 22,30% | 74% / 86% | 2,88 s | – | 89% | 53% | 72% | 0 (já incluso; ~100 MB de modelos baixados na 1ª abertura) | Apache-2.0 |
| EasyOCR, CPU (`easyocr_cpu`) | 10,30% | 22,79% | 73% / 86% | 3,87 s | 4 / 7 | 89% | 53% | 72% | idem | Apache-2.0 |
| **RapidOCR v6 small, tamanho original** (`rapidocr_nativo_lim@0.7`) | **7,87%** | **12,13%** | 70% / 86% | **1,08 s** | **58 / 7** | 98% | 91% | 97% | **+27 MB** | Apache-2.0 |
| RapidOCR v6 small, padrão (amplia o print) (`rapidocr_lim@0.7`) | 9,30% | 13,14% | 71% / 85% | 1,75 s | 55 / 12 | 98% | 89% | 97% | +27 MB | Apache-2.0 |
| RapidOCR v6 medium, padrão (`rapid_v6m_lim@0.7`) | 8,78% | 13,76% | 70% / 83% | 15,81 s | 51 / 14 | 98% | 87% | 97% | +103 MB | Apache-2.0 |
| RapidOCR v6 medium, tamanho original (`rapid_v6m_nativo_lim@0.7`) | 8,45% | 13,12% | 71% / 85% | 10,07 s | 53 / 12 | 98% | 88% | 98% | +103 MB | Apache-2.0 |
| RapidOCR v5 server, padrão (`rapid_v5s_lim@0.7`) | 9,49% | 20,48% | 70% / 82% | 35,09 s | 45 / 29 | 93% | 74% | 88% | +151 MB | Apache-2.0 |
| RapidOCR v5 server, tamanho original (`rapid_v5s_nativo_lim@0.7`) | 12,53% | 24,32% | 70% / 81% | 23,66 s | 42 / 31 | 85% | 64% | 81% | +151 MB | Apache-2.0 |
| RapidOCR v5 mobile en, padrão (`rapid_v5m_en@0.7`) | 10,78% | 16,10% | 70% / 85% | 1,78 s | 48 / 22 | 97% | 87% | 95% | +13 MB | Apache-2.0 |
| RapidOCR v5 mobile en, tamanho original (`rapid_v5m_en_nativo@0.7`) | 8,77% | 13,77% | 69% / 85% | 0,86 s | 57 / 15 | 97% | 89% | 93% | +13 MB | Apache-2.0 |
| RapidOCR v4 mobile en, padrão (`rapid_v4m_en@0.7`) | 9,07% | 20,04% | 70% / 82% | 2,85 s | 51 / 18 | 95% | 85% | 87% | +13 MB | Apache-2.0 |
| RapidOCR v4 mobile en, tamanho original (`rapid_v4m_en_nativo@0.7`) | 9,16% | 17,86% | 69% / 83% | 1,56 s | 49 / 18 | 95% | 86% | 88% | +13 MB | Apache-2.0 |
| OCR do Windows, pt-BR, uma caixa por linha (`windows_linha`) | 15,79% | 27,76% | 69% / 86% | 0,05 s | 21 / 55 | 82% | 86% | 64% | +0,5 MB (pywinrt) | MIT (pywinrt); o OCR é do Windows |
| OCR do Windows, pt-BR, ampliado 2x (`windows_2x`) | 16,77% | 28,18% | 72% / 81% | 0,11 s | 25 / 51 | 84% | 84% | 76% | +0,5 MB | idem |

As linhas da tabela vêm de três saídas: o EasyOCR, o Windows e o v6 small com corte em `saidas/comparar_rodada1.txt` e `saidas/comparar_corte.txt`, os modelos pesados em `saidas/comparar_pesados.txt` e os modelos no tamanho original em `saidas/comparar_nativos.txt`. As versões com outros cortes de confiança, ou sem corte, também estão nesses arquivos.

Notas:
- **"Padrão" e "tamanho original".** Por padrão, o detector do RapidOCR amplia o print até o lado menor ter 736 px. Uma legenda de 1249×193, por exemplo, vira 4763×736. Isso custa tempo e, no v6 small, também piora a leitura. "Tamanho original" usa `Det.limit_type=max` e `Det.limit_side_len=2016`, o que deixa o print do tamanho que está, a não ser que passe de 2016 px.
- **Limpeza de caracteres asiáticos (`_lim`).** Os modelos v6 e v5 server são multilíngues e leem ícones como se fossem caracteres chineses ("口", "三", "然"). A limpeza apaga esses caracteres, o que só faz sentido quando a língua de origem usa letras latinas. Os modelos "en" não produzem esses caracteres.
- **Tempos dos modelos pesados.** Os tempos do v6 medium e do v5 server no modo padrão saíram de uma rodada em que eu rodava análises ao mesmo tempo, então podem estar um pouco altos. Mesmo assim, a rodada no tamanho original, feita sem nada rodando em paralelo, confirma a diferença: o v6 medium é 9 vezes mais lento que o small e o v5 server, 22 vezes.
- **Variação do EasyOCR.** Na CPU, o EasyOCR dá praticamente o mesmo resultado que na GPU. O instalador padrão vem sem GPU, então essa é a referência de quem não tem placa.

## CER médio por jogo

| Jogo (n) | EasyOCR | RapidOCR v6 small (original, ≥0,7) | Windows pt-BR (por linha) |
|---|---|---|---|
| base (3) | 0,70 | **0,08** | 3,30 |
| danganronpa (5) | 1,47 | **0,00** | 4,36 |
| doki (3) | 8,40 | **0,00** | 29,57 |
| eve (12) | 14,64 | **12,85** | 20,37 |
| fallout (8) | 13,90 | **12,95** | 17,61 |
| immortalclan (15) | 1,95 | **0,15** | 6,31 |
| masseffect (5) | **0,56** | 0,74 | 3,34 |
| morrowind (6) | 22,72 | **17,99** | 25,54 |
| nitw (14) | 15,04 | **12,49** | 31,40 |
| persona4 (7) | 6,39 | **3,34** | 11,00 |
| qud (9) | 16,31 | 13,14 | **9,48** |
| undertale (3) | 9,84 | **6,52** | 16,24 |

O RapidOCR ganha em 11 dos 12 grupos. O OCR do Windows só ganha no Caves of Qud, cuja fonte é monoespaçada, e perde em todos os outros. A tabela completa, com todos os modos, está nas saídas.

## Prints em que o RapidOCR mais ganha e mais perde (CER, EasyOCR → RapidOCR)

**Maiores ganhos:**
- `nitw_demontower_titulo`: 16,18 → 0,00
- `doki_legenda_glitch`: 15,38 → 0,00
- `persona4_itens`: 30,52 → 17,53
- `nitw_demontower_intro`: 14,41 → 2,70
- `eve_atributos`: 11,38 → 0,80
- `morrowind_avisos`: 10,38 → 0,00

**Perdas (7 prints pioram mais de 0,5 ponto):**
- `nitw_letreiro_banca`: 86 → 108. Lê mais lixo no texto miúdo do letreiro.
- `eve_skills`: 57 → 68. É uma grade, e as palavras saem em outra ordem.
- `persona4_skills`: 1,16 → 5,81. Perdeu a palavra "List".
- `fallout_pipboy`: 46,6 → 49,3.
- `undertale_legenda_2`: 6,67 → 8,89. Na fonte de pixel, o apóstrofo vira "·" ("IT·S").
- `masseffect_aviso`: 0 → 2,08. "Press to" vira "Pressto", com o espaço do ícone perdido.
- `morrowind_status`: 68,3 → 69,9. Os números e as palavras estão todos certos; só a ordem diverge.

**Palavras que faltam no texto lido** (detalhe em `saidas/teto_motores.txt`):
- **EasyOCR:** 494 de 4548. Dessas, 270 nem foram lidas: 95 de uma letra e 51 números.
- **RapidOCR:** 105 de 4548. Só 68 não foram lidas.
- **Windows:** 806 de 4548.

O ganho maior do RapidOCR é justamente nas palavras de uma letra ("I", "a") e nos números isolados, que o detector do EasyOCR muitas vezes nem enxerga.

## Combinações testadas (EasyOCR + RapidOCR v6 small)

Os resultados estão em `saidas/comparar_corte.txt`. As mesmas combinações com o v6 medium estão em `saidas/comparar_nativos.txt` e dão o mesmo quadro: no melhor caso, escolhendo com o gabarito ("oráculo"), o CER chega a 7,42%.

| Combinação | CER | Observação |
|---|---|---|
| União: caixas do EasyOCR + caixas do Rapid com conf ≥ 0,5 que o EasyOCR não cobriu | 10,30% | Pior que o EasyOCR sozinho. As caixas extras entram fora de ordem. |
| Escolher o motor por print pela confiança média | 7,87% | Escolhe sempre o RapidOCR, cuja confiança é sempre maior. Dá o mesmo que usar só ele, com o dobro do tempo. |
| Usar o RapidOCR só quando a letra é pequena (altura mediana < 22 px) | 9,61% | Melhor que o EasyOCR, pior que o RapidOCR sozinho. |
| Oráculo: o menor CER em cada print, escolhido com o gabarito | 7,35% | É o teto da combinação, inalcançável na prática. Fica só 0,5 ponto abaixo do RapidOCR sozinho. |
| Oráculo EasyOCR + Windows | 8,63% | Não há seletor: o OCR do Windows não dá confiança. |

**Conclusão:** combinar não compensa. Rodar os dois motores dobra o tempo, e o melhor resultado possível mal passa o RapidOCR sozinho.

## OCR do Windows

- **Língua.** Só testei o pacote **pt-BR**, o único instalado no PC dos testes. Instalar o pacote de OCR em inglês mexe no sistema, então ficou de fora. Há duas formas:
  - em Configurações → Hora e idioma → Idioma e região, adicionar o inglês (EUA) com o recurso de reconhecimento de texto;
  - num PowerShell como administrador: `Add-WindowsCapability -Online -Name "Language.OCR~~~en-US~0.0.1.0"`.
- **O que o pacote em inglês mudaria.** Com o pacote em inglês, o reconhecedor deixaria de "corrigir" para palavras do português. A distância para o RapidOCR, porém, vem sobretudo das palavras que ele nem lê (7% do total) e dos números (só 64% lidos). Por isso é improvável que a troca de pacote feche a diferença, mas isso não foi medido.
- **Pontos a favor:** custa 0 MB de modelos, cerca de 0,5 MB do `winrt`, e é 20 vezes mais rápido que o RapidOCR.
- **Pontos contra:**
  - depende do pacote de língua que cada usuário tem instalado;
  - não dá confiança por caixa;
  - só vem no Windows 10 e no 11.
- **Formas de agrupar as palavras.** O OCR do Windows devolve palavras soltas. Testei três formas de juntá-las em caixas (`windows`, `_pal`, `_v10` e `_linha`, gerados pelo `derivar_windows.py`): a diferença entre elas é menor que 1 ponto de CER.

## Tamanho, licença e línguas

- **Tamanho de cada modelo.** Os números abaixo são o modelo cru → comprimido em LZMA:
  - v6 small: 31,2 → 26,0 MB;
  - v6 medium: 138,7 → 102,3 MB;
  - v5 server: 172,7 → 150,1 MB;
  - v5 mobile en: 12,7 → 11,7 MB;
  - v4 mobile en: 12,4 → cerca de 11,5 MB.

  O código soma cerca de 1 MB a qualquer um deles.
- **Instalador.** O instalador de 15/11 tinha 383 MB; com o RapidOCR, o de 16/11 ficou com 413,5 MB. Trocar o EasyOCR **não** tira o torch do instalador, porque o Argos (stanza) e o BERT opcional também usam. Em compensação, deixa de ser preciso baixar os modelos do EasyOCR (cerca de 100 MB) na 1ª abertura. O pacote de GPU (2,5 GB) também deixa de ser necessário para o OCR, porque o RapidOCR na CPU é mais rápido que o EasyOCR na GPU MX350.
- **Licenças:**
  - `rapidocr`: Apache-2.0;
  - modelos PaddleOCR no ModelScope: Apache License 2.0;
  - `onnxruntime`: MIT;
  - `omegaconf`: BSD-3-Clause;
  - `colorlog`: MIT;
  - `winrt` (pywinrt): MIT;
  - EasyOCR: Apache-2.0.
- **Línguas.** O PP-OCRv6 small (multi) cobre chinês simplificado e tradicional, japonês, inglês e cerca de 45 línguas de alfabeto latino, entre elas português, espanhol, francês, alemão, italiano, polonês, turco e vietnamita. O app tem 83 línguas em `idiomas.json`. As escritas cirílica, árabe, coreana, devanágari, tailandesa, grega e outras exigiriam modelos de reconhecimento PP-OCRv5 mobile por escrita, de cerca de 8 MB cada. Esses modelos podem ser baixados sob demanda, como o app já faz com o EasyOCR.

## O que a integração exigiu

A troca foi feita em 16/11/2026, logo depois desta medição.

1. **Regras de quebra de parágrafo.**
   - O que mudou: as quebras achadas caem de 74% para 70%. As regras foram ajustadas
     nas caixas do EasyOCR, e a caixa do RapidOCR tem outra forma: é cerca de 11% mais
     alta, com o topo mais acima, e cerca de 0,12 altura mais larga.
   - O que foi testado: as constantes do `paragrafos.py`, uma a uma, sobre a leitura do
     RapidOCR. Nenhuma mudou o resultado mais que 0,2 ponto, e as regras ficaram como
     estavam.
   - De onde vem a queda: quase toda da grade de skills do EVE (`eve_skills`). O
     RapidOCR lê as contagens pequenas entre as colunas, e elas tapam o vão que o corte
     XY usava para separar os blocos.
2. **Caracteres chineses, japoneses e coreanos.** Feito: o app os apaga quando a língua
   de origem não é chinês nem japonês.
3. **Corte de confiança.** Feito: o app descarta as caixas com confiança abaixo de 0,7.
4. **Detector no tamanho original.** Feito: `Det.limit_type=max` e
   `Det.limit_side_len=2016`.
5. **Casos conhecidos:**
   - o apóstrofo em fonte de pixel que vira "·": resolvido com uma regra nova, só nas
     contrações conhecidas ("IT·S" vira "IT'S");
   - o espaço que some junto a um ícone ou entre palavras ("Pressto", "resteasy"):
     continua;
   - o lixo em texto miúdo de fundo (o letreiro do NITW): continua.
6. **Línguas fora do PP-OCRv6.** O app lê com o RapidOCR as 43 línguas do `idiomas.json`
   que o modelo cobre: inglês, chinês, japonês e 40 de alfabeto latino. As outras 40
   continuam no EasyOCR. Os modelos PP-OCRv5 por escrita não foram medidos.
7. **Na CPU, sem GPU.** O RapidOCR roda no ONNX Runtime na CPU. O
   `onnxruntime-gpu`/DirectML não foi testado.

Com a troca feita, o benchmark completo deu CER de 7,82%, WER de 12,00%, 70% das quebras
achadas e 86% certas, a 1,2 s por print.

## Arquivos

Ficam todos em `laboratorios/`, fora do git: só existem no PC onde a medição foi feita.

- `ocr_alternativos/env/`: ambiente separado. Tem só os pacotes novos (`rapidocr` 3.10.0, `omegaconf`, `colorlog` e `winrt-*` 4.x) e enxerga os pacotes do env do projeto pelo `zz_env_projeto.pth`. Os modelos baixados ficam em `env/Lib/site-packages/rapidocr/models/`.
- `ocr_alternativos/motores.py`: as classes `MotorRapid` (os modos de `CONFIGS_RAPID`) e `MotorWindows`, com a mesma saída do `MotorOCR` do app.
- `ocr_alternativos/cache_motores.py`: roda os motores nos 90 prints e grava `laboratorios/quebras/cache/<modo>.json`.
- `ocr_alternativos/derivar_windows.py`: gera outras formas de juntar as palavras do OCR do Windows.
- `ocr_alternativos/ajustar_rapid.py`: gera `<modo>_lim` (sem caracteres asiáticos) e `<modo>_lim_aj` (o mesmo, com a geometria ajustada).
- `ocr_alternativos/comparar.py`: as tabelas, os ganhos e perdas e as combinações. O sufixo `@0.7` aplica o corte de confiança.
- `ocr_alternativos/saidas/`:
  - registros das rodadas: `cache_rodada{1,2,3}.txt`;
  - comparações: `comparar_rodada1.txt`, `comparar_corte.txt`, `comparar_ajustes.txt`, `comparar_pesados.txt` e `comparar_nativos.txt`;
  - textos lado a lado: `diff_easy_rapid.txt`;
  - palavras que faltam: `teto_motores.txt`;
  - palavras cruas do Windows: `windows*_palavras.json`.
- `quebras/cache/`: os caches novos.
  - O `cinza2.json` foi refeito nesta execução; o anterior está em `cinza2_contraste_20261116.json`.
  - Os demais caches dos motores: `easyocr_cpu`, `rapidocr*`, `rapid_*` e `windows*`.

Para refazer, a partir de `tradutor_gameplay/`:

```bash
laboratorios/ocr_alternativos/env/Scripts/python.exe laboratorios/ocr_alternativos/cache_motores.py cinza2,easyocr_cpu,rapidocr,rapidocr_nativo,windows,windows_2x
```

```bash
laboratorios/ocr_alternativos/env/Scripts/python.exe laboratorios/ocr_alternativos/ajustar_rapid.py rapidocr_nativo
```

```bash
laboratorios/ocr_alternativos/env/Scripts/python.exe laboratorios/ocr_alternativos/comparar.py --modos cinza2,rapidocr_nativo_lim@0.7,windows_linha --combos rapidocr_nativo_lim@0.7
```
