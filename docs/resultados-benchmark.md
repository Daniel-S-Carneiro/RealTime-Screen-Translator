# Resultados do benchmark, print a print

*Anexo do [estudo de caso](estudo-de-caso-ocr.md). Benchmark de 15/11/2026, com o app
como está na branch `quebras-de-linha` (correção por contexto desligada, o padrão).*

São **90 prints com gabarito**: 87 de 11 jogos e 3 exemplos públicos.
Os prints de jogos ficam fora do repositório, porque são telas de jogos de terceiros;
só os 3 exemplos da pasta `base` estão no git.

## Como ler

- **Acerto de letras** = 100% menos a CER (taxa de erro de caracteres): quanto do
  texto o app leu igual ao gabarito, contando letras trocadas, que faltaram ou que
  sobraram.
- **Acerto de palavras** = 100% menos a WER: o mesmo, contando palavras. Basta uma
  letra errada para a palavra inteira contar como erro.
- **Quebras achadas:** das quebras de linha do gabarito, quantas o app pôs. **A mais:**
  quebras que o app pôs onde o gabarito não tem. "—" quer dizer que o gabarito é uma
  linha só.
- O gabarito segue a ordem de leitura de uma pessoa: numa tela com painéis, um painel
  de cada vez. Palavras certas em outra ordem também contam como erro.
- Quando o app lê mais lixo do que texto, o erro passa de 100% e o acerto aparece
  como 0%.

## Média geral

| Medida | Resultado |
|---|---|
| Acerto de letras | **89,8%** |
| Acerto de palavras | **77,7%** |
| Quebras achadas | 74% |
| Quebras certas | 86% |
| Tempo médio por print (GeForce MX350) | 3,0 s |

A média é puxada para baixo por poucas telas muito difíceis:
- metade dos prints acerta **96,4%** das letras ou mais (a mediana);
- 55 dos 90 prints acertam 95% ou mais das letras, e 25 acertam 99% ou mais.

Com a correção por contexto ligada, o acerto vai a 89,8% das letras e 78,1% das palavras, a 3,1 s por print, sem contar os ~5 s para carregar o BERT.

## Por jogo

| Jogo | Prints | Acerto de letras | Acerto de palavras | Quebras achadas | Quebras certas |
|---|---|---|---|---|---|
| Mass Effect Legendary Edition | 5 | 99,4% | 96,9% | 100% | 100% |
| Exemplos públicos (pasta base) | 3 | 99,3% | 96,1% | 100% | 100% |
| Danganronpa: Trigger Happy Havoc | 5 | 98,5% | 94,1% | 67% | 100% |
| RPG de cultivo (primeiro jogo testado) | 15 | 98,1% | 91,5% | 96% | 91% |
| Persona 4 Golden | 7 | 93,6% | 82,8% | 97% | 100% |
| Doki Doki Literature Club | 3 | 91,6% | 69,7% | 29% | 80% |
| Undertale | 3 | 90,2% | 63,2% | 38% | 100% |
| Fallout: New Vegas | 8 | 86,1% | 77,3% | 61% | 81% |
| EVE Online | 12 | 85,4% | 74,8% | 73% | 87% |
| Night in the Woods | 14 | 85,0% | 64,4% | 78% | 78% |
| Caves of Qud | 9 | 83,7% | 70,6% | 66% | 80% |
| The Elder Scrolls III: Morrowind | 6 | 77,3% | 57,4% | 62% | 79% |
| **Todos** | **90** | **89,8%** | **77,7%** | **74%** | **86%** |

## Print a print

### Mass Effect Legendary Edition

Média: 99,4% das letras e 96,9% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `masseffect_aviso` | 100,0% | 100,0% | 1 de 1 | 0 |
| `masseffect_creditos` | 100,0% | 100,0% | 3 de 3 | 0 |
| `masseffect_dialogo` | 98,4% | 90,6% | 3 de 3 | 0 |
| `masseffect_diario` | 100,0% | 100,0% | 3 de 3 | 0 |
| `masseffect_legenda_1` | 98,8% | 93,9% | — | 0 |

### Exemplos públicos (pasta base)

Média: 99,3% das letras e 96,1% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `documento_tooltip_habilidade` | 98,7% | 94,3% | 5 de 5 | 0 |
| `jogo_tooltip_habilidade` | 100,0% | 100,0% | 6 de 6 | 0 |
| `sintetico_labs` | 99,2% | 94,1% | — | 0 |

### Danganronpa: Trigger Happy Havoc

