# Benchmark de OCR

Mede o pipeline **de produção** (`pipeline_ocr.reconhecer_texto`, o mesmo que o
app usa) em todas as imagens de `dataset/`. Substitui os laboratórios antigos,
que copiavam o pipeline e usavam uma imagem só.

## Como coletar prints

1. Rode o app pelo código (`env\Scripts\python.exe main.py`) com
   `DEBUG_MODE = True`.
2. No ícone da bandeja, marque **Salvar prints para o benchmark**.
3. Use o "Traduzir Área" normalmente. Cada captura gera em `dataset/`:
   - `coleta_AAAAMMDD_HHMMSS.png`: o print bruto;
   - `coleta_AAAAMMDD_HHMMSS.rascunho.txt`: o que o OCR leu.
4. Abra o print, **corrija o rascunho olhando a imagem** e salve como
   `coleta_AAAAMMDD_HHMMSS.txt` (sem o `.rascunho`). Pode renomear o par para
   algo descritivo, como `rpg_menu_fundo_claro.png` + `rpg_menu_fundo_claro.txt`.

Imagens sem `.txt` aparecem como `[PENDENTE]` e ficam fora da conta.

### O que vale coletar (15 a 30 prints)

- fundo claro e fundo escuro;
- texto colorido (laranja, roxo, vermelho) e texto sobre imagem/textura;
- fontes estilizadas, pixel art e letras pequenas;
- números e porcentagens (dano, HP, preço), que não podem errar;
- menus curtos ("New Game", "Settings") e diálogos longos;
- nomes próprios de personagens e lugares.

### Como escrever o gabarito

- Copie o texto **exatamente como aparece** na imagem, com a mesma pontuação.
- Quebras de linha e espaços repetidos não importam: o benchmark os ignora,
  assim como maiúsculas e minúsculas.
- A ordem é a de leitura: de cima para baixo, da esquerda para a direita.

## Como rodar

Na pasta do projeto:

```
env\Scripts\python.exe benchmark\benchmark.py
env\Scripts\python.exe benchmark\benchmark.py --detalhes
env\Scripts\python.exe benchmark\benchmark.py --configs producao,imagem_binarizado --repeticoes 3
```

| Opção | O que faz |
|---|---|
| `--configs` | Quais configurações rodar (padrão: todas) |
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
| `pontuacao_agressiva` | Liga as regras de regex ajustadas no `teste.png` |
| `pontuacao_agressiva+bert` | Regex agressivo + correção com SpellChecker e BERT |

## Como ler o resultado

- **CER** (taxa de erro de caracteres): quantas letras precisariam ser
  corrigidas, dividido pelo tamanho do gabarito. 2% = 2 letras erradas a cada 100.
  Quanto menor, melhor.
- **WER** (taxa de erro de palavras): o mesmo, contando palavras.
- **tempo**: imagem + OCR + pós-processamento (a tradução não entra).

Só troque um padrão da produção quando a diferença aparecer **na média e na
maioria das imagens**, não numa imagem só.
