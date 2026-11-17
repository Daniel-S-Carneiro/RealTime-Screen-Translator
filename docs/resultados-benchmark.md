# Resultados do benchmark com o RapidOCR, print a print

*Anexo do [estudo de caso](estudo-de-caso-ocr.md). Benchmark de 17/11/2026, com o app
lendo o texto com o RapidOCR (modelos PP-OCRv6 small do PaddleOCR, na CPU)
e a correção por contexto desligada, o padrão.
As colunas de "antes" trazem o acerto de letras em benchmarks anteriores: **EasyOCR na GPU, 15/11**; **RapidOCR antes das colunas, 16/11**.
O resultado completo do EasyOCR está em [resultados-benchmark-easyocr.md](resultados-benchmark-easyocr.md), e a
comparação entre os motores, em [comparacao-motores-ocr.md](comparacao-motores-ocr.md).*

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
| Acerto de letras | **95,1%** |
| Acerto de palavras | **91,1%** |
| Quebras achadas | 89% |
| Quebras certas | 89% |
| Tempo médio por print | 0,8 s |
| Acerto de letras (EasyOCR na GPU, 15/11) | 89,8% |
| Acerto de palavras (EasyOCR na GPU, 15/11) | 77,7% |
| Quebras achadas / certas (EasyOCR na GPU, 15/11) | 74% / 86% |
| Tempo médio por print (EasyOCR na GPU, 15/11) | 3,0 s |
| Acerto de letras (RapidOCR antes das colunas, 16/11) | 92,2% |
| Acerto de palavras (RapidOCR antes das colunas, 16/11) | 88,0% |
| Quebras achadas / certas (RapidOCR antes das colunas, 16/11) | 70% / 86% |
| Tempo médio por print (RapidOCR antes das colunas, 16/11) | 1,2 s |

A média é puxada para baixo por poucas telas muito difíceis:
- mais da metade dos prints não erra **nenhuma letra**;
- 78 dos 90 prints acertam 95% ou mais das letras, e 63 acertam 99% ou mais.

Com a correção por contexto ligada, o acerto vai a 95,1% das letras e 91,2% das palavras, a 0,8 s por print, sem contar os ~5 s para carregar o BERT.

## Por jogo

| Jogo | Prints | Acerto de letras | Acerto de palavras | Quebras achadas | Quebras certas | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|---|
| Danganronpa: Trigger Happy Havoc | 5 | 100,0% | 100,0% | 100% | 100% | 98,5% | 100,0% |
| Doki Doki Literature Club | 3 | 100,0% | 100,0% | 29% | 100% | 91,6% | 100,0% |
| Exemplos públicos (pasta base) | 3 | 99,9% | 99,5% | 100% | 100% | 99,3% | 99,9% |
| Immortal Clan | 15 | 99,9% | 99,0% | 99% | 98% | 98,1% | 99,9% |
| The Elder Scrolls III: Morrowind | 6 | 99,5% | 98,0% | 93% | 97% | 77,3% | 82,0% |
| Mass Effect Legendary Edition | 5 | 99,3% | 91,9% | 100% | 100% | 99,4% | 99,3% |
| Persona 4 Golden | 7 | 96,7% | 94,7% | 97% | 100% | 93,6% | 96,7% |
| Fallout: New Vegas | 8 | 96,0% | 91,4% | 88% | 85% | 86,1% | 87,1% |
| Undertale | 3 | 95,0% | 86,9% | 100% | 100% | 90,2% | 95,0% |
| EVE Online | 12 | 94,5% | 87,1% | 92% | 88% | 85,4% | 87,1% |
| Night in the Woods | 14 | 87,7% | 79,8% | 91% | 62% | 85,0% | 87,5% |
| Caves of Qud | 9 | 86,6% | 83,6% | 73% | 78% | 83,7% | 86,9% |
| **Todos** | **90** | **95,1%** | **91,1%** | **89%** | **89%** | 89,8% | 92,2% |

## Print a print

### Danganronpa: Trigger Happy Havoc

Média: 100,0% das letras e 100,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `danganronpa_legenda_1` | 100,0% | 100,0% | 2 de 2 | 0 | 100,0% | 100,0% |
| `danganronpa_legenda_2` | 100,0% | 100,0% | 1 de 1 | 0 | 96,5% | 100,0% |
| `danganronpa_menu` | 100,0% | 100,0% | 4 de 4 | 0 | 99,4% | 100,0% |
| `danganronpa_titulo` | 100,0% | 100,0% | 2 de 2 | 0 | 96,8% | 100,0% |
| `danganronpa_tutorial` | 100,0% | 100,0% | — | 0 | 100,0% | 100,0% |

