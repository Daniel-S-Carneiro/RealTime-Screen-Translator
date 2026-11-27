# Estudo dos concorrentes

*26/11/2026. O que os tradutores de tela para jogos oferecem hoje, o que o app já tem e o
que entra na primeira build. São duas pesquisas juntas: a minha e uma do ChatGPT, feita a
pedido do dono do projeto e conferida aqui produto a produto. Os dados vêm das páginas de
cada produto (Steam, GitHub, itch.io e listagens). Nenhum foi instalado nem testado: são
as promessas de cada desenvolvedor, não medidas.*

## Os concorrentes

**Gratuitos, de código aberto:**

| Produto | Licença | O que chama a atenção |
|---|---|---|
| DeskTranslate 2.0 | MIT | Refeito em 17/10/2026. Modo ao vivo que pula o OCR quando a imagem não muda, perfis por jogo, contexto para o LLM, chaves no cofre do Windows, edição da aparência na tela |
| Games_translator | GPL-3.0 | Uma área fixa para as falas (Live) e outra escolhida na hora (Dynamic); memória de tradução; cobre a legenda original com a cor da placa; chaves pela DPAPI, como nós |
| SubLens | MIT | Feito para falas e legendas: espera o texto meio apagado ficar legível, junta as linhas, carrega o perfil pelo executável do jogo |
| Lingolay | GPL-3.0 | Tudo offline (NLLB-200), com dublagem por voz neural; pula o OCR quando a imagem não muda e espera o efeito de máquina de escrever |
| Screen Translator (MilkteaTW1) | MIT | Windows, macOS e Android; protege nomes próprios; só mostra o bloco que apareceu duas vezes; chaves em texto puro |
| RSTGameTranslation | Grátis | Até 5 áreas, modo automático, LLMs, perfis por jogo, voz |
| Translumo | Apache-2.0 | Roda vários OCRs juntos e um modelo escolhe o melhor resultado |
| LunaTranslator | GPL-3.0 | Lê o texto de dentro do jogo (hook) e usa OCR quando não dá; foco em romances visuais |
| Shin Translator | GPL-3.0 | Hook (Textractor ou LunaHook) e OCR, com histórico das capturas por jogo |
| Interpreter | MIT | Jogos japoneses antigos; tradução embutida só do japonês para o inglês; cache por texto parecido |
| MORT | Código aberto | Tradutor coreano antigo: lê as falas por OCR e traduz por máquina ou por um banco de traduções |
| Universal Game Translator (UGT) | BSD | O pioneiro (2019), com o Google Cloud Vision, atalho e controle |
| Screen-Translate | MIT | Tesseract e vários tradutores, em Python e Tkinter |

**Pagos ou com versão paga:**

| Produto | Preço (26/11) | O que chama a atenção |
|---|---|---|
| Realtime Screen OCR Translator | R$ 3,49, na Steam | O mais barato; traduz de novo quando o texto muda |
| Game Overlay Translator | R$ 17,99, pagamento único, na Steam | Tela inteira ou até 4 áreas, controle, glossário, memória de tradução, perfis por jogo, voz; usa o RapidOCR, como nós |
| Real-Time Screen Translator (ESTI Software) | R$ 19,49, acesso antecipado, na Steam | Lançado em 22/11/2026, com quase o mesmo nome do nosso; modelos de tradução locais, sem chave |
| ComfyTrans | R$ 22,00, na Steam | PaddleOCR ou Windows OCR, LLM local ou na nuvem, histórico, predefinições por jogo |
| LingoHUD | R$ 37,49, acesso antecipado, na Steam | Modos de leitura (jogo, chat, legenda, mangá), modelos offline, leitura em voz |
| Playto | R$ 37,49, acesso antecipado, na Steam | Segue o cursor, congela a cena, glossário por jogo e caderno de palavras |
| Screen Translator (JinSoft) | Ainda não à venda; acesso antecipado previsto para novembro, na Steam | Tradução local (Hy-MT2), dicionários compartilhados pela Oficina da Steam |
| Translate Lens | Grátis com 20 traduções, depois créditos ou chave própria, na Steam | Atalho, controle, modo automático, Gemini, OpenAI, DeepL e Ollama |
| GameTranslate | US$ 5 ou mais, no itch.io | Entra no jogo (DirectX e OpenGL) e traduz no modo automático, offline |
| Game-Changing Translator | Grátis, com versão PRO | O OCR é feito por IA de visão (Gemini e outros) |
| Lookupper | Grátis limitado ou US$ 10 por mês | IA, dicionário e exportação para o Anki |
| Unitra AI | Não conferido | Junta voz, chat e tela; o texto lido vai para o servidor deles. Só uma listagem de terceiros confirmou os dados |

