# Bibliotecas e programas: o que ficou, o que saiu e por quê

*Levantamento de 25/11/2026. Cada item foi conferido no `requirements.txt`, nos imports do
código, no histórico do git, nos docs e nos scripts de `laboratorios/`. Os números vêm dos
docs ligados em cada seção; nada foi medido de novo para este levantamento.*

Este doc responde a uma pergunta que vai voltar: **"isso já foi testado?"**. Antes de trocar
uma peça ou de seguir uma sugestão de outra IA, vale olhar aqui se ela já passou pelo
projeto e por que ficou ou saiu.

## Resumo

| Situação | O quê |
|---|---|
| **No app** | PySide6, mss, OpenCV, numpy, RapidOCR com ONNX Runtime, EasyOCR com PyTorch, pyspellchecker, Transformers (BERT, opcional), deep-translator, Requests, Argos Translate |
| **No build** | PyInstaller, NSIS |
| **Na medição e no desenvolvimento** | Levenshtein, RapidFuzz, unittest, Pylint, Pyright, Git e GitHub CLI |
| **Testado e descartado** | Binarizar, inverter, suavizar e ampliar a imagem; Pillow na captura e no tratamento da imagem; beam search; modelos maiores do PaddleOCR; OCR do Windows; combinar motores; SymSpell; BERT sozinho; regex agressivo; as classes do deep-translator para as APIs pagas |
| **Descartado sem medir** | Tesseract, KenLM, JamSpell, LanguageTool e LLM como corretor (o teto medido não justificava) |
| **Nunca testado** | Super-resolução neural, `onnxruntime-gpu` e DirectML, modelos do RapidOCR por escrita |
| **Instalado, sem uso** | langdetect, language_tool_python, pipreqs (no `requirements.txt`); TextBlob, scikit-learn, torchaudio (só no env) |

## 1. O que o app usa hoje

### Interface, captura e imagem

| Biblioteca | Versão | Para quê | Por que ela |
|---|---|---|---|
| **PySide6** (Qt) | 6.11.1 | Janela transparente por cima do jogo, configurações, ícone na bandeja | Desde o começo do projeto. O OCR e a tradução rodam em segundo plano desde 02/11: antes, a janela congelava de 3 a 5 s a cada tradução |
| **mss** | 10.2.0 | Print da região embaixo da janela | Trocou o `ImageGrab` do Pillow em 02/11. Entrega o print direto na memória; antes, a captura era gravada em disco |
| **OpenCV** (`opencv-python-headless`) | 4.13.0.92 | Tons de cinza, recortes, a ampliação Lanczos da segunda leitura, o fundo das abas, as quantidades | A versão *headless* não traz janelas, que o app não usa. O RapidOCR e o EasyOCR também dependem dela |
| **numpy** | 2.4.6 | Contas sobre a imagem e as caixas | Base do OpenCV e dos dois motores |

O Pillow saiu do código do app. A captura começou com o `ImageGrab` dele, e nos laboratórios
de julho e agosto cada etapa do tratamento de imagem tinha uma versão em OpenCV e outra em
Pillow. Hoje ele só vem como dependência do RapidOCR, do EasyOCR e do torchvision.

### OCR

| Biblioteca | Versão | Para quê | Por que ela |
|---|---|---|---|
| **RapidOCR** com **ONNX Runtime** (CPU) | 3.10.0 e 1.31.1 | Lê inglês, chinês, japonês e 40 línguas de alfabeto latino, com os modelos PP-OCRv6 small do PaddleOCR | Trocou o EasyOCR em 16/11. Errou menos e, na CPU, foi quase três vezes mais rápido que o EasyOCR na placa de vídeo (tabela abaixo) |
| **EasyOCR** com **PyTorch** | 1.7.2, torch 2.6.0, torchvision 0.21.0 | Lê as outras 40 línguas: cirílico, árabe, coreano, devanágari, tailandês e outras | O PP-OCRv6 small não cobre essas escritas. Os modelos (cerca de 100 MB) são baixados na primeira vez que a língua é usada |

A troca de motor, medida nos 90 prints em 16/11:

| | EasyOCR (GPU MX350) | RapidOCR v6 small (CPU) |
|---|---|---|
| Erro de letras (CER) | 10,24% | **7,87%** |
| Erro de palavras (WER) | 22,30% | **12,13%** |
| Palavras de uma letra lidas | 53% | **91%** |
| Números lidos | 72% | **97%** |
| Tempo por print | 2,88 s | **1,08 s** |
| Prints melhores / piores | – | 58 / 7 |
| Instalador | – | +27 MB |