- `danganronpa_titulo`: texto inclinado: depois de endireitado, as palavras saem na ordem certa, mas as três linhas viram um parágrafo só.

### Doki Doki Literature Club

Média: 100,0% das letras e 100,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `doki_legenda_1` | 100,0% | 100,0% | 2 de 7 | 0 | 96,6% | 100,0% |
| `doki_legenda_2` | 100,0% | 100,0% | 2 de 7 | 0 | 93,6% | 100,0% |
| `doki_legenda_glitch` | 100,0% | 100,0% | — | 0 | 84,6% | 100,0% |

### Exemplos públicos (pasta base)

Média: 99,9% das letras e 99,5% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `documento_tooltip_habilidade` | 99,8% | 98,6% | 5 de 5 | 0 | 98,7% | 99,8% |
| `jogo_tooltip_habilidade` | 100,0% | 100,0% | 6 de 6 | 0 | 100,0% | 100,0% |
| `sintetico_labs` | 100,0% | 100,0% | — | 0 | 99,2% | 100,0% |

### Immortal Clan

Média: 99,9% das letras e 99,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `immortalclan_fase_efeito` | 100,0% | 100,0% | 2 de 2 | 0 | 95,8% | 100,0% |
| `immortalclan_loja_investidor` | 99,6% | 97,3% | 7 de 8 | 1 | 96,2% | 99,6% |
| `immortalclan_mapa_mist_island` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% | 100,0% |
| `immortalclan_missoes_capitulo` | 99,0% | 89,7% | 8 de 8 | 0 | 95,6% | 99,0% |
| `immortalclan_tomo_azure_blade` | 100,0% | 100,0% | 7 de 7 | 0 | 97,8% | 100,0% |
| `immortalclan_tomo_bloodburn` | 100,0% | 100,0% | 9 de 9 | 0 | 97,8% | 100,0% |
| `immortalclan_tomo_dragonbind` | 100,0% | 100,0% | 9 de 9 | 0 | 97,4% | 100,0% |
| `immortalclan_tomo_green_lotus` | 99,7% | 99,0% | 8 de 8 | 1 | 99,3% | 99,7% |
| `immortalclan_tomo_kunxu` | 100,0% | 100,0% | 9 de 9 | 0 | 99,4% | 100,0% |
| `immortalclan_tomo_malice` | 100,0% | 100,0% | 9 de 9 | 0 | 97,3% | 100,0% |
| `immortalclan_tomo_overwhelm` | 100,0% | 100,0% | 7 de 7 | 0 | 98,8% | 100,0% |
| `immortalclan_tomo_spirit_rhino` | 100,0% | 100,0% | 6 de 6 | 0 | 98,5% | 100,0% |
| `immortalclan_tomo_thunder_verdict` | 100,0% | 100,0% | 9 de 9 | 0 | 97,7% | 100,0% |
| `immortalclan_tomo_turbid_fire` | 100,0% | 100,0% | 9 de 9 | 0 | 99,8% | 100,0% |
| `immortalclan_tomo_windriding` | 99,5% | 98,5% | 9 de 9 | 0 | 99,3% | 99,5% |

### The Elder Scrolls III: Morrowind

Média: 99,5% das letras e 98,0% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `morrowind_avisos` | 100,0% | 100,0% | 2 de 2 | 0 | 89,6% | 100,0% |
| `morrowind_dialogo` | 99,9% | 99,2% | 23 de 26 | 3 | 76,6% | 82,7% |
| `morrowind_legenda` | 100,0% | 100,0% | — | 0 | 100,0% | 100,0% |
| `morrowind_magias` | 99,8% | 98,4% | 23 de 23 | 0 | 96,3% | 99,6% |
| `morrowind_nivel` | 97,9% | 93,5% | 9 de 12 | 0 | 69,5% | 79,8% |
| `morrowind_status` | 99,2% | 96,7% | 28 de 28 | 0 | 31,7% | 30,1% |

### Mass Effect Legendary Edition

