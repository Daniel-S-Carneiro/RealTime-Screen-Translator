# Resultados do benchmark com o RapidOCR, print a print

*Anexo do [estudo de caso](estudo-de-caso-ocr.md). Benchmark de 16/11/2026, com o app
lendo o texto com o RapidOCR (modelos PP-OCRv6 small do PaddleOCR, na CPU)
e a correção por contexto desligada, o padrão.
A coluna "antes" é o acerto de letras com o EasyOCR, no benchmark anterior;
o resultado completo dele está em [resultados-benchmark-easyocr.md](resultados-benchmark-easyocr.md). A comparação
entre os motores está em [comparacao-motores-ocr.md](comparacao-motores-ocr.md).*

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
| Acerto de letras | **92,2%** |
| Acerto de palavras | **88,0%** |
| Quebras achadas | 70% |
| Quebras certas | 86% |
| Tempo médio por print | 1,2 s |
| Acerto de letras antes (EasyOCR) | 89,8% |
| Acerto de palavras antes (EasyOCR) | 77,7% |
| Tempo médio por print antes (EasyOCR, GeForce MX350) | 3,0 s |

A média é puxada para baixo por poucas telas muito difíceis:
- mais da metade dos prints não erra **nenhuma letra**;
- 72 dos 90 prints acertam 95% ou mais das letras, e 60 acertam 99% ou mais.

Com a correção por contexto ligada, o acerto vai a 92,2% das letras e 88,1% das palavras, a 1,2 s por print, sem contar os ~5 s para carregar o BERT.

## Por jogo

| Jogo | Prints | Acerto de letras | Acerto de palavras | Quebras achadas | Quebras certas | Letras antes |
|---|---|---|---|---|---|---|
| Danganronpa: Trigger Happy Havoc | 5 | 100,0% | 100,0% | 67% | 100% | 98,5% |
| Doki Doki Literature Club | 3 | 100,0% | 100,0% | 29% | 100% | 91,6% |
| Exemplos públicos (pasta base) | 3 | 99,9% | 99,5% | 100% | 100% | 99,3% |
| Immortal Clan | 15 | 99,9% | 99,0% | 97% | 98% | 98,1% |
| Mass Effect Legendary Edition | 5 | 99,3% | 91,9% | 100% | 100% | 99,4% |
| Persona 4 Golden | 7 | 96,7% | 94,7% | 97% | 100% | 93,6% |
| Undertale | 3 | 95,0% | 86,9% | 38% | 100% | 90,2% |
| Night in the Woods | 14 | 87,5% | 79,8% | 70% | 73% | 85,0% |
| EVE Online | 12 | 87,1% | 79,8% | 65% | 85% | 85,4% |
| Fallout: New Vegas | 8 | 87,1% | 82,2% | 61% | 75% | 86,1% |
| Caves of Qud | 9 | 86,9% | 83,7% | 58% | 77% | 83,7% |
| The Elder Scrolls III: Morrowind | 6 | 82,0% | 77,9% | 64% | 87% | 77,3% |
| **Todos** | **90** | **92,2%** | **88,0%** | **70%** | **86%** | 89,8% |

## Print a print

### Danganronpa: Trigger Happy Havoc

Média: 100,0% das letras e 100,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `danganronpa_legenda_1` | 100,0% | 100,0% | 1 de 2 | 0 | 100,0% |
| `danganronpa_legenda_2` | 100,0% | 100,0% | 1 de 1 | 0 | 96,5% |
| `danganronpa_menu` | 100,0% | 100,0% | 4 de 4 | 0 | 99,4% |
| `danganronpa_titulo` | 100,0% | 100,0% | 0 de 2 | 0 | 96,8% |
| `danganronpa_tutorial` | 100,0% | 100,0% | — | 0 | 100,0% |

- `danganronpa_titulo`: texto inclinado: depois de endireitado, as palavras saem na ordem certa, mas as três linhas viram um parágrafo só.

### Doki Doki Literature Club

Média: 100,0% das letras e 100,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `doki_legenda_1` | 100,0% | 100,0% | 2 de 7 | 0 | 96,6% |
| `doki_legenda_2` | 100,0% | 100,0% | 2 de 7 | 0 | 93,6% |
| `doki_legenda_glitch` | 100,0% | 100,0% | — | 0 | 84,6% |

### Exemplos públicos (pasta base)

Média: 99,9% das letras e 99,5% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `documento_tooltip_habilidade` | 99,8% | 98,6% | 5 de 5 | 0 | 98,7% |
| `jogo_tooltip_habilidade` | 100,0% | 100,0% | 6 de 6 | 0 | 100,0% |
| `sintetico_labs` | 100,0% | 100,0% | — | 0 | 99,2% |

### Immortal Clan

