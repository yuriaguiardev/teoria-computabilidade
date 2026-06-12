# λ-Cálculo — formalização e implementação

**Modelo:** Opção 7 (λ-Cálculo). **Problema:** computar o **fatorial** `n!`
puramente em λ-cálculo não tipado, usando **numerais de Church** e recursão pelo
**combinador de ponto fixo Y**.

## 1. Definição formal (sintaxe)
Um **termo** λ é definido indutivamente:

```
M, N ::= x            (variável)
       | (λx. M)      (abstração — função anônima de parâmetro x e corpo M)
       | (M N)        (aplicação — aplica a função M ao argumento N)
```

- **Variáveis livres** `FV`: `FV(x)={x}`, `FV(λx.M)=FV(M)\{x}`, `FV(M N)=FV(M)∪FV(N)`.
- **Variável ligada:** o `x` em `λx. M` liga as ocorrências de `x` em `M`.
- **α-equivalência:** termos iguais a menos do nome das variáveis ligadas
  (`λx.x ≡ λy.y`).

## 2. Regra de computação (única): β-redução
```
(λx. M) N   →β   M[x := N]
```
A **substituição `M[x := N]`** troca as ocorrências **livres** de `x` por `N`,
**evitando captura**: ao entrar em `λy. P` com `y ∈ FV(N)`, renomeia-se `y`
(α-conversão) para um nome fresco. Sem isso, uma variável livre de `N` seria
capturada e o significado mudaria.

## 3. Estratégia de avaliação: ordem normal
Reduzimos sempre o redex **mais à esquerda e mais externo** (*leftmost-outermost*).
Pelo **Teorema da Padronização**, essa estratégia é **normalizante**: se o termo
tem forma normal, ela é encontrada. Forma normal = termo sem nenhum redex.

## 4. Codificações (em `prelude.py`)
| Conceito | Definição λ |
|---|---|
| Numeral de Church `n` | `λf x. f (f … (f x))` (n vezes) |
| `TRUE` / `FALSE` | `λx y. x` / `λx y. y` |
| `IF b t e` | `b t e` |
| `SUCC` | `λn f x. f (n f x)` |
| `PLUS` | `λm n f x. m f (n f x)` |
| `MULT` | `λm n f. m (n f)` |
| `ISZERO` | `λn. n (λx. FALSE) TRUE` |
| `PRED` | `λn. FST (n (λp. PAIR (SND p) (SUCC (SND p))) (PAIR 0 0))` |
| `Y` (ponto fixo) | `λf. (λx. f (x x)) (λx. f (x x))` |
| `FACT` | `Y (λf n. IF (ISZERO n) 1 (MULT n (f (PRED n))))` |

## 5. Critério de parada
A forma normal é a "resposta". Como nem todo termo tem forma normal (ex.:
`Ω = (λx. x x)(λx. x x)`), o avaliador usa um **limite de passos** — refletindo a
**indecidibilidade do problema da parada**.

## 6. Arquivos
- `lambda_calc.py` — AST (`Var`/`Abs`/`App`), tokenizer+parser, `free_vars`,
  `substitute` (captura evitada), `normalize` (β em ordem normal + traço),
  `alpha_equal`.
- `prelude.py` — definições de Church/combinadores; `expand` troca apelidos por
  λ puro; `church_numeral`/`church_to_int` codificam/decodificam inteiros.
- `exemplos.py` — demonstrações (`MULT`, `PRED`, booleanos, `FACT 0..4`, `Ω`).

## 7. Decisões de modelagem (para a arguição)
- **Por que numerais de Church?** Permitem representar números como funções puras,
  sem qualquer tipo nativo — fiel ao λ-cálculo.
- **Por que Y?** O λ-cálculo puro não tem recursão; `Y g` satisfaz `Y g = g (Y g)`,
  "amarrando o nó" para o fatorial se referenciar.
- **Por que ordem normal (e não aplicativa)?** Ordem normal não avalia argumentos
  desnecessários (call-by-name), o que faz o `IF` e o `Y` terminarem; ordem
  aplicativa entraria em laço ao expandir `Y` ansiosamente.
- **Por que limite de passos?** É impossível decidir em geral se um termo
  normaliza (parada indecidível).

## Executar
```bash
python exemplos.py
```
