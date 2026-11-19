# Benchmark de OCR

Mede o pipeline **de produção** (`pipeline_ocr.reconhecer_texto`, o mesmo que o
app usa) em todas as imagens de `dataset/`. Substitui os laboratórios antigos,
que copiavam o pipeline e usavam uma imagem só.

## Como coletar prints

1. Rode o app pelo código (`env\Scripts\python.exe main.py`). O modo de
   depuração liga sozinho quando o app não é o instalado.
2. No ícone da bandeja, marque **Salvar prints para o benchmark**.
3. Use o "Traduzir Área" normalmente. Cada captura vai para a pasta do dia,
   `dataset/AAAA-MM-DD/`:
   - `coleta_AAAAMMDD_HHMMSS.png`: o print bruto;
   - `coleta_AAAAMMDD_HHMMSS.rascunho.txt`: o que o OCR leu, um parágrafo por linha.
4. Abra o print, **corrija o rascunho olhando a imagem** e salve como
   `coleta_AAAAMMDD_HHMMSS.txt` (sem o `.rascunho`). Pode renomear o par para
   algo descritivo, como `rpg_menu_fundo_claro.png` + `rpg_menu_fundo_claro.txt`.

Imagens sem `.txt` aparecem como `[PENDENTE]` e ficam fora da conta.

**Na validação com jogos novos é diferente** (veja o
[plano de validação](../docs/plano-de-validacao.md)): os prints são **movidos** (não
copiados) da pasta do dia para `dataset/validacao/`, e o gabarito é escrito olhando só a
imagem, **sem abrir o rascunho**. Corrigir o rascunho seria olhar o resultado do app antes
da prova. O rascunho fica na pasta do dia.

### Como a pasta é organizada

```
dataset/
├── base/          os 3 exemplos que vêm com o repositório
├── 2026-11-02/    uma pasta por dia de coleta
├── 2026-11-14/
├── validacao/     os prints de jogos novos, medidos à parte (--periodo validacao)
└── _fora/         prints guardados que não entram no teste
```

Os prints coletados ficam só no seu PC: tudo em `dataset/` está no `.gitignore`,
menos a pasta `base/`. Você também pode criar pastas com outros nomes (por
exemplo, `undertale/`); o `--periodo` filtra pelo nome da pasta. Pastas que
começam com `_` ficam fora do teste: servem para guardar um print que ajudou a
olhar as quebras de linha, mas que não vai ter gabarito.

### O que vale coletar (15 a 30 prints)

- fundo claro e fundo escuro;
- texto colorido (laranja, roxo, vermelho) e texto sobre imagem/textura;
- fontes estilizadas, pixel art e letras pequenas;
- números e porcentagens (dano, HP, preço), que não podem errar;
- menus curtos ("New Game", "Settings") e diálogos longos;
- nomes próprios de personagens e lugares;
- texto centralizado, fonte manuscrita e efeitos de glitch.

Não vale ter gabarito para letra de música ou texto completo de terceiros (um
poema ou uma carta inteira): o `.txt` seria uma cópia da obra. Se o print foi útil
para ver as quebras, guarde em `_fora/`.

### Como escrever o gabarito

- Copie o texto **exatamente como aparece** na imagem, com a mesma pontuação.
- **Uma linha por parágrafo ou item**: título, parágrafo, opção de menu, efeito.
  Quando a frase só continua na linha de baixo porque não coube na caixa, junte
  numa linha só.
- O CER e o WER ignoram as quebras de linha, os espaços repetidos e as maiúsculas;
  as quebras são medidas à parte.
- A ordem é a de leitura: de cima para baixo, da esquerda para a direita.

## Como rodar

Na pasta do projeto:

```
env\Scripts\python.exe benchmark\benchmark.py
env\Scripts\python.exe benchmark\benchmark.py --detalhes
env\Scripts\python.exe benchmark\benchmark.py --periodo 2026-11-14
env\Scripts\python.exe benchmark\benchmark.py --periodo base,2026-11-01..2026-11-10
env\Scripts\python.exe benchmark\benchmark.py --configs producao,imagem_binarizado --repeticoes 3
```

| Opção | O que faz |
|---|---|
| `--configs` | Quais configurações rodar (padrão: todas) |
| `--periodo` | Quais pastas de `dataset/` testar, separadas por vírgula (padrão: todas). Aceita o nome da pasta (`base`, `2026-11-14`), o começo dele (`2026-11` pega o mês todo) ou um intervalo com as duas pontas incluídas (`2026-11-01..2026-11-10`) |
| `--repeticoes N` | Roda N vezes e usa a mediana do tempo |
| `--detalhes` | Mostra as palavras erradas: `[-esperado-]{+lido+}` |
| `--idioma` | Idioma do texto, para o pós-processamento (padrão `en`) |