Ficaram de fora as ferramentas de outro tipo: o Immersive Translate traduz uma imagem
enviada, não a tela ao vivo, e o Sugoi Translator e o Textractor leem o texto de dentro
dos romances visuais.

## Quem tem cada função

| Função | Quem tem | Nós |
|---|---|---|
| **Atalho global** (traduzir, mostrar, esconder) | Quase todos: DeskTranslate, Games_translator, SubLens, Lingolay, Screen Translator (MilkteaTW1 e JinSoft), RSTGameTranslation, Translumo, Game Overlay Translator, ComfyTrans, LingoHUD, Playto, Translate Lens | Não: só o botão "Traduzir Área" |
| **Modo automático** (traduz de novo quando o texto muda) | DeskTranslate, Games_translator, SubLens, Lingolay, Screen Translator (MilkteaTW1 e JinSoft), Interpreter, RSTGameTranslation, LunaTranslator, ComfyTrans, LingoHUD, Playto, Translate Lens, Realtime Screen OCR Translator | Não |
| **Pula o OCR quando a imagem não muda** | DeskTranslate, Lingolay | Não |
| **Espera o texto ficar estável** (máquina de escrever, texto meio apagado) | SubLens, Lingolay; o MilkteaTW1 só mostra o bloco visto duas vezes | Não |
| **Tira a própria janela da captura** (não lê a própria tradução) | SubLens, Lingolay, Screen Translator (MilkteaTW1 e JinSoft); o DeskTranslate deixa a janela fora da área | Não: a janela some por 300 ms a cada captura |
| **Resposta atrasada não apaga a nova** | DeskTranslate | Não se aplica sem o modo automático |
| **Cache ou memória de tradução** | Games_translator, Game Overlay Translator (corrigível pelo usuário), Lingolay, Screen Translator (MilkteaTW1 e JinSoft), Interpreter (por texto parecido), Translate Lens, GameTranslate, Game-Changing | Não |
| **Tradução sobre o texto original**, na mesma posição | Games_translator (cobre a placa da legenda), Screen Translator (MilkteaTW1), Interpreter, LunaTranslator, Game Overlay Translator, ESTI, ComfyTrans, LingoHUD, RSTGameTranslation, Translate Lens, Lingolay (experimental) | Em parte: o texto traduzido aparece dentro da janela, por cima da área inteira |
| **Clique atravessa a janela** (click-through) | DeskTranslate, SubLens, Lingolay, Screen Translator (MilkteaTW1 e JinSoft), Interpreter | Não |
| **Aparência** (letra, cor, fundo, opacidade) | DeskTranslate, Games_translator, SubLens, Lingolay, JinSoft, Game Overlay Translator, ComfyTrans, ESTI, Playto, Translate Lens | Não: letra fixa de 16 px |
| **LLM na nuvem** com chave própria | DeskTranslate (OpenAI, Anthropic, Gemini, OpenRouter), Games_translator, SubLens, Screen Translator (MilkteaTW1), RSTGameTranslation, ComfyTrans, Translate Lens, LunaTranslator | Não: Google, Azure, DeepL e Google Cloud |
| **LLM local** (Ollama, LM Studio) | DeskTranslate, SubLens, Screen Translator (MilkteaTW1), Interpreter, RSTGameTranslation, Game Overlay Translator, ComfyTrans, LingoHUD, Translate Lens; a JinSoft roda modelos GGUF | Não |
| **Contexto para o LLM** (linhas anteriores, glossário, notas do jogo) | DeskTranslate, SubLens, Interpreter, RSTGameTranslation, Game-Changing | Não |
| **Tradução offline** | Games_translator, Lingolay (NLLB-200), Screen Translator (MilkteaTW1: Argos e TranslateGemma), JinSoft, ESTI, LingoHUD, Playto, Game Overlay Translator, GameTranslate | Sim, com o Argos, de qualidade mais baixa |
| **Glossário** | DeskTranslate, SubLens, Screen Translator (MilkteaTW1: nomes que não se traduzem), JinSoft, Game Overlay Translator, Playto | Não |
| **Perfis por jogo** | DeskTranslate, Games_translator, SubLens (carrega pelo executável do jogo), Lingolay, Shin Translator, RSTGameTranslation, Game Overlay Translator, ComfyTrans | Não |
| **Histórico** | Shin Translator (com a imagem da captura), RSTGameTranslation, Game Overlay Translator, ComfyTrans, Playto | Não |
| **Várias áreas** | Games_translator (fixa e na hora), RSTGameTranslation (5), Game Overlay Translator (4), ComfyTrans, Playto, LunaTranslator | Não |
| **Tela inteira ou janela do jogo** | DeskTranslate, Screen Translator (MilkteaTW1 e JinSoft), Interpreter, Game Overlay Translator, LingoHUD, ComfyTrans, Playto | Não: o menu diz "Em breve" |
| **Chaves protegidas** | DeskTranslate (cofre do Windows), Games_translator (DPAPI); o MilkteaTW1 e o Interpreter guardam em texto puro | Sim, pela DPAPI |
| **Controle** (gamepad) | Translate Lens, Game Overlay Translator, UGT | Não |
| **Leitura em voz** | Lingolay (dublagem), RSTGameTranslation, Game Overlay Translator, LingoHUD, Playto, LunaTranslator, Lookupper | Não |
| **Legenda da voz do jogo** | Screen Translator (MilkteaTW1), RSTGameTranslation, Game Overlay Translator, ComfyTrans, LunaTranslator, Unitra AI | Não |
| **Estudo de língua** (dicionário, Anki) | LunaTranslator, Shin Translator, Playto, Lookupper | Não |

