# Resultados da validação: rodada 1

*Medida em 24/11/2026, com o código do ponto de congelamento
`referencia-validacao-2026-11-22`. O `git diff` dos `.py` da raiz saiu vazio e os 106
testes passaram. As regras do portão estão na [referência da
validação](referencia-validacao.md), e o passo a passo, no [plano de
validação](plano-de-validacao.md).*

Comandos, com a mesma configuração da referência:

```
env\Scripts\python.exe benchmark\benchmark.py --configs producao --periodo validacao --detalhes
env\Scripts\python.exe benchmark\benchmark.py --configs producao --periodo outra-lingua --idioma es --detalhes
```

O app foi medido uma vez. Depois disso, 14 gabaritos foram corrigidos (veja [Os gabaritos
corrigidos](#os-gabaritos-corrigidos)) e a medida foi repetida com o mesmo código. Os
dois resultados ficam neste anexo. Os relatórios ficam fora do git, em
`relatorios/benchmark/`:

| Medida | Inglês | Espanhol |
|---|---|---|
| Primeira, com os gabaritos originais | `benchmark_20261124_163634.csv` | `benchmark_20261124_163714.csv` |
| Com os gabaritos corrigidos | `benchmark_20261124_164705.csv` | `benchmark_20261124_164716.csv` |

A saída completa está em `relatorios/validacao/`, e os gabaritos antigos, em
`relatorios/validacao/gabaritos_antes_da_correcao/`.

## O veredito: não passou no portão

| Portão | Exigido | Primeira medida | Com os gabaritos corrigidos | |
|---|---|---|---|---|
| Letras sem ordem | 93% ou mais | **92,3%** | **92,3%** | não passou |
| Linhas inteiras | 75% ou mais | **65%** (188 de 289) | **66%** (190 de 290) | não passou |
| Nenhum tipo mais de 5 pontos abaixo dos 90 prints | | letreiro nas letras; todos os tipos nas linhas | igual | não passou |

O plano esperava algo entre 93% e 96% nas letras sem ordem e entre 70% e 78% nas linhas
inteiras. As letras ficaram um pouco abaixo dessa faixa e as linhas, bem abaixo. A
correção dos gabaritos não mudou o veredito.

Daqui em diante, os números são os dos gabaritos corrigidos. Onde a correção mudou algum
número, a primeira medida aparece entre parênteses.

## Por tipo de tela

Validação (50 prints em inglês) contra os 90 prints da referência:

| Tipo | Prints | Letras sem ordem | Referência | Diferença | Linhas inteiras | Referência | Diferença |
|---|---:|---:|---:|---:|---:|---:|---:|
| ficha | 13 | 96,5% | 95,2% | +1,3 | 66% (104/157) (antes 63%) | 77% | **−11** |
| legenda | 12 | 99,7% | 99,4% | +0,3 | 71% (10/14) | 81% | **−10** |
| letreiro | 9 | 70,3% | 85,9% | **−15,6** | 25% (3/12) (antes 43%) | 78% | **−53** |
| menu | 11 | 95,0% | 98,8% | −3,8 | 67% (57/85) | 80% | **−13** |
| texto | 5 | 97,2% | 99,5% | −2,3 | 73% (16/22) | 92% | **−19** |

Legendas, letreiros e textos têm poucas linhas de duas palavras ou mais (14, 12 e 22),
então uma linha a mais ou a menos muda muito a porcentagem deles.

## Por jogo

| Jogo | Prints | Letras sem ordem | Linhas inteiras |
|---|---:|---:|---:|
| Butterfly Soup | 10 | 98,8% | 81% (21/26) |
| Disco Elysium | 10 | 96,4% | 64% (89/140) |
| Katawa Shoujo | 10 | 99,4% | 68% (21/31) |
| Path of Exile | 10 | 95,0% | 73% (51/70) |
| The Big Con | 10 | 71,7% | 35% (8/23) (antes 27%) |

## As outras medidas

| Medida | Validação | Referência (90 prints) |
|---|---:|---:|
| Letras, na ordem lida | 91,3% | 95,8% |
| Quebras achadas | 86,7% (286/330) (antes 82,7%) | 91,9% |
| Quebras certas | 89,9% (286/318) (antes 91,8%) | 90,8% |
| Quebras a mais | 32 (antes 26) | 69 |
| Tempo por print: média e p95 | 0,86 s e 1,70 s | 0,8 s e 2,5 s |
| Linhas perdidas: com sobra, partidas, faltando | 28, 22 e 50 (antes 37, 18 e 46) | 33, 22 e 67 |

## O que os números dizem

Esta é a primeira leitura. A classificação de cada erro é a fase 4 do plano.

**As letras só reprovaram por causa dos letreiros do The Big Con.** Sem esse jogo, os
outros 40 prints dão **97,4%** nas letras sem ordem, o mesmo nível dos 90 prints. Os piores
são o cartaz da Crystal Horm (18% de acerto), o Cooper's Market em letra cursiva (20%), a
placa do trem escrita à mão (53%) e o Mallton Mall em arco (67%). Letra torta, em arco ou
cursiva é limite da leitura (o Problema 5), não das regras de montagem. Mesmo assim, o
portão foi fixado antes e conta esses prints.

**As linhas inteiras reprovaram de forma ampla.** Sem o The Big Con, ficam em **68%**
(182 de 267), ainda abaixo dos 75%. Das 100 linhas que não saíram inteiras, metade tem uma
palavra que nem foi lida (leitura), e a outra metade foi mal montada: 28 saíram junto de
outra linha e 22 saíram cortadas. As perdas se concentram nas fichas e nos menus do Disco
Elysium e do Path of Exile:
- `disco_ficha_2`: 7 de 19, com 9 linhas cortadas;
- `disco_ficha_4`: 3 de 14, com 7 faltando e 4 cortadas;
- `disco_menu_2`: 1 de 9;
- `poe_ficha_5`: 5 de 11, com 5 juntas de outra linha.

É o sinal que o plano temia: as regras de montagem não se generalizaram tão bem quanto
pareciam nos 90 prints.

**O que se manteve.** Legendas e textos continuam em 97% a 99% nas letras. Quando o app
põe uma quebra, ela está certa em 89,9% das vezes, perto dos 90,8% da referência, e as
quebras a mais por print caíram. O tempo ficou dentro do esperado.

## Os gabaritos corrigidos

O [README do benchmark](../benchmark/README.md) manda escrever **uma linha por parágrafo
ou item**, e juntar numa linha só a frase que continua embaixo porque não coube na caixa.
Os 90 prints seguem isso também nos letreiros: a manchete do jornal do Night in the Woods,
que ocupa várias linhas na tela, está numa linha só no gabarito.

Depois da primeira medida, apareceu que 14 gabaritos escritos em 24/11 quebravam as
frases como na tela:
- **The Big Con, 6:** o diário e 5 letreiros ("LINDA'S VIDEO STORE", "COOPER'S MARKET",
  "THIS WAY TO TRAIN", "TRY THE CRYSTAL HORM CHALLENGE!" e a fala "Whoa, I'm
  INFORMATION.");
- **Stardew Valley, 8:** as 5 falas com mais de uma linha, as 2 fichas e o aviso das
  sementes, em que a assinatura do prefeito tinha ido para outra linha.

Os outros 44 gabaritos em inglês já seguiam a regra.

A correção foi feita olhando só os `.png`. Um script conferiu, em cada um dos 14, que as
palavras continuam as mesmas e na mesma ordem: só mudou onde a linha quebra. Por isso as
letras não mudaram em nenhum print, e nenhum print fora desses 14 mudou de resultado.

| | Primeira medida | Gabaritos corrigidos |
|---|---:|---:|
| Inglês: linhas inteiras | 65% (188/289) | 66% (190/290) |
| Inglês: letreiros, linhas inteiras | 43% (3/7) | 25% (3/12) |
| Inglês: diário do The Big Con | 3 de 14 | 5 de 10 |
| Espanhol: linhas inteiras | 24% (9/37) | 38% (8/21) |
| Espanhol: falas, linhas inteiras | 12% (2/17) | 50% (3/6) |

Nos letreiros, a correção piorou o número. Os nomes e frases que agora são uma linha só,
como "COOPER'S MARKET", quase nunca saem inteiros. Das 9 linhas que não saem inteiras, 6
têm alguma palavra mal lida, e 3 saem em pedaços.

**Uma conclusão da primeira medida estava errada.** Com os gabaritos quebrados, as falas em
espanhol pareciam ter sido todas juntadas pelo app. Com o gabarito certo, só 3 das 6
falas saem inteiras. Duas saem cortadas em duas linhas e uma perde uma palavra.

## O jogo em espanhol (fora do portão)

Stardew Valley, 10 prints, com a Origem do app em espanhol. É a primeira medida do app
fora do inglês e não passa nem reprova.

| Tipo | Prints | Letras sem ordem | Letras | Linhas inteiras |
|---|---:|---:|---:|---:|
| **Total** | 10 | 95,0% | 91,1% | 38% (8/21) (antes 24%) |
| ficha | 2 | 76,6% | 56,7% | 33% (4/12) |
| legenda | 6 | 99,7% | 99,7% | 50% (3/6) |
| menu | 1 | 100% | 100% | 100% (1/1) |
| texto | 1 | 99,0% | 99,0% | 0% (0/2) |

As falas foram lidas com acentos, ñ, ¿ e ¡ quase sem erro, mas metade delas não chega
inteira ao tradutor. A tela de criação de personagem, com rótulos em duas linhas e
colunas de números, é a pior nas letras. Esses números viram a referência do app em
espanhol.

## Próximos passos

1. Fase 4 do plano: classificar cada linha perdida, por jogo e por tipo de tela. Feito em
   24/11: [Por que as linhas se perderam](classificacao-linhas-perdidas.md). Um erro que
   aparece num jogo só não vira regra.
2. A partir daqui, os 50 prints passam a ser conjunto de ajuste, com os 90 da referência.
   A próxima prova é a rodada 2, com jogos que nenhuma correção viu.
3. Antes da rodada 2, conferir cada gabarito contra a regra do README **antes** de medir.