O relatório vai para `relatorios/benchmark/benchmark_<data>.csv`.

## Configurações comparadas

| Nome | O que muda em relação à produção |
|---|---|
| `producao` | Nada: padrões atuais do app |
| `imagem_original` | Manda a imagem colorida sem tratamento |
| `imagem_cinza` / `imagem_binarizado` | Outro modo de imagem (aparece o que não for o padrão) |
| `contexto_bert` | Liga a correção por contexto: troca a palavra só quando o dicionário e o BERT concordam |
| `pontuacao_agressiva` | Liga as regras de regex ajustadas no `teste.png` |
| `pontuacao_agressiva+bert` | Regex agressivo + correção por contexto |

## Como ler o resultado

- **CER** (taxa de erro de caracteres): quantas letras precisariam ser
  corrigidas, dividido pelo tamanho do gabarito. 2% = 2 letras erradas a cada 100.
  Quanto menor, melhor.
- **sem ordem** (coluna `cer_sem_ordem` no CSV): o CER depois de pôr as linhas lidas
  na ordem do gabarito. Cada linha vai para a posição do trecho do gabarito com que ela
  mais se parece, e o lixo vai para o fim. Letra trocada, texto que falta e texto a mais
  continuam contando; só a ordem entre as linhas sai da conta, porque uma tela com dois
  painéis pode ter duas ordens certas. Nunca passa do CER. É a medida do portão de
  letras da validação.
- **WER** (taxa de erro de palavras): o mesmo, contando palavras.
- **quebras**: o app manda ao tradutor um parágrafo por linha (`paragrafos.py`).
  Em cada imagem, `quebras 7/8 (1 a mais)` quer dizer que ele achou 7 das 8
  quebras do gabarito e pôs 1 onde não havia. No resumo, **achadas** é a parte das
  quebras do gabarito que ele encontrou e **certas** é a parte das quebras que ele
  pôs que estão no gabarito.
- **linhas inteiras**: cada linha do gabarito com duas palavras ou mais é uma unidade
  que o tradutor deveria receber inteira. Em cada imagem, `linhas inteiras 5/6` quer
  dizer que 5 das 6 saíram inteiras e sozinhas numa linha do app. O CSV separa as que
  não saíram em três tipos:
  - **com sobra**: saíram junto de outra linha (quebra perdida);
  - **partidas**: saíram cortadas em linhas diferentes (quebra a mais, ou outra região
    no meio);
  - **faltando**: alguma palavra não foi lida.
- **tempo**: imagem + OCR + pós-processamento (a tradução não entra).
- **POR PASTA**: quando o teste pega mais de uma pasta, o resumo repete as médias
  de cada uma, para ver se um período ou um jogo foi pior que os outros.
- **POR CATEGORIA**: o mesmo por tipo de tela. O tipo de cada print está em
  [`categorias.json`](categorias.json): legenda, texto, menu, ficha ou letreiro. Ao
  coletar um print novo, acrescente o nome dele lá.

Só troque um padrão da produção quando a diferença aparecer **na média e na
maioria das imagens**, não numa imagem só.

## Testes automáticos

Os casos de montagem do texto em várias línguas (com caixas de OCR simuladas, sem
texto de jogo) e as métricas do benchmark têm testes em `tests/`. Eles rodam em menos
de um segundo, sem prints e sem OCR:

```
env\Scripts\python.exe -m unittest -v
```

Os casos ficam em `tests/casos_paragrafos.py`. Os marcados com `limite_conhecido` ainda
falham e aparecem como falha esperada.

## Como mudar uma regra com segurança

Toda regra nova de montagem do texto passou por estes passos:

1. **Caso reproduzível:** achar o print que erra e olhar as caixas que o OCR devolveu.
2. **Medida antes da regra:** medir o sinal em todos os prints antes de escrever a regra
   (por exemplo, o vão entre caixas dos itens que deviam quebrar e dos que deviam ficar
   juntos).
3. **Teste diferencial:** rodar a regra sobre as caixas guardadas e comparar com a versão
   da `main`, print a print, nas leituras dos dois motores. A ferramenta é
   `laboratorios/quebras/testar_regras.py --comparar main`, que fica fora do git, junto
   com as caixas guardadas.
4. **Testes automáticos** (`tests/`), com um caso simulado novo quando a regra puder
   afetar outra língua.
5. **Benchmark completo**, e só então a regra entra na produção.