Média: 98,5% das letras e 94,1% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `danganronpa_legenda_1` | 100,0% | 100,0% | 1 de 2 | 0 |
| `danganronpa_legenda_2` | 96,5% | 93,8% | 1 de 1 | 0 |
| `danganronpa_menu` | 99,4% | 96,8% | 4 de 4 | 0 |
| `danganronpa_titulo` | 96,8% | 80,0% | 0 de 2 | 0 |
| `danganronpa_tutorial` | 100,0% | 100,0% | — | 0 |

- `danganronpa_titulo`: texto inclinado: depois de endireitado, as palavras saem na ordem certa, mas as três linhas viram um parágrafo só.

### RPG de cultivo (primeiro jogo testado)

Média: 98,1% das letras e 91,5% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `coleta_20261102_062239` | 98,8% | 93,4% | 7 de 7 | 0 |
| `coleta_20261102_062304` | 99,4% | 96,7% | 9 de 9 | 0 |
| `coleta_20261102_062342` | 99,8% | 98,9% | 9 de 9 | 0 |
| `coleta_20261102_062420` | 97,8% | 95,2% | 9 de 9 | 1 |
| `coleta_20261102_062455` | 97,3% | 91,1% | 9 de 9 | 1 |
| `coleta_20261102_062554` | 99,3% | 96,1% | 8 de 8 | 1 |
| `coleta_20261102_062706` | 99,3% | 95,6% | 8 de 9 | 0 |
| `coleta_20261102_062745` | 97,8% | 93,7% | 7 de 7 | 2 |
| `coleta_20261102_062910` | 97,4% | 88,9% | 9 de 9 | 2 |
| `coleta_20261102_062943` | 98,5% | 91,8% | 6 de 6 | 1 |
| `coleta_20261102_063011` | 97,7% | 94,4% | 9 de 9 | 1 |
| `coleta_20261102_063145` | 96,2% | 78,4% | 7 de 8 | 1 |
| `coleta_20261102_063316` | 100,0% | 100,0% | 1 de 1 | 0 |
| `coleta_20261102_063334` | 95,8% | 76,0% | 2 de 2 | 0 |
| `coleta_20261102_063407` | 95,6% | 82,8% | 6 de 8 | 1 |

### Persona 4 Golden

Média: 93,6% das letras e 82,8% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `persona4_batalha` | 98,9% | 92,9% | 9 de 9 | 0 |
| `persona4_item_obtido` | 95,5% | 90,9% | — | 0 |
| `persona4_itens` | 69,5% | 34,2% | 12 de 13 | 0 |
| `persona4_legenda_1` | 100,0% | 100,0% | 1 de 1 | 0 |
| `persona4_legenda_2` | 94,1% | 82,3% | 1 de 1 | 0 |
| `persona4_menu` | 98,5% | 90,0% | 8 de 8 | 0 |
| `persona4_skills` | 98,8% | 89,5% | 6 de 6 | 0 |

- `persona4_itens`: os números em itálico e a coluna de "×" não são lidos.

### Doki Doki Literature Club

Média: 91,6% das letras e 69,7% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `doki_legenda_1` | 96,6% | 79,2% | 2 de 7 | 0 |
| `doki_legenda_2` | 93,6% | 76,0% | 2 de 7 | 0 |
| `doki_legenda_glitch` | 84,6% | 53,9% | — | 1 |

### Undertale

Média: 90,2% das letras e 63,2% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `undertale_legenda_1` | 89,0% | 46,7% | — | 0 |
| `undertale_legenda_2` | 93,3% | 75,0% | — | 0 |
| `undertale_menu` | 88,1% | 68,0% | 3 de 8 | 0 |

### Fallout: New Vegas

Média: 86,1% das letras e 77,3% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `fallout_bau` | 94,4% | 81,1% | 13 de 15 | 1 |
| `fallout_dialogo` | 100,0% | 100,0% | 1 de 1 | 0 |
| `fallout_legenda_1` | 100,0% | 100,0% | — | 0 |
| `fallout_legenda_2` | 99,0% | 95,2% | — | 0 |
| `fallout_missao` | 98,5% | 93,0% | 2 de 2 | 0 |
| `fallout_pipboy` | 53,4% | 32,1% | 11 de 31 | 4 |
| `fallout_special` | 48,0% | 27,9% | 7 de 16 | 6 |
| `fallout_traits` | 95,5% | 88,9% | 16 de 17 | 1 |

- `fallout_pipboy`: vários painéis, ícones e números pequenos na mesma tela.
- `fallout_special`: fonte de faroeste: "STRENGTH" sai "S7REIOII".

### EVE Online