Ajustes que fazem parte da escolha:
- **o print no tamanho original** (`limit_type=max`, até 2016 px). O padrão do RapidOCR
  amplia o print até 736 px no lado menor, e aí ele lia pior (CER de 9,30%) e mais devagar;
- **corte de confiança em 0,7**, escolhido antes de olhar os prints. Com 0,8 o CER cairia um
  pouco mais, mas isso seria ajustar o corte ao próprio dataset;
- **apagar os caracteres chineses** quando o jogo é de língua latina, porque o modelo
  multilíngue lê ícones como "口".

Desde 25/11, o app também usa duas saídas do próprio RapidOCR, sem biblioteca nova:
- **as caixas de cada palavra** (`return_word_box=True`), para separar um menu lido numa
  caixa só. Custam cerca de 15 ms por print, medidos num teste pareado;
- **as probabilidades do CTC**, que o reconhecedor já calcula e o `espacos.py` guarda, para
  devolver o espaço que a leitura engoliu.

O ONNX Runtime já vinha no build antes da troca: o Argos Translate depende dele, pelo
`minisbd`. O RapidOCR trouxe junto o `omegaconf` e o `colorlog`. O `shapely` e o `pyclipper`
servem aos dois motores.

### Limpeza do texto

| Biblioteca | Versão | Para quê | Por que ela |
|---|---|---|---|
| **pyspellchecker** | 0.9.0 | Dicionário do inglês para as letras que a fonte confunde ("chc" → "the", "Dursue" → "Pursue") e para devolver o apóstrofo ("dont" → "don't") | Só troca quando a palavra lida não existe e a troca forma uma palavra comum. Nenhum dos 90 prints piorou |
| **Transformers** com o modelo **bert-base-uncased** | 5.12.1 | Correção pelo contexto, **opcional e desligada por padrão** | Só troca a palavra se o dicionário e o BERT concordarem. Com o EasyOCR, levou o CER de 10,24% para 10,17%, com 4 prints melhores e nenhum pior. Com o RapidOCR, quase nada (7,82% → 7,81%). Custa uns 5 s para carregar e 0,4 s por parágrafo com palavra desconhecida |

As duas só rodam quando o jogo está em inglês, porque o dicionário e o modelo são do inglês.
As regras de parágrafo rodam em qualquer língua e não usam biblioteca de fora.

### Tradução

| Biblioteca ou serviço | Versão | Para quê | Por que |
|---|---|---|---|
| **deep-translator** | 1.11.4 | Só o Google Tradutor grátis (`GoogleTranslator`) | Não pede conta. É o primeiro motor de reserva |
| **Requests**, direto nas APIs REST | 2.34.2 | Azure Translator, DeepL e Google Cloud Translation, com a chave do usuário | As classes do deep-translator para essas APIs faziam pedidos extras, usavam um formato antigo de autenticação do DeepL e não tratavam os erros de cota |
| **Argos Translate** | 1.11.0 | Tradução offline, a última reserva | Roda no PC, sem limite. Baixa cerca de 80 a 100 MB por par de línguas na primeira vez. É importado só quando usado, porque carrega spaCy, Stanza e CTranslate2 e deixaria a abertura lenta |

A ordem de reserva é: o motor escolhido, depois o Google grátis, depois o Argos.

As chaves das APIs ficam no `config.json` do usuário, criptografadas com o DPAPI do Windows,
chamado direto pelo `ctypes`, sem biblioteca de fora.

### Aceleração por GPU

O instalador traz o **PyTorch de CPU**, que funciona em qualquer PC e cabe no limite de 2 GB
do NSIS. Em PCs com placa NVIDIA, o app oferece baixar o **PyTorch com CUDA** (variante
`cu124`, cerca de 2,5 GB) do site oficial, com retomada e conferência do SHA-256.

Desde a troca de motor, a placa só acelera as línguas do EasyOCR. Manter ou não esse pacote
é uma decisão de produto ainda aberta.

O PyTorch continuaria no instalador mesmo sem o EasyOCR: o Argos (pelo Stanza) e o BERT
opcional também o usam.

## 2. Build e instalador

