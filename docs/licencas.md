# Licenças: o que o app usa e o que isso permite

*Levantamento de 25/11/2026, para quando o app for distribuído ou vendido. Complementa
[bibliotecas e ferramentas](bibliotecas-e-ferramentas.md), que conta por que cada peça
entrou ou saiu.*

> **Não é parecer jurídico.** É um inventário para orientar a decisão e mostrar o que
> falta conferir. Antes de vender, as licenças e os termos marcados como "a conferir"
> precisam ser lidos na fonte, de preferência com ajuda especializada.

**De onde vêm os dados:**
- **Bibliotecas:** a lista do que vai no instalador saiu do executável de 16/11/2026 (o
  último build), lida com o `pyi-archive_viewer` do PyInstaller e cruzada com a pasta
  `_internal`. A licença de cada uma saiu dos metadados do pacote instalado no `env_build`,
  o ambiente do build.
- **Modelos:** dos arquivos baixados neste PC e das páginas oficiais, quando indicadas.
- **Serviços:** da busca nas páginas dos termos. O que não foi lido na fonte está marcado.

## Resumo

- **O projeto é GPLv3** (arquivo `LICENSE`). Tudo o que vai no instalador é compatível com a
  GPLv3: 127 das 137 bibliotecas têm licença permissiva (MIT, BSD, Apache, PSF, ISC), e as
  outras 10 são LGPL, MPL, GPL ou AGPL, que a GPLv3 aceita.
- **Vender com o código aberto pode.** A GPLv3 permite cobrar pelo app. Em troca, quem
  recebe o app tem direito ao código-fonte (o repositório público é o jeito usual de cumprir
  isso), e os avisos de licença e os créditos exigidos têm de ir junto.
- **Uma versão fechada, hoje, não daria.** Duas bibliotecas têm licença que, pelo
  entendimento comum, obriga o programa que as inclui a ser aberto: o `minisbd` (AGPL-3.0),
  que vem com o Argos Translate, e o `Levenshtein` (GPL-2.0 ou posterior), que entra no
  pacote sem o app usar. O PySide6 serviria pela LGPLv3, com as obrigações dela.
- **Falta conferir antes de vender:**
  - a licença dos pesos dos modelos do EasyOCR;
  - os termos de cada tradutor (o Google grátis, que usava um endereço não oficial, saiu
    do app em 27/11/2026);
  - a licença de cada modelo do Argos: os pares inglês → português do Brasil e espanhol →
    inglês vêm do OPUS-MT (CC-BY 4.0); os outros pares não foram vistos.

## 1. Bibliotecas que vão no instalador

### As que o código do app usa

| Biblioteca | Versão | Licença | Para quê |
|---|---|---|---|
| PySide6 (e shiboken6) | 6.11.1 | LGPL-3.0 ou GPL-2.0 ou GPL-3.0, à escolha | Interface |
| mss | 10.2.0 | MIT | Captura de tela |
| opencv-python-headless | 4.13.0.92 | Apache-2.0 | Imagem |
| numpy | 2.4.6 | BSD-3-Clause, com partes 0BSD, MIT, Zlib e CC0 | Contas |
| rapidocr | 3.10.0 | Apache-2.0 | OCR principal |
| onnxruntime | 1.31.1 | MIT | Roda os modelos do RapidOCR |
| omegaconf, colorlog | 2.4.0, 6.12.0 | BSD, MIT | Vêm com o RapidOCR |
| easyocr | 1.7.2 | Apache-2.0 | OCR das outras escritas |
| torch, torchvision | 2.6.0, 0.21.0 | BSD-3-Clause, BSD | EasyOCR, Argos e BERT |
| python-bidi | 0.6.10 | LGPL | Vem com o EasyOCR (escrita da direita para a esquerda) |
| pyspellchecker | 0.9.0 | MIT | Dicionário das letras confundidas |
| transformers | 5.12.1 | Apache-2.0 | BERT, opcional |
| requests | 2.34.2 | Apache-2.0 | APIs da Azure, do DeepL e do Google Cloud |
| argostranslate | 1.11.0 | MIT (o projeto diz MIT ou CC0) | Tradução offline |
| ctranslate2, sentencepiece, stanza, spaCy, sacremoses | — | MIT, Apache-2.0, Apache-2.0, MIT, MIT | Vêm com o Argos |
| **minisbd** | 0.9.5 | **AGPL-3.0** | Vem com o Argos (divide o texto em frases) |

