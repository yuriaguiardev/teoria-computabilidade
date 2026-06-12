# Rastreamento de execução — MT Não Determinística

Modelo: **Máquina de Turing Não Determinística** (Opção 4).
Problema: reconhecer **L = { ww : w ∈ {a,b}+ }** (palavras duplicadas).

Reprodução:
```bash
cd implementacoes/mt_nao_deterministica
python maquina_ww.py
```
Saída bruta salva em [`saida_execucao.txt`](saida_execucao.txt).
Testes automatizados (inclui oráculo de força bruta até |w| ≤ 10):
`python -m unittest discover -s testes`.

Parâmetros formais: **|Q| = 10** (estados), **37 transições** em δ,
Γ = {a, b, A, B, Sa, Sb, C, _}, Σ = {a, b}, F = {qAccept}.

---

## Tabela de testes (entrada → esperado → obtido)

| # | Entrada | Pertence a L? (oráculo) | Veredito da MTND | Configs exploradas | Status |
|---|---------|:-----------------------:|:----------------:|------------------:|:------:|
| 1 | `aa`     | sim | **ACEITA**  | 13 | ✅ |
| 2 | `abab`   | sim | **ACEITA**  | 40 | ✅ |
| 3 | `aabaab` | sim | **ACEITA**  | 97 | ✅ |
| 4 | `ab`     | não | rejeita | 7  | ✅ |
| 5 | `abba`   | não (é palíndromo, não `ww`) | rejeita | 32 | ✅ |
| 6 | `aba`    | não (ímpar) | rejeita | 21 | ✅ |
| 7 | `abc`    | não (`c ∉ Σ`) | rejeita | 0 | ✅ |
| 8 | `a`      | não (ímpar) | rejeita | 2 | ✅ |
| 9 | `` (vazia) | não (`w` deve ser não-vazia) | rejeita | 1 | ✅ |

> Casos **aceitos** (1–3), **rejeitados por conteúdo** (4, 5), **de fronteira**
> (6 ímpar, 8 unitário, 9 vazia) e **inválido** (7, símbolo fora de Σ).
> **Verificação exaustiva:** o oráculo comparou a MTND com a definição de L para
> **TODAS** as 1023 cadeias de {a,b}* até comprimento 9 (e 2046 até comprimento 10
> no teste) — **0 divergências**.

---

## Ramo aceitante (caminho de configurações) — entrada `abab`

`[x]` marca a posição do cabeçote; `_` é o branco.

```
passo  0: q0: [a] b a b
passo  1: qScan: a [b] a b
passo  2: qScan: a b [a] b
passo  3: qFindLeft: a [b] Sa b
passo  4: qFindLeft: [a] b Sa b
passo  5: qFindLeft: [_] a b Sa b
passo  6: qScanRight: [a] b Sa b
passo  7: qToBoundaryA: A [b] Sa b
passo  8: qToBoundaryA: A b [Sa] b
passo  9: qFindLeft: A [b] C b
passo 10: qFindLeft: [A] b C b
passo 11: qFindLeft: [_] A b C b
passo 12: qScanRight: [A] b C b
passo 13: qScanRight: A [b] C b
passo 14: qToBoundaryB: A B [C] b
passo 15: qSeekSecondB: A B C [b]
passo 16: qFindLeft: A B [C] C
passo 17: qFindLeft: A [B] C C
passo 18: qFindLeft: [A] B C C
passo 19: qFindLeft: [_] A B C C
passo 20: qScanRight: [A] B C C
passo 21: qScanRight: A [B] C C
passo 22: qScanRight: A B [C] C
passo 23: qCheckSecond: A B C [C]
passo 24: qCheckSecond: A B C C [_]
passo 25: qAccept: A B C C [_]      <-- ramo aceitante
```

## Árvore de computação — entrada `ab` (REJEITA: todos os ramos morrem)
```
q0: [a] b
   └─ qScan: a [b]
      ├─ qScan: a b [_] ✗ (sem transições)          <- ramo "não tagueou": morre
      └─ qFindLeft: [a] Sb                            <- ramo "tagueou meio em b"
         └─ qFindLeft: [_] a Sb
            └─ qScanRight: [a] Sb
               └─ qToBoundaryA: A [Sb] ✗ (sem transições)   <- a ≠ b: morre
```

## Análise técnica
- **O que é computado:** a máquina decide a linguagem L = {ww}. O **não
  determinismo** está em `qScan`, onde a máquina ADIVINHA o ponto médio (dois
  ramos por símbolo: "continua na 1ª metade" ou "começa a 2ª metade aqui").
- **Como a computação evolui:** escolhido um palpite, a verificação é
  determinística — casa, na mesma ordem, o símbolo mais à esquerda não casado da
  1ª metade com o mais à esquerda não consumido da 2ª metade, marcando ambos
  (`a→A`, tag `Sa`/`Sb`, consumido `C`). Aceita **sse algum ramo** esgota as duas
  metades juntas (`qCheckSecond` lê o branco em `qAccept`).
- **Por que não é trivial:** L **não é livre de contexto** (lema do bombeamento
  para LLCs), logo um autômato de pilha não a reconhece — é preciso o poder da MT.
  São 10 estados e 37 transições, com alfabeto de fita estendido por marcadores.
- **Limitações observadas:** todo ramo PARA (cada iteração aumenta o número de
  marcas), então a máquina é um **decisor** para L. O simulador ainda usa limite
  de passos e conjunto de visitados para o caso geral de MTs que podem não parar.