| Programa | Versão | Para quê | Detalhes |
|---|---|---|---|
| **PyInstaller** | 6.21.0 | Monta a pasta do app a partir do `main.py` | O `.spec` inclui os modelos do RapidOCR (`collect_data_files`), o import escondido `rapidocr.main` e o gancho `pyi_gancho_gpu.py`, que põe o PyTorch com CUDA na frente quando ele foi baixado. O `nltk` é excluído do pacote; o motivo não ficou registrado |
| **NSIS** | – | Gera o `RealTimeScreenTranslator_Setup.exe` | Detecta a versão instalada e atualiza no lugar, mantendo as chaves. O limite de 2 GB é o motivo de o PyTorch com CUDA ficar fora |
| **env_build** | – | Ambiente separado só para o build | Tem o PyTorch de CPU do PyPI, para as bibliotecas CUDA não entrarem no instalador |

O instalador tinha 383 MB em 15/11 e foi para 413,5 MB com o RapidOCR, em 16/11.

## 3. Medição e desenvolvimento

| Biblioteca ou programa | Versão | Para quê |
|---|---|---|
| **Levenshtein** | 0.27.3 | A distância de edição do CER e do WER no benchmark |
| **RapidFuzz** | 3.14.5 | Achar, no gabarito, o trecho com que cada linha lida mais se parece, para medir o erro de letras sem contar a ordem entre painéis |
| **unittest** (do Python) | – | 140 testes com caixas de OCR simuladas, em várias línguas, sem prints |
| **Pylint** com o plugin **pylint-qt** | 4.0.6 | Conferir cada script criado ou editado (regra de 23/11) |
| **Pyright**, o motor do Pylance | 1.1.414 | O mesmo, com checagem de tipos. Instalado pelo npm em `ferramentas/`. Entrou depois que o Pylance do VS Code achou um defeito real que o Pylint e os testes não pegavam ([verificação de código](verificacao-de-codigo.md)) |
| **Git**, **GitHub** e a **GitHub CLI** (`gh`) | – | Histórico, PRs e merge |
| **Python 3.12** em ambiente virtual (`env`) | – | Desenvolvimento |

## 4. Testado e descartado

### Tratar a imagem

Entre 13/07 e 09/08, 18 scripts de laboratório rodaram quase 10 mil combinações de
tratamento de imagem no EasyOCR: ampliar, tirar ruído, separar um canal de cor, binarizar e
limpar, cada etapa em OpenCV ou em Pillow e em todas as ordens. A binarização de Otsu ganhou
dos limiares adaptativos (97,9% contra 58,3% e 52,0% de acerto). Mas tudo foi medido numa
imagem só, e no primeiro print real o resultado não se repetiu (*overfitting*, seção 5 do
[estudo de caso](estudo-de-caso-ocr.md)).

Medido depois em prints reais, nenhum tratamento ganhou da imagem só em tons de cinza:

| Tratamento | Resultado | Onde |
|---|---|---|
| Pipeline binarizado e ampliado dos laboratórios | CER de 1,41% contra 0,78% e 7,0 s contra 2,9 s, em 3 prints | Benchmark de 02/11 |
| Inverter as cores quando o fundo é escuro | 12,42% contra 12,27%; 21 prints melhores e 28 piores | 90 prints, EasyOCR |
| Inverter só com muito fundo preto | 12,49%; 16 melhores e 24 piores | idem |
| Desfoque leve, para fonte em pixel | 17,25%; 13 melhores e 52 piores | idem |
| Ampliar 2x e desfocar | 13,32%, a 10,1 s por print | idem |
| Reduzir e ampliar de volta | 22,99% | idem |
| Ampliar até 736 px (o padrão do RapidOCR) | 9,30% contra 7,87% | 90 prints, RapidOCR |

CLAHE e nitidez também aparecem como piores nos docs, sem número registrado. A única
ampliação que entrou é local: a segunda leitura amplia com Lanczos só as caixas pequenas,
uma a uma.

### Configurar o EasyOCR

| O quê | Por que saiu |
|---|---|
| Decoder *beam search* | O *greedy* é mais rápido (6,74 s contra 8,91 a 13,12 s na imagem dos laboratórios, todos com o mesmo acerto) e não engole letras duplas |
| Baixar o tamanho mínimo e os limiares da detecção | Não fez o detector achar números e palavras de uma letra em fonte pequena |
| EasyOCR como motor principal | Saiu em 16/11 para o RapidOCR (tabela da seção 1). Na CPU, ficou em 10,30% de CER, a 3,87 s por print |

