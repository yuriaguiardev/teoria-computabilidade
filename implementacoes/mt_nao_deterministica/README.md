# MT Não Determinística — formalização e implementação

**Modelo:** Opção 4 (Máquina de Turing Não Determinística — MTND).
**Problema:** reconhecer **L = { ww : w ∈ {a,b}+ }** (palavras duplicadas).

## 1. Definição formal
Uma MTND é a 8-upla `M = (Q, Σ, Γ, δ, q0, b, F, q_rej)` em que a transição é uma
**relação** (não uma função):

```
δ : (Q × Γ) → P(Q × Γ × {L, R, S})
```

Para esta máquina:
- **Q** = { q0, qScan, qFindLeft, qScanRight, qToBoundaryA, qToBoundaryB,
  qSeekSecondA, qSeekSecondB, qCheckSecond, qAccept } — **|Q| = 10 (> 8)**.
- **Σ** = { a, b }.
- **Γ** = { a, b, A, B, Sa, Sb, C, _ } (`_` é o branco `b`).
- **q0** = q0 · **F** = { qAccept }.
- **δ** tem **37 transições** (tabela na Seção 4).

### Critério de aceitação (não determinístico)
`w ∈ L(M)` **sse algum ramo** da árvore de computação atinge `qAccept`. Um ramo
**morre** (rejeita) quando não há transição aplicável. `w` é aceita se existir ao
menos um caminho aceitante; rejeitada se **todos** os ramos morrerem.

## 2. Significado dos símbolos de fita
| Símbolo | Significado |
|---|---|
| `a`, `b` | símbolo de entrada ainda **não processado** |
| `A`, `B` | célula da **1ª metade** já casada (era `a` / era `b`) |
| `Sa`, `Sb` | **tag**: início (adivinhado) da 2ª metade, guardando o valor `a`/`b` |
| `C` | célula da **2ª metade** já consumida |
| `_` | branco |

## 3. Ideia do algoritmo
1. **q0** força a 1ª célula a ficar na 1ª metade (garante `w` não-vazia).
2. **qScan** varre para a direita e, em cada símbolo, faz a **escolha não
   determinística**: *continuar na 1ª metade* **ou** *declarar “aqui começa a 2ª
   metade”* (tagueando a célula como `Sa`/`Sb`). Cada escolha cria um ramo.
3. A verificação (determinística) repete: marcar o símbolo mais à esquerda **não
   casado** da 1ª metade (`a→A`/`b→B`) e casá-lo com o mais à esquerda **não
   consumido** da 2ª metade (tag ou `a`/`b`), marcando-o `C`. Mismatch → ramo morre.
4. **qCheckSecond** aceita quando as duas metades se esgotam **juntas** (mesmo
   tamanho e mesmo conteúdo, na mesma ordem — não é palíndromo!).

## 4. Tabela de transições δ
Formato de cada destino: `(novo estado, escreve, movimento)`. Pares (estado,
símbolo) **ausentes** = ramo morre (sem transição).

| Estado | lê `a` | lê `b` | lê `A` | lê `B` | lê `Sa` | lê `Sb` | lê `C` | lê `_` |
|---|---|---|---|---|---|---|---|---|
| **q0** | qScan,a,R | qScan,b,R | — | — | — | — | — | — |
| **qScan** | qScan,a,R **\|** qFindLeft,Sa,L | qScan,b,R **\|** qFindLeft,Sb,L | — | — | — | — | — | — |
| **qFindLeft** | self,a,L | self,b,L | self,A,L | self,B,L | self,Sa,L | self,Sb,L | self,C,L | qScanRight,_,R |
| **qScanRight** | qToBoundaryA,A,R | qToBoundaryB,B,R | self,A,R | self,B,R | — | — | qCheckSecond,C,R | — |
| **qToBoundaryA** | self,a,R | self,b,R | self,A,R | self,B,R | qFindLeft,C,L | — | qSeekSecondA,C,R | — |
| **qToBoundaryB** | self,a,R | self,b,R | self,A,R | self,B,R | — | qFindLeft,C,L | qSeekSecondB,C,R | — |
| **qSeekSecondA** | qFindLeft,C,L | — | — | — | — | — | self,C,R | — |
| **qSeekSecondB** | — | qFindLeft,C,L | — | — | — | — | self,C,R | — |
| **qCheckSecond** | — | — | — | — | — | — | self,C,R | qAccept,_,S |
| **qAccept** | (aceita) | | | | | | | |

> A **célula em qScan** é o único ponto de **não determinismo** (dois destinos no
> mesmo par estado/símbolo): adivinhar o ponto médio.

## 5. Por que não é trivial / limites
- **L = {ww} não é livre de contexto** (lema do bombeamento para LLCs) → exige uma
  MT; um autômato de pilha não basta.
- Toda computação **para** (cada passo de casamento aumenta o número de marcas),
  logo a máquina é um **decisor** de L.
- Uma MTND tem o **mesmo poder** de uma MT determinística (simulação por busca em
  largura na árvore de configurações, com custo possivelmente exponencial). O não
  determinismo aqui é só uma forma elegante de *adivinhar e verificar*.

## 6. Verificação (oráculo)
`maquina_ww.py` compara a máquina com a definição matemática de L (`na_linguagem`)
para **todas** as cadeias de {a,b}* até um comprimento dado. Resultado:
**0 divergências** até |w| = 10 (ver `testes/`).

## 7. Arquivo JFLAP (`maquina_ww.jff`)
Além do simulador em Python, a mesma máquina está disponível em **JFLAP**
(`maquina_ww.jff`), gerada por `gerar_jflap.py`. Como o JFLAP exige símbolos de
fita de **um caractere**, os rótulos de dois caracteres foram remapeados:

| Python | `Sa` | `Sb` | `C` | `_` (branco) |
|---|---|---|---|---|
| **JFLAP** | `X` | `Y` | `Z` | célula vazia |

(`a, b, A, B` são iguais nos dois.) O branco aparece como campo vazio nas
transições, conforme o padrão do JFLAP. A aceitação é **por estado final**
(`qAccept`), coerente com a aceitação por ramo: ao abrir no JFLAP e usar
*Input → Multiple Run* ou *Step*, a máquina explora os ramos não determinísticos.

Para regenerar o arquivo:
```bash
python gerar_jflap.py
```

## Executar
```bash
python maquina_ww.py
```
