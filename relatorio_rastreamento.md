# Relatório curto de rastreamento de execução — AV2

**Disciplina:** Teoria da Computabilidade · **Turma:** CC5NA
**Equipe:** Yuri Aguiar, João Rath, Pedro Paulo
**Modelos:** (7) λ-Cálculo · (4) Máquina de Turing Não Determinística

Este relatório resume as entradas de teste, as saídas esperadas e as saídas
obtidas de cada implementação. Os rastreamentos completos (traços passo a passo,
árvores de computação e saída bruta das execuções) estão em:

- `testes/lambda_calculo/rastreamento.md` + `saida_execucao.txt`
- `testes/mt_nao_deterministica/rastreamento.md` + `saida_execucao.txt`

Tudo é reproduzível com:
```bash
python -m unittest discover -s testes        # 32 testes, todos passam
python implementacoes/lambda_calculo/exemplos.py
python implementacoes/mt_nao_deterministica/maquina_ww.py
```

---

## 1) λ-Cálculo — problema: fatorial via combinador Y

A computação ocorre **por β-redução em ordem normal** sobre termos λ puros
(numerais e booleanos de Church). O resultado é decodificado para inteiro.

| Entrada | Esperado | Obtido | β-reduções | Tipo de caso |
|---------|----------|--------|-----------:|--------------|
| `MULT 2 3` | 6 | 6 | 7 | produzido corretamente |
| `PRED 3` | 2 | 2 | 36 | produzido corretamente |
| `AND TRUE FALSE` | FALSE | `\x y. y` | 4 | produzido corretamente |
| `FACT 3` | 6 | 6 | 1525 | produzido corretamente |
| `FACT 4` | 24 | 24 | 10384 | produzido corretamente |
| `(\x.x x)(\x.x x)` (Ω) | diverge | não normaliza | limite | **fronteira** (sem forma normal) |

**Interpretação:** o avaliador reproduz aritmética e lógica usando só a regra β.
O fatorial mostra recursão genuína (via Y) e custo real (10 384 reduções para 4!).
O caso Ω evidencia a indecidibilidade da parada — daí o limite de passos.

---

## 2) MT Não Determinística — problema: L = { ww : w ∈ {a,b}+ }

Não determinismo = **adivinhar o ponto médio**; verificação determinística casa
as duas metades na mesma ordem. Aceita **sse existe ramo aceitante**.

| Entrada | Pertence a L? | Veredito | Configs | Tipo de caso |
|---------|:-------------:|:--------:|--------:|--------------|
| `aa` | sim | ACEITA | 13 | aceito |
| `abab` | sim | ACEITA | 40 | aceito |
| `aabaab` | sim | ACEITA | 97 | aceito |
| `abba` | não | rejeita | 32 | rejeitado (palíndromo ≠ ww) |
| `aba` | não | rejeita | 21 | **fronteira** (comprimento ímpar) |
| `abc` | não | rejeita | 0 | inválido (`c ∉ Σ`) |
| `` (vazia) | não | rejeita | 1 | **fronteira** (w não-vazia) |

**Verificação exaustiva (oráculo):** a MTND foi comparada com a definição
matemática de L para **todas** as cadeias de {a,b}* até comprimento **10**
(2047 cadeias) — **0 divergências**. Logo `L(M) = L` exatamente, nesse universo.

**Interpretação:** a máquina decide L = {ww}, que **não é livre de contexto**;
todo ramo para (decisor). O número de configurações exploradas cresce com o
tamanho da entrada por causa da árvore de palpites (não determinismo).

---

## 3) Conformidade com os requisitos de complexidade
- MTND: **10 estados (> 8)** e **37 transições (≥ 10)** — `test_mais_de_8_estados`,
  `test_pelo_menos_10_transicoes`.
- λ-Cálculo: **avaliador/interpretador funcional** com exemplos documentados;
  `FACT 3` sozinho faz 1525 β-reduções (≫ 7 etapas exigidas).