### Outros motores de OCR (16/11)

Medidos nos 90 prints, com as mesmas regras do app ([comparação de motores](comparacao-motores-ocr.md)):

| Motor | CER | Tempo | Por que não |
|---|---|---|---|
| RapidOCR PP-OCRv6 medium | 8,45% | 10,1 s | Mais lento e pior que o small, e +103 MB no instalador |
| RapidOCR PP-OCRv5 server | 12,53% | 23,7 s | Pior e muito mais lento, +151 MB |
| RapidOCR PP-OCRv5 mobile, só inglês | 8,77% | 0,86 s | A alternativa mais leve (+13 MB), mas atrás do v6 small no CER, nos números e em prints piorados (15 contra 7) |
| RapidOCR PP-OCRv4 mobile, só inglês | 9,16% | 1,56 s | Pior que os dois acima |
| OCR do Windows (`winrt`), pacote pt-BR | 15,79% | 0,05 s | Muito rápido, mas só lê 82% das palavras, não dá confiança por caixa e depende do pacote de língua de cada PC. Só o pt-BR foi testado |

Combinar o EasyOCR e o RapidOCR também não compensou:
- **juntar as caixas** dos dois: 10,30%, pior que o EasyOCR sozinho;
- **escolher pela confiança**: escolhe sempre o RapidOCR, com o dobro do tempo;
- **usar o RapidOCR só na letra pequena**: 9,61%;
- **o teto**, escolhendo o melhor motor de cada print com o gabarito na mão: 7,35%, só meio
  ponto abaixo do RapidOCR sozinho.

### Corrigir as palavras

| O quê | Resultado | Por que saiu |
|---|---|---|
| Corretor ortográfico e BERT sem exigir acordo (a versão dos laboratórios) | 7 prints melhores e 7 piores | Trocava termos de jogo por palavras comuns: "swarmer" virava "warmer", "melee" virava "pelee" |
| Regex agressivo de pontuação | 56 prints piores | Punha ponto no meio de títulos ("Fire. Technique.") |
| SymSpell (`symspellpy`), para separar palavras grudadas | Quebrou nomes de jogo ("Dragonbind", "Garrus") | E um dicionário por língua não serve a um app que lê 83 línguas. O espaço engolido foi resolvido em 25/11 pela probabilidade do CTC, sem dicionário |

**Descartados sem medir: Tesseract, KenLM, JamSpell, LanguageTool e LLM como corretor.**
Eles aparecem nas listas do que não será mais tentado, mas não há script nem número deles
nos laboratórios. A decisão veio de medidas anteriores:
- antes de atacar a correção, contei quanto dava para ganhar. Com o EasyOCR, só 3,6% das
  palavras estavam lidas erradas mas parecidas, que é o que um corretor conserta. Com o
  RapidOCR, o teto caiu para cerca de 1% das palavras;
- o Tesseract entrou na lista dos motores descartados porque o RapidOCR v6 small ganhou de
  todos os que foram medidos. Ele mesmo não foi medido.

Se algum deles voltar à mesa, a medida ainda está por fazer.

### Medir a tradução

Nos laboratórios, a tradução do Google foi comparada com uma referência pelo
**sentence-transformers**, com o modelo `paraphrase-multilingual-MiniLM-L12-v2`, que mede se
duas frases dizem a mesma coisa. Deu 97,8% de similaridade, contra 93% letra por letra. A
conclusão foi que o tradutor não era o gargalo. Medir a qualidade da tradução está fora do
projeto até o dono pedir.

## 5. Sugerido e nunca testado

| O quê | De onde veio | Por que não foi testado |
|---|---|---|
| Super-resolução neural (FSRCNN, ESPCN, Real-ESRGAN; o OpenCV tem `dnn_superres`) | Problemas em aberto e o Grok, no problema dos letreiros | A segunda leitura com Lanczos resolveu. O Grok sugeriu o FSRCNN só se o Lanczos não bastasse |
| `onnxruntime-gpu` e DirectML | Comparação de motores | O RapidOCR na CPU já é mais rápido que o EasyOCR na placa |
| Modelos PP-OCRv5 por escrita (cirílico, árabe, coreano...), cerca de 8 MB cada | Comparação de motores | Ainda não há prints com gabarito nessas línguas |
| TrOCR, SwinIR, waifu2x, Ollama com Phi ou Qwen | Listas de sugestões de outras IAs, em 16/11 | Nenhum foi medido. A troca para o RapidOCR, no mesmo dia, e o teto da correção tiraram a urgência |

