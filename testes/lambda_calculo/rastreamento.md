# Rastreamento de execução — Cálculo Lambda

Modelo: **λ-Cálculo** (Opção 7). Problema-alvo: **calcular o fatorial via combinador Y**.

Reprodução:
```bash
cd implementacoes/lambda_calculo
python exemplos.py
```
A saída bruta desta execução está salva em [`saida_execucao.txt`](saida_execucao.txt).
Testes automatizados: `python -m unittest discover -s testes`.

---

## Tabela de testes (entrada → esperado → obtido)

| # | Entrada (λ-expressão) | Esperado | Obtido (forma normal) | β-reduções | Status |
|---|------------------------|----------|------------------------|-----------:|:------:|
| 1 | `MULT 2 3`   | numeral 6  | numeral 6  | 7     | ✅ |
| 2 | `PRED 3`     | numeral 2  | numeral 2  | 36    | ✅ |
| 3 | `AND TRUE FALSE` | `FALSE` (`\x y. y`) | `(\x y. y)` | 4 | ✅ |
| 4 | `OR FALSE TRUE`  | `TRUE`  (`\x y. x`) | `(\x y. x)` | 4 | ✅ |
| 5 | `NOT FALSE`      | `TRUE`  | `(\x y. x)` | 3 | ✅ |
| 6 | `ISZERO 0`       | `TRUE`  | `(\x y. x)` | 3 | ✅ |
| 7 | `ISZERO 2`       | `FALSE` | `(\x y. y)` | 4 | ✅ |
| 8 | `FACT 0`         | numeral 1  | 1  | 12     | ✅ |
| 9 | `FACT 1`         | numeral 1  | 1  | 45     | ✅ |
| 10| `FACT 2`         | numeral 2  | 2  | 248    | ✅ |
| 11| `FACT 3`         | numeral 6  | 6  | 1525   | ✅ |
| 12| `FACT 4`         | numeral 24 | 24 | 10384  | ✅ |
| 13| `(\x. x x)(\x. x x)` (Ω) | **diverge** | não normaliza (limite atingido) | 100+ | ✅ (esperado) |

> Os casos 1–7 são *aceitos/produzidos corretamente*; o caso 13 é o caso de
> **fronteira**: um termo SEM forma normal, que ilustra a indecidibilidade da
> parada (nenhum avaliador pode decidir, em geral, se a redução termina).

---

## Traço completo — `MULT 2 3 → 6` (7 β-reduções, leftmost-outermost)

```
[ 0] (((\m n f. (m (n f))) (\f x. (f (f x)))) (\f x. (f (f (f x)))))
[ 1] ((\n f. ((\f x. (f (f x))) (n f))) (\f x. (f (f (f x)))))
[ 2] (\f. ((\f x. (f (f x))) ((\f x. (f (f (f x)))) f)))
[ 3] (\f x. (((\f x. (f (f (f x)))) f) (((\f x. (f (f (f x)))) f) x)))
[ 4] (\f x. ((\x. (f (f (f x)))) (((\f x. (f (f (f x)))) f) x)))
[ 5] (\f x. (f (f (f (((\f x. (f (f (f x)))) f) x)))))
[ 6] (\f x. (f (f (f ((\x. (f (f (f x)))) x)))))
[ 7] (\f x. (f (f (f (f (f (f x)))))))      <-- numeral de Church 6
```

## Traço (resumido) — `PRED 3 → 2` (36 β-reduções)
Primeiros e últimos passos (completo em `saida_execucao.txt`):
```
[ 0] ((\n. ((\p. (p (\x y. x))) ((n (\p. ...)) ...))) (\f x. (f (f (f x)))))
 ...
[34] (\f x. (f (f (((\f x. x) f) x))))
[35] (\f x. (f (f ((\x. x) x))))
[36] (\f x. (f (f x)))                       <-- numeral de Church 2
```

## Análise técnica
- **O que é computado:** funções aritméticas e lógicas representadas como termos
  λ puros (numerais e booleanos de Church). O resultado é sempre outro termo λ,
  decodificado para inteiro contando as aplicações de `f` no numeral.
- **Como a computação evolui:** apenas por **β-redução em ordem normal**. Não há
  estado mutável nem laços nativos — a recursão do fatorial é "fabricada" pelo
  **combinador Y**, que satisfaz `Y g = g (Y g)` e é re-expandido sob demanda.
- **Por que não é trivial:** `FACT 4` exige **10 384** β-reduções e usa Y,
  numerais de Church, `PRED` por pares e o condicional de Church — bem além de
  uma simples substituição. A substituição é **com captura evitada** (α-renomeação),
  validada pelo teste `test_captura_evitada`.
- **Limitações observadas:** termos sem forma normal (Ω) divergem; por isso o
  avaliador usa um **limite de passos**. Isso reflete a indecidibilidade da parada.