Média: 99,9% das letras e 99,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `immortalclan_fase_efeito` | 100,0% | 100,0% | 2 de 2 | 0 | 95,8% |
| `immortalclan_loja_investidor` | 99,6% | 97,3% | 7 de 8 | 1 | 96,2% |
| `immortalclan_mapa_mist_island` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% |
| `immortalclan_missoes_capitulo` | 99,0% | 89,7% | 7 de 8 | 0 | 95,6% |
| `immortalclan_tomo_azure_blade` | 100,0% | 100,0% | 7 de 7 | 0 | 97,8% |
| `immortalclan_tomo_bloodburn` | 100,0% | 100,0% | 9 de 9 | 0 | 97,8% |
| `immortalclan_tomo_dragonbind` | 100,0% | 100,0% | 9 de 9 | 0 | 97,4% |
| `immortalclan_tomo_green_lotus` | 99,7% | 99,0% | 8 de 8 | 1 | 99,3% |
| `immortalclan_tomo_kunxu` | 100,0% | 100,0% | 9 de 9 | 0 | 99,4% |
| `immortalclan_tomo_malice` | 100,0% | 100,0% | 9 de 9 | 0 | 97,3% |
| `immortalclan_tomo_overwhelm` | 100,0% | 100,0% | 7 de 7 | 0 | 98,8% |
| `immortalclan_tomo_spirit_rhino` | 100,0% | 100,0% | 6 de 6 | 0 | 98,5% |
| `immortalclan_tomo_thunder_verdict` | 100,0% | 100,0% | 9 de 9 | 0 | 97,7% |
| `immortalclan_tomo_turbid_fire` | 100,0% | 100,0% | 9 de 9 | 0 | 99,8% |
| `immortalclan_tomo_windriding` | 99,5% | 98,5% | 8 de 9 | 0 | 99,3% |

### Mass Effect Legendary Edition

Média: 99,3% das letras e 91,9% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `masseffect_aviso` | 97,9% | 75,0% | 1 de 1 | 0 | 100,0% |
| `masseffect_creditos` | 100,0% | 100,0% | 3 de 3 | 0 | 100,0% |
| `masseffect_dialogo` | 98,4% | 84,4% | 3 de 3 | 0 | 98,4% |
| `masseffect_diario` | 100,0% | 100,0% | 3 de 3 | 0 | 100,0% |
| `masseffect_legenda_1` | 100,0% | 100,0% | — | 0 | 98,8% |

- `masseffect_aviso`: o OCR come o espaço ao lado do ícone do botão ("Pressto").
- `masseffect_dialogo`: o OCR come o espaço entre algumas palavras ("resteasy", "willexploithim").

### Persona 4 Golden

Média: 96,7% das letras e 94,7% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `persona4_batalha` | 100,0% | 100,0% | 9 de 9 | 0 | 98,9% |
| `persona4_item_obtido` | 100,0% | 100,0% | — | 0 | 95,5% |
| `persona4_itens` | 82,5% | 68,3% | 13 de 13 | 0 | 69,5% |
| `persona4_legenda_1` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% |
| `persona4_legenda_2` | 100,0% | 100,0% | 1 de 1 | 0 | 94,1% |
| `persona4_menu` | 100,0% | 100,0% | 8 de 8 | 0 | 98,5% |
| `persona4_skills` | 94,2% | 94,7% | 5 de 6 | 0 | 98,8% |

- `persona4_itens`: na coluna de quantidade, o "×" vira "X" e vários números somem.

### Undertale

Média: 95,0% das letras e 86,9% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `undertale_legenda_1` | 97,3% | 93,3% | — | 0 | 89,0% |
| `undertale_legenda_2` | 95,6% | 87,5% | — | 0 | 93,3% |
| `undertale_menu` | 92,1% | 80,0% | 3 de 8 | 0 | 88,1% |

### Night in the Woods

Média: 87,5% das letras e 79,8% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `nitw_cartaz_desaparecido` | 100,0% | 100,0% | 2 de 2 | 0 | 99,2% |
| `nitw_cartaz_harfest` | 100,0% | 100,0% | 4 de 5 | 0 | 100,0% |
| `nitw_demontower_fase` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% |
| `nitw_demontower_intro` | 97,3% | 91,3% | 0 de 1 | 1 | 85,6% |
| `nitw_demontower_pergunta` | 96,8% | 83,3% | 1 de 2 | 0 | 87,1% |
| `nitw_demontower_titulo` | 100,0% | 100,0% | 1 de 2 | 0 | 83,8% |
| `nitw_jornal` | 99,4% | 95,7% | — | 1 | 96,3% |
| `nitw_legenda_1` | 100,0% | 100,0% | — | 0 | 100,0% |
| `nitw_legenda_2` | 100,0% | 100,0% | — | 0 | 100,0% |
| `nitw_legenda_3` | 100,0% | 100,0% | — | 0 | 100,0% |
| `nitw_legenda_4` | 100,0% | 100,0% | — | 0 | 91,2% |
| `nitw_letreiro_banca` | 0,0% | 5,9% | 4 de 6 | 1 | 13,9% |
| `nitw_letreiro_diner` | 86,7% | 0,0% | — | 0 | 86,7% |
| `nitw_letreiros` | 53,3% | 41,7% | 3 de 4 | 3 | 45,6% |