### As que vão junto sem o app usar

O PyInstaller põe no pacote tudo o que alguma biblioteca importa, mesmo que o app nunca
chegue lá. No instalador de 16/11 estão:
- **o `Levenshtein`** (GPL-2.0 ou posterior), puxado por um tokenizador do Transformers que
  o app não usa;
- **o `astroid`** (LGPL-2.1 ou posterior), puxado pelo `asttokens`, que vem com o IPython;
- **o IPython, o Jupyter** (`nbconvert`, `nbformat`, `jupyter_client`), **o `jedi`, o
  scikit-learn e o torchaudio**, todos com licença permissiva.

Eles não mudam o que a GPLv3 permite, mas aumentam o instalador e, no caso do
`Levenshtein`, impediriam uma versão fechada. Tirá-los é uma limpeza a fazer no `.spec`, com
o instalador refeito e testado depois.

### As outras

As demais dependências que vão no pacote têm licença permissiva (MIT, BSD, Apache-2.0, PSF,
ISC), menos duas com MPL-2.0: o `certifi` (os certificados das conexões seguras) e parte do
`tqdm`. A MPL-2.0 vale arquivo por arquivo: pede que o código desses arquivos fique
disponível para quem recebe o app, e o arquivo de avisos de terceiros (seção 6) pode dizer
onde ele está.

A lista completa, com versão e licença de cada uma das 137, está no anexo, no fim.

## 2. Modelos

| Modelo | Como chega ao usuário | Licença | Conferido? |
|---|---|---|---|
| PP-OCRv6 small (RapidOCR) | Dentro do instalador | Apache-2.0 (código e modelos) | Sim, em 16/11 ([comparação de motores](comparacao-motores-ocr.md)) |
| Detector CRAFT e leitores do EasyOCR | Baixados pelo próprio EasyOCR na 1ª vez que a língua é usada | O código do EasyOCR é Apache-2.0, e o do CRAFT, da NAVER, é MIT. A licença dos pesos não está escrita numa fonte primária | **A conferir** |
| bert-base-uncased | Baixado do Hugging Face na 1ª vez que a correção por contexto é ligada | Apache-2.0, pela marcação do repositório do modelo, que tem um arquivo `LICENSE` | Em parte: o texto do arquivo não foi lido |
| Modelos do Argos Translate | Baixados do índice do Argos na 1ª tradução de cada par | Os pares inglês → português do Brasil e espanhol → inglês, baixados neste PC, dizem que vêm do OPUS-MT (Jörg Tiedemann e Santhosh Thottingal, Universidade de Helsinque) e que o original é CC-BY 4.0, que exige dar o crédito. O crédito está no README e na descrição do motor offline, na tela de configurações (27/11). Os outros pares não foram vistos | Esses dois pares |
| PyTorch com CUDA (pacote de GPU) | Baixado do site oficial do PyTorch, se o usuário pedir | BSD-3-Clause; traz bibliotecas da NVIDIA, que têm licença própria | **A conferir** a parte da NVIDIA |

Só o PP-OCRv6 vai dentro do instalador. Os outros o próprio usuário baixa da fonte oficial
quando usa, o que é diferente de o app redistribuir os arquivos.

## 3. Tradutores