Média: 99,3% das letras e 91,9% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `masseffect_aviso` | 97,9% | 75,0% | 1 de 1 | 0 | 100,0% | 97,9% |
| `masseffect_creditos` | 100,0% | 100,0% | 3 de 3 | 0 | 100,0% | 100,0% |
| `masseffect_dialogo` | 98,4% | 84,4% | 3 de 3 | 0 | 98,4% | 98,4% |
| `masseffect_diario` | 100,0% | 100,0% | 3 de 3 | 0 | 100,0% | 100,0% |
| `masseffect_legenda_1` | 100,0% | 100,0% | — | 0 | 98,8% | 100,0% |

- `masseffect_aviso`: o OCR come o espaço ao lado do ícone do botão ("Pressto").
- `masseffect_dialogo`: o OCR come o espaço entre algumas palavras ("resteasy", "willexploithim").

### Persona 4 Golden

Média: 96,7% das letras e 94,7% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `persona4_batalha` | 100,0% | 100,0% | 9 de 9 | 0 | 98,9% | 100,0% |
| `persona4_item_obtido` | 100,0% | 100,0% | — | 0 | 95,5% | 100,0% |
| `persona4_itens` | 82,5% | 68,3% | 13 de 13 | 0 | 69,5% | 82,5% |
| `persona4_legenda_1` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% | 100,0% |
| `persona4_legenda_2` | 100,0% | 100,0% | 1 de 1 | 0 | 94,1% | 100,0% |
| `persona4_menu` | 100,0% | 100,0% | 8 de 8 | 0 | 98,5% | 100,0% |
| `persona4_skills` | 94,2% | 94,7% | 5 de 6 | 0 | 98,8% | 94,2% |

- `persona4_itens`: na coluna de quantidade, o "×" vira "X" e vários números somem.

### Fallout: New Vegas

Média: 96,0% das letras e 91,4% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `fallout_bau` | 96,8% | 91,9% | 14 de 15 | 1 | 94,4% | 96,8% |
| `fallout_dialogo` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% | 100,0% |
| `fallout_legenda_1` | 100,0% | 100,0% | — | 1 | 100,0% | 100,0% |
| `fallout_legenda_2` | 99,0% | 90,5% | — | 0 | 99,0% | 99,0% |
| `fallout_missao` | 99,4% | 96,5% | 2 de 2 | 0 | 98,5% | 99,4% |
| `fallout_pipboy` | 76,8% | 64,2% | 22 de 31 | 5 | 53,4% | 50,7% |
| `fallout_special` | 95,9% | 88,2% | 16 de 16 | 6 | 48,0% | 50,6% |
| `fallout_traits` | 100,0% | 100,0% | 17 de 17 | 0 | 95,5% | 100,0% |

- `fallout_pipboy`: vários painéis, ícones e números pequenos na mesma tela.

### Undertale

Média: 95,0% das letras e 86,9% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `undertale_legenda_1` | 97,3% | 93,3% | — | 0 | 89,0% | 97,3% |
| `undertale_legenda_2` | 95,6% | 87,5% | — | 0 | 93,3% | 95,6% |
| `undertale_menu` | 92,1% | 80,0% | 8 de 8 | 0 | 88,1% | 92,1% |

### EVE Online

Média: 94,5% das letras e 87,1% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `eve_atributos` | 100,0% | 100,0% | 12 de 12 | 0 | 88,6% | 100,0% |
| `eve_ficha` | 99,1% | 96,7% | 25 de 27 | 2 | 96,3% | 99,1% |
| `eve_fila_treino` | 97,6% | 90,7% | 12 de 12 | 2 | 94,5% | 97,6% |
| `eve_filamento` | 91,2% | 90,0% | 5 de 5 | 0 | 88,5% | 91,2% |
| `eve_menu_contexto` | 99,0% | 96,0% | 23 de 23 | 1 | 72,0% | 73,4% |
| `eve_mercado` | 97,6% | 86,0% | 26 de 29 | 0 | 63,1% | 63,1% |
| `eve_minijogo` | 100,0% | 100,0% | 3 de 3 | 0 | 96,7% | 100,0% |
| `eve_overview` | 95,2% | 86,9% | 36 de 39 | 8 | 91,4% | 95,2% |
| `eve_painel_local` | 95,6% | 72,6% | 13 de 14 | 0 | 93,4% | 95,6% |
| `eve_perfil` | 98,5% | 89,5% | 3 de 5 | 0 | 97,0% | 98,5% |
| `eve_planos` | 100,0% | 100,0% | 6 de 6 | 0 | 100,0% | 100,0% |
| `eve_skills` | 60,6% | 37,3% | 37 de 43 | 14 | 42,8% | 32,1% |