- `nitw_letreiro_banca`: letreiro miúdo e borrado: o OCR solta lixo de texto que nem dá para ler no tamanho da tela.
- `nitw_letreiro_diner`: o OCR lê os pontos de neon como "·": as letras estão certas, mas a palavra conta como errada.
- `nitw_letreiros`: placas espalhadas e letra clara de pouco contraste.

### EVE Online

Média: 87,1% das letras e 79,8% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `eve_atributos` | 100,0% | 100,0% | 11 de 12 | 0 | 88,6% |
| `eve_ficha` | 99,1% | 96,7% | 13 de 27 | 2 | 96,3% |
| `eve_fila_treino` | 97,6% | 90,7% | 12 de 12 | 2 | 94,5% |
| `eve_filamento` | 91,2% | 90,0% | 5 de 5 | 0 | 88,5% |
| `eve_menu_contexto` | 73,4% | 74,0% | 15 de 23 | 1 | 72,0% |
| `eve_mercado` | 63,1% | 50,9% | 20 de 29 | 1 | 63,1% |
| `eve_minijogo` | 100,0% | 100,0% | 3 de 3 | 0 | 96,7% |
| `eve_overview` | 95,2% | 86,9% | 36 de 39 | 5 | 91,4% |
| `eve_painel_local` | 95,6% | 72,6% | 13 de 14 | 0 | 93,4% |
| `eve_perfil` | 98,5% | 89,5% | 1 de 5 | 0 | 97,0% |
| `eve_planos` | 100,0% | 100,0% | 4 de 6 | 0 | 100,0% |
| `eve_skills` | 32,1% | 6,8% | 9 de 43 | 14 | 42,8% |

- `eve_mercado`: dois painéis e uma barra de abas na mesma altura: rótulos dos dois lados saem juntos na mesma linha.
- `eve_skills`: grade de 3 colunas: agora as contagens pequenas são lidas, mas ocupam o vão entre as colunas, e a grade sai linha a linha.

### Fallout: New Vegas

Média: 87,1% das letras e 82,2% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `fallout_bau` | 96,8% | 91,9% | 13 de 15 | 1 | 94,4% |
| `fallout_dialogo` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% |
| `fallout_legenda_1` | 100,0% | 100,0% | — | 0 | 100,0% |
| `fallout_legenda_2` | 99,0% | 90,5% | — | 0 | 99,0% |
| `fallout_missao` | 99,4% | 96,5% | 2 de 2 | 0 | 98,5% |
| `fallout_pipboy` | 50,7% | 37,7% | 11 de 31 | 3 | 53,4% |
| `fallout_special` | 50,6% | 41,2% | 6 de 16 | 13 | 48,0% |
| `fallout_traits` | 100,0% | 100,0% | 17 de 17 | 0 | 95,5% |

- `fallout_pipboy`: vários painéis, ícones e números pequenos na mesma tela.
- `fallout_special`: a lista de títulos à esquerda e a descrição à direita saem misturadas, linha a linha.

### Caves of Qud

Média: 86,9% das letras e 83,7% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `qud_criacao_genotipo` | 96,8% | 95,5% | 10 de 12 | 3 | 92,9% |
| `qud_criacao_preset` | 84,1% | 80,7% | 8 de 21 | 4 | 84,2% |
| `qud_criacao_resumo` | 35,0% | 24,0% | 9 de 19 | 8 | 35,3% |
| `qud_criatura` | 99,6% | 98,7% | 6 de 6 | 0 | 98,5% |
| `qud_dialogo` | 99,5% | 98,6% | 6 de 8 | 0 | 95,6% |
| `qud_introducao` | 99,5% | 97,4% | 1 de 1 | 0 | 96,0% |
| `qud_lugar` | 100,0% | 100,0% | 1 de 1 | 0 | 93,9% |
| `qud_registro` | 99,4% | 94,1% | 21 de 26 | 0 | 90,9% |
| `qud_reputacao` | 67,9% | 64,2% | 13 de 36 | 8 | 65,9% |

- `qud_criacao_resumo`: as palavras saem quase todas certas, mas a caixa de tutorial vem depois das colunas, e o gabarito a põe antes.
- `qud_reputacao`: tabela de três colunas por facção.

### The Elder Scrolls III: Morrowind

Média: 82,0% das letras e 77,9% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras antes |
|---|---|---|---|---|---|
| `morrowind_avisos` | 100,0% | 100,0% | 0 de 2 | 0 | 89,6% |
| `morrowind_dialogo` | 82,7% | 84,4% | 14 de 26 | 5 | 76,6% |
| `morrowind_legenda` | 100,0% | 100,0% | — | 0 | 100,0% |
| `morrowind_magias` | 99,6% | 96,9% | 23 de 23 | 0 | 96,3% |
| `morrowind_nivel` | 79,8% | 74,2% | 6 de 12 | 0 | 69,5% |
| `morrowind_status` | 30,1% | 11,7% | 15 de 28 | 4 | 31,7% |

- `morrowind_status`: as palavras e os números saem quase todos certos, mas as duas colunas da ficha saem misturadas, linha a linha.

Prints em que o erro passou de 100% em alguma medida (acerto mostrado como 0%): `nitw_letreiro_banca`.