**Limitações que quase todos admitem:**
- **Tela cheia exclusiva:** a tradução some ou a captura falha. Quase todos pedem o modo
  janela ou janela sem borda.
- **Antitrapaça:** jogos online podem avisar, expulsar ou banir.
- **Executável sem assinatura:** DeskTranslate, SubLens, Lingolay e MilkteaTW1 avisam que o
  Windows (SmartScreen) pode reclamar.

## O que só nós temos

- **Qualidade medida e publicada.** Nenhum concorrente mostra quantas letras e linhas
  acerta. Nós medimos o OCR e a montagem em 150 prints de 17 jogos, com a régua (o
  benchmark) no repositório.
- **A montagem do texto.** Títulos, parágrafos, opções de menu e linhas de efeito saem
  separados; a frase que só quebrou para caber vai inteira ao tradutor; fichas, inventários
  e painéis são lidos coluna por coluna. Alguns concorrentes descrevem juntar as linhas de
  uma legenda, mas nenhum descreve a montagem de fichas e menus.
- **A trava de cota.** O app mostra o uso do mês e para antes de passar do grátis. Nenhum
  outro descreve isso; o Game-Changing só mostra o custo.
- **Português do Brasil.** A interface é em português, e a maioria dos concorrentes é em
  inglês, chinês ou russo.

A cifra das chaves não é só nossa: o DeskTranslate e o Games_translator também protegem as
chaves.

**As 83 línguas não são, ainda, um diferencial.** O app lê 83 línguas, mas o benchmark só
mediu o inglês e 10 prints em espanhol. O Windows OCR, que muitos concorrentes usam, também
lê dezenas de línguas. Antes de vender isso, é preciso medir outras escritas.

## O nome

Há pelo menos quatro produtos com nome parecido com o nosso (RealTime Screen Translator):
- o Real-Time Screen Translator da ESTI Software, na Steam desde 22/11/2026, com a mesma
  proposta;