## 6. Instalado, mas sem uso

Não fazem parte do app, mas continuam no PC de desenvolvimento. Ficam listados para uma
limpeza futura, com o instalador refeito e testado depois.

| O quê | Onde está | Situação |
|---|---|---|
| `langdetect` 1.0.9 e `language_tool_python` 3.4.0 | `requirements.txt` | Nenhum código importa |
| `pipreqs` 0.5.0, que traz o IPython, o nbconvert e a família do Jupyter | `requirements.txt` | Ferramenta que gera o `requirements.txt` a partir dos imports |
| TextBlob, que traz o NLTK | Só no `env` | Nenhum código importa. O NLTK é excluído do instalador no `.spec` |
| scikit-learn, sentence-transformers, symspellpy, torchaudio | Só no `env` | Usados em laboratório ou sem uso |
| Modelo `vennify/t5-base-grammar-correction` | Cache do Hugging Face | Um corretor de gramática baixado em algum teste. Não há script nem resultado registrado |
| `craft_mlt_25k.pth` e `latin_g2.pth` | Pasta `modelos/`, fora do git | Modelos do EasyOCR dos laboratórios de julho. O app não usa essa pasta |
| `winrt` | Ambiente separado em `laboratorios/ocr_alternativos/` | Usado só para medir o OCR do Windows |

## 7. Programas do processo

- **Outras IAs, para os problemas difíceis.** Do problema 3 em diante: ChatGPT, Grok,
  DeepSeek, Mistral e Qwen. Nos dois primeiros, também o Copilot e o Gemini, que saíram
  porque respondiam rápido mas repetiam ideias que a pergunta dizia já ter testado. Toda
  proposta é medida nos prints, nas duas leituras, antes de entrar. Placar e lições em
  [consulta a outras IAs](consulta-outras-ias.md).
- **Claude Code**, como assistente de programação: implementa, mede e documenta. Os commits
  feitos com ele levam a linha `Co-Authored-By`.
- **VS Code com o Pylance**, onde o defeito da troca de língua apareceu.

## 8. Linha do tempo

| Data | O que entrou ou saiu |
|---|---|
| 28/06 | Estrutura inicial: PySide6, captura com o `ImageGrab` do Pillow, OpenCV, EasyOCR, o Google Tradutor pelo deep-translator e o instalador com PyInstaller e NSIS |
| 13/07 a 09/08 | Laboratórios: tratamento de imagem em OpenCV e Pillow, parâmetros do EasyOCR, pyspellchecker com BERT, MiniLM para medir a tradução |
| 02/11 | Benchmark com o código do app. Sai o tratamento de imagem e o *beam search*; o BERT fica opcional; a captura passa ao mss. Entram as APIs da Azure, do DeepL e do Google Cloud pela REST e o Argos offline. O build passa a um ambiente com PyTorch de CPU, e entra o pacote de GPU |
| 16/11 | Entra o RapidOCR com o ONNX Runtime. O EasyOCR fica só nas línguas que o RapidOCR não lê |
| 17 a 25/11 | Regras de leitura e de parágrafo com propostas de outras IAs, sem biblioteca nova |
| 23/11 | Entram o Pylint e o Pyright em todo script editado |
| 25/11 | O app passa a usar as caixas de palavra e as probabilidades do CTC do RapidOCR |

## Onde estão os detalhes

- [Estudo de caso](estudo-de-caso-ocr.md): a história inteira, com os erros do caminho.
- [Comparação de motores de OCR](comparacao-motores-ocr.md): todos os modelos medidos, com
  licenças e tamanhos.
- [Resultados com o RapidOCR](resultados-benchmark.md) e [com o EasyOCR](resultados-benchmark-easyocr.md).
- [Problemas em aberto](problemas-em-aberto.md), com a tabela do que já foi testado e não
  funcionou nas regras de leitura e de parágrafo.
- [Verificação de código](verificacao-de-codigo.md): a regra do Pylint e do Pyright.
- [Consulta a outras IAs](consulta-outras-ias.md).
