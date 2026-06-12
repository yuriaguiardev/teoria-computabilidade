# AV2 — Teoria da Computabilidade
## Máquinas Universais, Turing e λ-Cálculo

> **Repositório da equipe.** 
> **`https://github.com/yuriaguiardev/teoria-computabilidade`**

---

### Identificação
| | |
|---|---|
| **Disciplina** | Teoria da Computabilidade — Prof. Daniel Leal Souza |
| **Turma** | **CC5NA** |
| **Semestre** | 01/2026 |
| **Equipe (3 integrantes)** | **Yuri Aguiar**, **João Rath**, **Pedro Paulo** |

### Modelos escolhidos (exatamente 2, distintos)
| Opção | Modelo | Problema resolvido (diferentes entre si) |
|:----:|--------|------------------------------------------|
| **7** | **λ-Cálculo** (avaliador funcional) | **Computar o fatorial** `n!` puramente em λ-cálculo, com recursão via combinador **Y** e numerais de Church. |
| **4** | **Máquina de Turing Não Determinística** | **Reconhecer** a linguagem **L = { ww : w ∈ {a,b}+ }** (palavras duplicadas), adivinhando o ponto médio. |

Os dois problemas são **distintos no formalismo e na tarefa computacional**: um
*computa uma função numérica* por reescrita de termos; o outro *decide uma
linguagem* por busca em uma árvore de configurações.

---

## Como executar

### Dependências
- **Python 3.10 ou superior** (testado em 3.11). **Nenhuma biblioteca externa** —
  somente a biblioteca padrão. Não há `pip install`.
- Para exibir acentuação corretamente no terminal Windows, os scripts já
  reconfiguram a saída para UTF-8.

### Rodar as demonstrações
```bash
# 1) Cálculo Lambda — traços de redução, booleanos e fatorial via Y
python implementacoes/lambda_calculo/exemplos.py

# 2) MT Não Determinística — aceita/rejeita, árvore de computação e oráculo
python implementacoes/mt_nao_deterministica/maquina_ww.py
```

### Rodar os testes (32 testes, incluindo oráculo de força bruta)
```bash
python -m unittest discover -s testes
```

---

## Exemplos de uso (entrada → saída)

**λ-Cálculo** (avaliando expressões com o prelúdio de Church):
```text
MULT 2 3        ->  numeral de Church 6      (7 β-reduções)
FACT 4          ->  numeral de Church 24     (10384 β-reduções)
AND TRUE FALSE  ->  (\x y. y)  (= FALSE)
(\x.x x)(\x.x x)->  diverge (sem forma normal; ilustra a parada indecidível)
```

**MT Não Determinística** (reconhecendo L = {ww}):
```text
aa, abab, aabaab   ->  ACEITA
ab, abba, aba, abc ->  rejeita
```
A máquina imprime também a **árvore de computação** e o **ramo aceitante**.

---

## Estrutura do repositório
```
README.md                      Este arquivo (identificação, instruções, exemplos)
uso_ia.md                      Declaração de uso de IA (Seção 8 do enunciado)
referencias.md                 Referências consultadas
relatorio_rastreamento.md      Relatório curto de rastreamento (ambos os modelos)
slides/
  apresentacao.md              Slides do seminário (Markdown/Marp -> PDF/PPTX)
implementacoes/
  lambda_calculo/
    lambda_calc.py             Núcleo: AST, parser, substituição, β-redução
    prelude.py                 Numerais/booleanos de Church, combinadores, Y, FACT
    exemplos.py                Demonstrações executáveis
    README.md                  Formalização do λ-cálculo + decisões de modelagem
  mt_nao_deterministica/
    ntm.py                     Formalismo e simulador genérico da MTND (árvore)
    maquina_ww.py              Máquina de L={ww} + oráculo de verificação
    README.md                  Formalização da MTND + tabela de transições
testes/
  lambda_calculo/
    test_lambda.py             Testes (parser, substituição, aritmética, Y, Ω)
    rastreamento.md            Tabela de testes + traços
    saida_execucao.txt         Saída bruta da execução
  mt_nao_deterministica/
    test_ntm.py                Testes + oráculo de força bruta (|w| ≤ 10)
    rastreamento.md            Tabela de testes + árvore/caminho
    saida_execucao.txt         Saída bruta da execução
```

---

## Relação com computabilidade (resumo)
- **λ-Cálculo** é **Turing-completo** (Kleene): tudo o que uma MT computa, o
  λ-cálculo também computa, e vice-versa — uma das formulações da **Hipótese de
  Church-Turing**. A recursão, que o cálculo puro não tem, é obtida pelo
  **combinador de ponto fixo Y**.
- A **MT Não Determinística** reconhece exatamente as mesmas linguagens que a MT
  determinística (toda MTND é simulável por uma MT determinística, com custo
  exponencial no pior caso). O **não determinismo** é uma *conveniência de
  modelagem* (adivinhar-e-verificar), não um ganho de poder computacional.
- L = {ww} **não é livre de contexto**, o que motiva o uso de uma MT (um autômato
  de pilha não basta) — conectando o trabalho à hierarquia de Chomsky e aos
  limites dos modelos mais fracos.

Detalhes formais em [`implementacoes/lambda_calculo/README.md`](implementacoes/lambda_calculo/README.md)
e [`implementacoes/mt_nao_deterministica/README.md`](implementacoes/mt_nao_deterministica/README.md).

## Uso de IA e referências
Veja [`uso_ia.md`](uso_ia.md) e [`referencias.md`](referencias.md).