- o Realtime Screen OCR Translator, também na Steam;
- o Screen Translator da JinSoft, que vai entrar na Steam;
- o Screen Translator do MilkteaTW1, no GitHub.

Numa busca na loja, todos se confundem. **Antes de publicar uma build, vale escolher um
nome próprio.** A decisão é do dono do projeto.

## A pesquisa do ChatGPT

O ChatGPT trouxe 11 concorrentes que a minha pesquisa não tinha. Conferi cada um na
página do projeto:
- **Existem e batem com o que ele disse:** DeskTranslate 2.0, Games_translator, SubLens,
  Lingolay, Screen Translator (MilkteaTW1), Screen Translator (JinSoft), Shin Translator e
  Interpreter. As diferenças são pequenas: o Lingolay diz 21 línguas, não 22.
- **Não conferidos:** a lista de motores do MORT não bate com a que aparece nas buscas
  (Tesseract, Windows OCR, NHOcr e EasyOCR; Papago, Google, Google Sheets, ezTrans e DeepL),
  e o MeikiOCR do Interpreter não aparece na página dele. O Unitra AI só aparece numa
  listagem de terceiros.
- **Não encontrado:** o ScreenGloss. Nenhuma busca achou esse nome; ficou de fora.

**O que ele errou sobre o nosso app:**
- **"7,87% de CER e 1,08 s por print".** Esse é um número antigo, de antes da leitura por
  colunas. Hoje o erro de letras nos 90 prints é de 4,1% (95,9% de acerto e 97,4% sem
  ordem), e 549 de 671 linhas saem inteiras.
- **As funções marcadas "a confirmar".** Foram conferidas no código: o app ainda não tem
  modo automático, atalhos, glossário, contexto, cache, perfis nem várias áreas.

**O que ele acrescentou de útil:**
- **Os detalhes do modo automático:** pular o OCR na imagem parada, esperar o texto ficar
  estável, tirar a própria janela da captura e não deixar uma resposta atrasada apagar a
  nova.
- **O contexto para o LLM** (linhas anteriores, glossário e notas do jogo) e os perfis
  carregados pelo executável do jogo.
- **Um roteiro de teste prático:** instalar seis concorrentes (DeskTranslate, Games_translator,
  SubLens, Game Overlay Translator, LunaTranslator e Lingolay) e passar os mesmos casos em
  todos: fala simples, fala em duas linhas, texto que surge aos poucos, inventário, ficha,
  menu e tela cheia. Fica como opção para o dono do projeto. Baixar e rodar programas de
  terceiros é decisão dele.
- **O posicionamento:** os concorrentes investem em facilidade de uso, não só em precisão.
  O jogador quer abrir, escolher o jogo e jogar.

## O que entra na primeira build

As duas pesquisas chegam à mesma conclusão: o básico que todos têm falta no nosso app, e a
montagem do texto é o que só nós temos. Nada aqui mexe nos módulos de leitura e montagem
(`paragrafos.py`, `espacos.py`, `quantidades.py`, `releitura.py`, `ocr_engine.py`,
`pipeline_ocr.py` e `processador_texto.py`), que ficam congelados até a rodada 2 ser medida.

**Bloco 1, usar sem sair do jogo:**
1. **Atalhos globais**, configuráveis: traduzir, ligar e desligar o modo automático,
   mostrar ou esconder, limpar.
2. **A janela fora da captura.** É o que deixa o modo automático ler a tela sem ler a
   própria tradução, e acaba com o piscar da janela a cada captura.
3. **Modo automático:** compara a área com a captura anterior e só roda o OCR quando a
   imagem muda; espera o texto ficar estável; não traduz de novo a mesma linha; uma
   resposta atrasada não apaga a nova.
4. **Cache das traduções**, em disco, que também poupa a cota das chaves.
5. **Aparência:** tamanho da letra, cores, opacidade do fundo e o clique atravessando a
   janela.
6. **Histórico** das últimas traduções, com cópia.
7. **O Google grátis mais robusto.** Em 26/11, o diagnóstico na rede do dono do projeto deu
   429 e a página de captcha do Google (`google.com/sorry`): o IP da rede está bloqueado, e
   nenhuma biblioteca muda isso. O motor ganha tempo limite, reconhece o bloqueio mesmo
   quando ele vem como resposta normal, espera o tempo que o Google indicar e diz ao
   usuário o que fazer. O app não contorna o captcha nem se passa por navegador.