- `eve_skills`: a grade já sai coluna por coluna; sobram o lixo lido de um texto vertical e o painel de treino, que entra no meio da última coluna.

### Night in the Woods

Média: 87,7% das letras e 79,8% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `nitw_cartaz_desaparecido` | 100,0% | 100,0% | 2 de 2 | 1 | 99,2% | 100,0% |
| `nitw_cartaz_harfest` | 100,0% | 100,0% | 5 de 5 | 0 | 100,0% | 100,0% |
| `nitw_demontower_fase` | 100,0% | 100,0% | 1 de 1 | 0 | 100,0% | 100,0% |
| `nitw_demontower_intro` | 97,3% | 91,3% | 1 de 1 | 1 | 85,6% | 97,3% |
| `nitw_demontower_pergunta` | 96,8% | 83,3% | 1 de 2 | 0 | 87,1% | 96,8% |
| `nitw_demontower_titulo` | 100,0% | 100,0% | 2 de 2 | 0 | 83,8% | 100,0% |
| `nitw_jornal` | 99,4% | 95,7% | — | 1 | 96,3% | 99,4% |
| `nitw_legenda_1` | 100,0% | 100,0% | — | 0 | 100,0% | 100,0% |
| `nitw_legenda_2` | 100,0% | 100,0% | — | 0 | 100,0% | 100,0% |
| `nitw_legenda_3` | 100,0% | 100,0% | — | 0 | 100,0% | 100,0% |
| `nitw_legenda_4` | 100,0% | 100,0% | — | 0 | 91,2% | 100,0% |
| `nitw_letreiro_banca` | 0,0% | 5,9% | 5 de 6 | 6 | 13,9% | 0,0% |
| `nitw_letreiro_diner` | 86,7% | 0,0% | — | 0 | 86,7% | 86,7% |
| `nitw_letreiros` | 53,3% | 41,7% | 4 de 4 | 4 | 45,6% | 53,3% |

- `nitw_letreiro_banca`: letreiro miúdo e borrado: o OCR solta lixo de texto que nem dá para ler no tamanho da tela.
- `nitw_letreiro_diner`: o OCR lê os pontos de neon como "·": as letras estão certas, mas a palavra conta como errada.
- `nitw_letreiros`: placas espalhadas e letra clara de pouco contraste.

### Caves of Qud

Média: 86,6% das letras e 83,6% das palavras.

| Print | Acerto de letras | Acerto de palavras | Quebras achadas | A mais | Letras: EasyOCR na GPU, 15/11 | Letras: RapidOCR antes das colunas, 16/11 |
|---|---|---|---|---|---|---|
| `qud_criacao_genotipo` | 96,8% | 95,5% | 10 de 12 | 3 | 92,9% | 96,8% |
| `qud_criacao_preset` | 84,1% | 80,7% | 8 de 21 | 4 | 84,2% | 84,1% |
| `qud_criacao_resumo` | 35,0% | 24,0% | 9 de 19 | 8 | 35,3% | 35,0% |
| `qud_criatura` | 99,6% | 98,7% | 6 de 6 | 0 | 98,5% | 99,6% |
| `qud_dialogo` | 99,5% | 98,6% | 8 de 8 | 0 | 95,6% | 99,5% |
| `qud_introducao` | 99,5% | 97,4% | 1 de 1 | 0 | 96,0% | 99,5% |
| `qud_lugar` | 100,0% | 100,0% | 1 de 1 | 0 | 93,9% | 100,0% |
| `qud_registro` | 99,8% | 98,3% | 26 de 26 | 0 | 90,9% | 99,4% |
| `qud_reputacao` | 64,9% | 59,4% | 26 de 36 | 12 | 65,9% | 67,9% |

- `qud_criacao_resumo`: as palavras saem quase todas certas, mas a caixa de tutorial vem depois das colunas, e o gabarito a põe antes.
- `qud_reputacao`: três colunas de texto por facção: as colunas saem separadas, mas o texto de várias facções se mistura.

Prints em que o erro passou de 100% em alguma medida (acerto mostrado como 0%): `nitw_letreiro_banca`.