| Serviço | Quem tem o contrato | O que se sabe |
|---|---|---|
| **Google Tradutor grátis** | Ninguém: não havia contrato de API | **Saiu do app em 27/11/2026**, para o app poder ser vendido sem depender dele. O app pedia a tradução à página do Google Tradutor (até 26/11, pelo deep-translator), que não é uma API oficial. Os termos de serviço do Google de 2017 a 2020 proibiam acessar os serviços por outro meio que não a interface e as instruções do próprio Google; o texto atual não foi conferido. O app já trata o bloqueio: depois de um CAPTCHA, o Google fica de fora 10 minutos, e a pausa dobra a cada bloqueio seguido, até 6 horas. O app não contorna o CAPTCHA nem se passa por navegador. **É o ponto mais frágil para vender** |
| **Azure Translator** | O usuário, com a chave dele | O app só chama a API em nome do usuário. Os termos não foram lidos para este doc |
| **DeepL API** | O usuário, com a chave dele | Os termos dos serviços grátis do DeepL dizem que o texto pode ser usado para treinar os modelos e proíbem conteúdo confidencial ou pessoal. O documento específico da API Free não foi lido |
| **Google Cloud Translation** | O usuário, com a chave dele | Os termos não foram lidos para este doc |
| **Argos Translate (offline)** | — | Roda no PC; vale a licença de cada modelo (seção 2) |

Como cada usuário usa a própria chave, o contrato com a Azure, o DeepL e o Google Cloud é
dele. O que cabe ao app é não prometer o que o serviço não permite e deixar claro, na tela
de configuração, que a chave e o uso são do usuário.

## 4. Build

| Programa | Licença | O que significa |
|---|---|---|
| PyInstaller | GPL-2.0 ou posterior, com uma exceção | A exceção permite usar o PyInstaller para montar e distribuir programas de qualquer licença, inclusive comerciais |
| NSIS | zlib/libpng (os módulos de compressão bzip2 e LZMA têm licenças próprias) | Livre para gerar e distribuir instaladores. Conferido em fontes secundárias e na página do projeto no SourceForge |
| Python | PSF | Permissiva |

As ferramentas de desenvolvimento (Pylint, Pyright, Git) não vão para o usuário.

## 5. O que isso permite

**Vender o app como ele é (GPLv3):**
- pode cobrar;
- quem compra tem direito ao código-fonte, sob a mesma licença, e pode redistribuí-lo; o
  repositório público é o jeito usual de entregar o código;
- os avisos de licença das bibliotecas e os créditos exigidos (como o CC-BY dos modelos do
  OPUS-MT, que desde 27/11 está no README e na tela de configurações) têm de ir junto. Hoje o instalador leva só parte dos arquivos de licença das
  bibliotecas: um arquivo de avisos de terceiros no instalador resolveria isso.

**Uma versão fechada exigiria, no mínimo:**
- trocar o Argos ou o `minisbd` (AGPL-3.0);
- tirar o `Levenshtein` do pacote (GPL);
- usar o PySide6 pela LGPLv3, com o Qt em arquivos separados, que o usuário possa trocar (o
  build em pasta já faz assim), ou comprar a licença comercial do Qt;
- conferir os pesos do EasyOCR e os termos dos tradutores.

## 6. O que fazer antes de distribuir

1. Tirar do instalador as bibliotecas que vão sem uso (seção 1), refazendo e testando o
   instalador.
2. Pôr no instalador um arquivo de avisos de terceiros, com as licenças e os créditos.
3. Conferir na fonte: os pesos do EasyOCR, os termos da Azure, do DeepL e do Google
   Cloud, os modelos do Argos que o app baixa e as bibliotecas da NVIDIA do pacote
   de GPU.
4. O Google grátis numa versão paga: resolvido em 27/11/2026, quando ele saiu do app.

## Fontes