8. **Primeira execução guiada** para um motor que não bloqueia: a chave grátis da Azure (2
   milhões de caracteres por mês) ou o modo offline.

**Bloco 2, a qualidade da tradução:**
1. **LLMs com chave própria**, por uma API no padrão da OpenAI. Uma integração só cobre
   OpenAI, Gemini, DeepSeek, Groq, OpenRouter e Anthropic, e também o **Ollama** e o **LM
   Studio**, que rodam no PC. O motor entra na mesma fila de queda e no mesmo controle de
   uso dos outros.
2. **Contexto para o LLM:** as últimas linhas, o glossário e uma nota sobre o jogo.
3. **Glossário:** nomes que não se traduzem e termos com tradução fixa.
4. **Perfis por jogo:** área, línguas, motor, glossário e aparência, carregados quando o
   jogo abre.

**Bloco 3, o alcance:**
1. **Interface em inglês**, além do português.
2. **Aviso sobre o modo de tela e a antitrapaça**, na primeira execução e no README.
3. **O nome novo**, se o dono do projeto decidir trocar.

**Para depois da primeira build:** várias áreas; a tradução sobre cada linha, na posição
do original; a tela inteira; o controle; a leitura em voz; um modelo offline melhor que o
Argos. O candidato medido é o Hy-MT2 1.8B ([Os tradutores, lado a
lado](comparacao-tradutores.md)). **Fora, por ora:** a legenda da voz do jogo, a dublagem, o
OCR por IA de visão, o hook, o estudo de língua e o Steam Deck.

Cada build é medida no benchmark antes de sair, como ficou combinado: a que piorar as
letras ou as linhas inteiras não sai.

## Fontes

Páginas lidas em 26/11/2026:
- Código aberto: [DeskTranslate](https://github.com/DeskTranslate/DeskTranslate),
  [Games_translator](https://github.com/ZGeorg-tech/Games_translator),
  [SubLens](https://github.com/bnsware/SubLens),
  [Lingolay](https://github.com/keremss7/lingolay),
  [Screen Translator (MilkteaTW1)](https://github.com/MilkteaTW1/Screen-Translator),
  [RSTGameTranslation](https://github.com/thanhkeke97/RSTGameTranslation) e o
  [site](https://thanhkeke97.github.io/RSTGameTranslation),
  [Translumo](https://github.com/Danily07/Translumo),
  [LunaTranslator](https://github.com/HIllya51/LunaTranslator),
  [Shin Translator](https://github.com/leo2august/Shin-Translator),
  [Interpreter](https://github.com/bquenin/interpreter),
  [MORT](https://github.com/killkimno/MORT),
  [UGT](https://github.com/SethRobinson/UGT),
  [Screen-Translate](https://github.com/Dadangdut33/Screen-Translate).
- Steam: [Translate Lens](https://store.steampowered.com/app/3652400),
  [Realtime Screen OCR Translator](https://store.steampowered.com/app/3923160),
  [Real-Time Screen Translator (ESTI)](https://store.steampowered.com/app/5367460),
  [Game Overlay Translator](https://store.steampowered.com/app/4864520),
  [LingoHUD](https://store.steampowered.com/app/4289950),
  [ComfyTrans](https://store.steampowered.com/app/5259250/),
  [Playto](https://store.steampowered.com/app/4603950/Playto/),
  [Screen Translator (JinSoft)](https://store.steampowered.com/app/5454530).
- Outros: [GameTranslate](https://godnoken.itch.io/gametranslate),
  [Game-Changing Translator](https://tomkam1702.github.io/OCR-Translator/),
  [Lookupper](https://alternativeto.net/software/lookupper--screen-translator/about)
  (listagem do AlternativeTo),
  [Unitra AI](https://startup-seeker.com/company/unitra~ai) (listagem de terceiros),
  [Immersive Translate](https://immersivetranslate.com/en/image/game-screenshot-translator/).