Média: 85,4% das letras e 74,8% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `eve_atributos` | 88,6% | 71,0% | 11 de 12 | 0 |
| `eve_ficha` | 96,3% | 86,9% | 13 de 27 | 2 |
| `eve_fila_treino` | 94,5% | 90,7% | 12 de 12 | 0 |
| `eve_filamento` | 88,5% | 72,5% | 5 de 5 | 1 |
| `eve_menu_contexto` | 72,0% | 74,0% | 14 de 23 | 4 |
| `eve_mercado` | 63,1% | 50,9% | 21 de 29 | 1 |
| `eve_minijogo` | 96,7% | 91,2% | 2 de 3 | 0 |
| `eve_overview` | 91,4% | 77,4% | 35 de 39 | 5 |
| `eve_painel_local` | 93,4% | 75,8% | 14 de 14 | 3 |
| `eve_perfil` | 97,0% | 79,0% | 3 de 5 | 0 |
| `eve_planos` | 100,0% | 100,0% | 4 de 6 | 0 |
| `eve_skills` | 42,8% | 28,8% | 26 de 43 | 8 |

- `eve_mercado`: dois painéis e o "&" que o OCR não lê.
- `eve_skills`: grade de 3 colunas, e as contagens pequenas nem são detectadas.

### Night in the Woods

Média: 85,0% das letras e 64,4% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `nitw_cartaz_desaparecido` | 99,2% | 95,3% | 2 de 2 | 0 |
| `nitw_cartaz_harfest` | 100,0% | 100,0% | 4 de 5 | 0 |
| `nitw_demontower_fase` | 100,0% | 100,0% | 1 de 1 | 0 |
| `nitw_demontower_intro` | 85,6% | 47,8% | 1 de 1 | 1 |
| `nitw_demontower_pergunta` | 87,1% | 50,0% | 1 de 2 | 0 |
| `nitw_demontower_titulo` | 83,8% | 41,7% | 2 de 2 | 0 |
| `nitw_jornal` | 96,3% | 73,9% | — | 1 |
| `nitw_legenda_1` | 100,0% | 100,0% | — | 0 |
| `nitw_legenda_2` | 100,0% | 100,0% | — | 0 |
| `nitw_legenda_3` | 100,0% | 100,0% | — | 0 |
| `nitw_legenda_4` | 91,2% | 83,3% | — | 0 |
| `nitw_letreiro_banca` | 13,9% | 0,0% | 5 de 6 | 0 |
| `nitw_letreiro_diner` | 86,7% | 0,0% | — | 0 |
| `nitw_letreiros` | 45,6% | 33,3% | 2 de 4 | 3 |

- `nitw_letreiro_banca`: letreiro miúdo e borrado: o OCR solta lixo de texto que nem dá para ler no tamanho da tela.
- `nitw_letreiro_diner`: o OCR lê os pontos de neon como hífen ("CLIK-CLAK-DINER"): as letras estão certas, mas a palavra conta como errada.
- `nitw_letreiros`: placas espalhadas e letra clara de pouco contraste.

### Caves of Qud

Média: 83,7% das letras e 70,6% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `qud_criacao_genotipo` | 92,9% | 76,1% | 10 de 12 | 3 |
| `qud_criacao_preset` | 84,2% | 73,5% | 10 de 21 | 4 |
| `qud_criacao_resumo` | 35,3% | 12,0% | 14 de 19 | 4 |
| `qud_criatura` | 98,5% | 94,8% | 6 de 6 | 1 |
| `qud_dialogo` | 95,6% | 88,9% | 6 de 8 | 1 |
| `qud_introducao` | 96,0% | 87,2% | 1 de 1 | 0 |
| `qud_lugar` | 93,9% | 72,2% | 1 de 1 | 0 |
| `qud_registro` | 90,9% | 81,8% | 23 de 26 | 0 |
| `qud_reputacao` | 65,9% | 48,7% | 15 de 36 | 8 |

- `qud_criacao_resumo`: as palavras saem quase todas certas, mas a caixa de tutorial vem depois das colunas, e o gabarito a põe antes.
- `qud_reputacao`: tabela de três colunas por facção.

### The Elder Scrolls III: Morrowind

Média: 77,3% das letras e 57,4% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais |
|---|---|---|---|---|
| `morrowind_avisos` | 89,6% | 57,9% | 0 de 2 | 0 |
| `morrowind_dialogo` | 76,6% | 54,9% | 12 de 26 | 10 |
| `morrowind_legenda` | 100,0% | 100,0% | — | 0 |
| `morrowind_magias` | 96,3% | 76,6% | 23 de 23 | 0 |
| `morrowind_nivel` | 69,5% | 43,5% | 8 de 12 | 2 |
| `morrowind_status` | 31,7% | 11,7% | 13 de 28 | 3 |

- `morrowind_status`: os números alinhados à direita não são lidos, e a fonte medieval troca letras.

Prints em que o erro passou de 100% em alguma medida (acerto mostrado como 0%): `nitw_letreiro_banca`.