- Bibliotecas: metadados dos pacotes do `env_build` e a lista do executável de 16/11 (no PC).
- Modelo do Argos inglês → português do Brasil: `README.md` do pacote baixado (no PC).
- EasyOCR: [README do projeto](https://raw.githubusercontent.com/JaidedAI/EasyOCR/master/README.md);
  CRAFT: [repositório da NAVER (clovaai) indexado no ecosyste.ms](https://awesome.ecosyste.ms/projects/1051672).
- BERT: [histórico do arquivo LICENSE no repositório do modelo](https://huggingface.co/google-bert/bert-base-uncased/commits/main/LICENSE).
- Argos Translate: [README do projeto](https://raw.githubusercontent.com/argosopentech/argos-translate/master/README.md).
- Google: [termos de serviço de 2017 a 2020 (arquivo)](https://policies.google.com/terms/archive/20171025-20200331?l=en).
- DeepL: [termos dos serviços grátis](https://www.deepl.com/en/terms-of-use).
- NSIS: [página do projeto no SourceForge](https://sourceforge.net/p/nsis/).

## Anexo: as 137 bibliotecas do instalador de 16/11

A licença é a dos metadados de cada pacote. Quando o campo de licença vem vazio ou genérico,
vale a classificação do pacote, entre parênteses. Refazer a lista depois de cada build.

| Biblioteca | Versão | Licença (metadados) |
|---|---|---|
| annotated-doc | 0.0.4 | MIT |
| annotated-types | 0.8.0 | MIT |
| anyio | 4.14.1 | MIT |
| argostranslate | 1.11.0 | MIT License |
| astroid | 4.0.4 | LGPL-2.1-or-later |
| asttokens | 3.0.1 | Apache 2.0 |
| attrs | 26.1.0 | MIT |
| backcall | 0.2.0 | BSD License |
| beautifulsoup4 | 4.15.0 | MIT License |
| bleach | 6.4.0 | Apache Software License |
| blis | 1.3.4 | BSD |
| catalogue | 2.0.10 | MIT |
| certifi | 2026.6.17 | MPL-2.0 |
| charset-normalizer | 3.4.7 | MIT |
| click | 8.4.2 | BSD-3-Clause |
| cloudpathlib | 0.26.0 | MIT License |
| colorama | 0.4.6 | BSD License |
| colorlog | 6.12.0 | MIT License |
| confection | 1.3.4 | MIT |
| ctranslate2 | 4.8.4 | MIT |
| cymem | 2.0.16 | MIT |
| decorator | 5.3.1 | BSD-2-Clause |
| deep-translator | 1.11.4 | MIT |
| defusedxml | 0.7.1 | PSFL |
| dill | 0.4.1 | BSD-3-Clause |
| easyocr | 1.7.2 | Apache License 2.0 |
| emoji | 2.16.0 | BSD License |
| executing | 2.2.1 | MIT |
| fastjsonschema | 2.21.2 | BSD |
| filelock | 3.29.4 | MIT |
| fsspec | 2026.6.0 | BSD-3-Clause |
| h11 | 0.16.0 | MIT |
| hf-xet | 1.5.1 | Apache-2.0 |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| huggingface_hub | 1.21.0 | Apache-2.0 |
| idna | 3.18 | BSD-3-Clause |
| ImageIO | 2.37.3 | BSD-2-Clause |
| ipython | 8.12.3 | BSD-3-Clause |
| jedi | 0.20.0 | MIT |
| Jinja2 | 3.1.6 | BSD License |
| joblib | 1.5.3 | BSD-3-Clause |
| jsonschema | 4.26.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| jupyter_client | 8.9.1 | BSD 3-Clause License |
| jupyter_core | 5.9.1 | BSD-3-Clause |
| jupyterlab_pygments | 0.3.0 | BSD License |
| lazy-loader | 0.5 | BSD-3-Clause |
| Levenshtein | 0.27.3 | GPL-2.0-or-later |
| markdown-it-py | 4.2.0 | MIT License |
| MarkupSafe | 3.0.3 | BSD-3-Clause |
| matplotlib-inline | 0.2.2 | BSD-3-Clause |
| mdurl | 0.1.2 | MIT License |
| minisbd | 0.9.5 | GNU AFFERO GENERAL PUBLIC LICENSE (GNU Affero General Public License v3) |
| mistune | 3.3.2 | BSD-3-Clause |
| mpmath | 1.3.0 | BSD |
| mss | 10.2.0 | MIT License |
| murmurhash | 1.0.16 | MIT |
| narwhals | 2.24.0 | MIT |
| nbclient | 0.11.0 | BSD 3-Clause License |
| nbconvert | 7.17.1 | BSD 3-Clause License |
| nbformat | 5.10.4 | BSD 3-Clause License |
| networkx | 3.6.1 | BSD-3-Clause |
| numpy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| omegaconf | 2.4.0 | BSD License |
| onnxruntime | 1.31.1 | MIT License |
| opencv-python-headless | 4.13.0.92 | Apache 2.0 |
| packaging | 26.2 | Apache-2.0 OR BSD-2-Clause |
| pandocfilters | 1.5.1 | BSD-3-Clause |
| parso | 0.8.7 | MIT |
| pickleshare | 0.7.5 | MIT |
| pillow | 12.2.0 | MIT-CMU |
| platformdirs | 4.10.0 | MIT |
| preshed | 3.0.15 | MIT |
| prompt_toolkit | 3.0.52 | BSD License |
| protobuf | 7.36.2 | 3-Clause BSD License |
| psutil | 7.2.2 | BSD-3-Clause |
| pure_eval | 0.2.3 | MIT |
| pyclipper | 1.4.0 | MIT (OSI Approved; MIT License) |
| pydantic | 2.14.2 | MIT |
| pydantic_core | 2.50.2 | MIT |
| Pygments | 2.20.0 | BSD-2-Clause |
| PySide6 | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| PySide6_Addons | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| PySide6_Essentials | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| pyspellchecker | 0.9.0 | MIT |
| python-bidi | 0.6.10 | GNU Library or Lesser General Public License (LGPL) |
| python-dateutil | 2.9.0.post0 | BSD License; Apache Software License |
| PyYAML | 6.0.3 | MIT |
| pyzmq | 27.1.0 | BSD 3-Clause License |
| RapidFuzz | 3.14.5 | MIT |
| rapidocr | 3.10.0 | Apache-2.0 |
| referencing | 0.37.0 | MIT |
| regex | 2026.6.28 | Apache-2.0 AND CNRI-Python |
| requests | 2.34.2 | Apache-2.0 |
| rich | 15.0.0 | MIT |
| rpds-py | 2026.5.1 | MIT |
| sacremoses | 0.1.1 | MIT License |
| safetensors | 0.8.0 | Apache Software License |
| scikit-image | 0.26.0 | BSD License |
| scikit-learn | 1.9.0 | BSD-3-Clause |
| scipy | 1.18.0 | BSD License |
| sentencepiece | 0.2.2 | Apache-2.0 |
| setuptools | 81.0.0 | MIT |
| shapely | 2.1.2 | BSD 3-Clause |
| shellingham | 1.5.4 | ISC License |
| shiboken6 | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| six | 1.17.0 | MIT |
| smart_open | 9.0.1 | MIT License |
| soupsieve | 2.8.4 | MIT |
| spacy | 3.8.18 | MIT |
| srsly | 2.5.5 | MIT |
| stack-data | 0.6.3 | MIT |
| stanza | 1.10.1 | Apache License 2.0 |
| sympy | 1.13.1 | BSD |
| thinc | 8.3.14 | MIT |
| threadpoolctl | 3.6.0 | BSD-3-Clause |
| tifffile | 2026.6.1 | BSD-3-Clause |
| tinycss2 | 1.5.1 | BSD License |
| tokenizers | 0.22.2 | Apache Software License |
| toml | 0.10.2 | MIT |
| torch | 2.6.0+cpu | BSD-3-Clause |
| torchaudio | 2.6.0+cpu | BSD License |
| torchvision | 0.21.0+cpu | BSD |
| tornado | 6.5.7 | Apache-2.0 |
| tqdm | 4.68.3 | MPL-2.0 AND MIT |
| traitlets | 5.15.1 | BSD 3-Clause License |
| transformers | 5.12.1 | Apache 2.0 License |
| typer | 0.25.1 | MIT |
| typing-inspection | 0.4.4 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
| urllib3 | 2.7.0 | MIT |
| wasabi | 1.1.3 | MIT |
| wcwidth | 0.8.1 | MIT |
| weasel | 1.0.1 | MIT |
| webencodings | 0.5.1 | BSD |
| wrapt | 2.5.2 | BSD-2-Clause |
