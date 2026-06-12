# Roteiro da apresentação — AV2 Teoria da Computabilidade

**Equipe:** Yuri Aguiar · João Rath · Pedro Paulo — **Turma CC5NA**
**Modelos:** (7) λ-Cálculo → fatorial via combinador Y · (4) MT Não Determinística → reconhecer `L = { ww : w ∈ {a,b}+ }`
**Tempo total:** 12–15 min · **Meta:** ~3 min teoria, ~6 min demonstração, ~3 min análise, ~3 min arguição.

> Este documento descreve **o miolo da apresentação (10 slides)**, focado em
> *funcionamento, cálculo e decisões de modelagem*. Os slides de **capa** e
> **conclusão** estão descritos à parte, no final.
> Para cada slide há: **objetivo**, **conteúdo (o que vai na tela)**, **fala**
> (quem diz e o quê) e, quando útil, **imagem (prompt de geração)**.
> Convenção das imagens: diagramas conceituais → prompt de IA/desenho; telas de
> execução → **captura de tela real do terminal** (mais confiável e auditável).

---

## Divisão de falas (resumo)

| Bloco | Slides | Responsável | Tempo |
|---|---|---|---|
| Teoria + cálculo λ | 1–3 | **Yuri** | ~3 min |
| Demonstração λ | 4–5 | **João** | ~3 min |
| Teoria + funcionamento MTND | 6–8 | **Yuri / Pedro** | ~3 min |
| Demonstração MTND | 9 | **Pedro** | ~3 min |
| Análise e limites | 10 | **Yuri** | ~2 min |
| Arguição | — | **todos** | ~3 min |

---

# PARTE I — λ-Cálculo (Opção 7)

## Slide 1 — λ-Cálculo: sintaxe e a única regra de cálculo
**Objetivo:** estabelecer o que é um termo e como ele "computa".

**Conteúdo (tela):**
- Termo (definição indutiva): `M ::= x | (λx. M) | (M N)` — variável · abstração · aplicação.
- Variáveis **livres × ligadas**; **α-equivalência** (`λx.x ≡ λy.y`).
- **Única regra — β-redução:** `(λx. M) N → M[x := N]`.
- **Substituição com captura evitada:** ao entrar em `λy.P` com `y ∈ FV(N)`, renomeia-se `y` (α-conversão) para um nome fresco.

**Fala (Yuri):** "No λ-cálculo *tudo* é função. Só existe uma operação: aplicar
uma função a um argumento e substituir — a β-redução. O único cuidado técnico é
não 'capturar' uma variável livre do argumento; por isso implementamos a
substituição com α-renomeação. Isso é literalmente o coração do nosso avaliador
em `lambda_calc.py`."

**Imagem (prompt):** *"Diagrama limpo, fundo branco, estilo livro-texto, de uma
árvore de sintaxe abstrata do termo `(λx. x) y`: nó raiz 'App (aplicação)' com
dois filhos — à esquerda 'Abs λx' apontando para folha 'x', à direita folha 'y'.
Rótulos em português (Aplicação, Abstração, Variável). Sem cores berrantes,
traços finos."*

---

## Slide 2 — Codificações de Church e estratégia de avaliação
**Objetivo:** mostrar que números e lógica são *só funções puras*, e por que usamos ordem normal.

**Conteúdo (tela):**
- **Numeral de Church:** `n = λf x. f (f … (f x))` (aplica `f` n vezes).
- **Booleanos:** `TRUE = λx y. x`, `FALSE = λx y. y`, `IF b t e = b t e`.
- **Aritmética:** `MULT = λm n f. m (n f)`; `ISZERO`, `PRED` (via pares).
- **Ordem normal** (leftmost-outermost): pelo **Teorema da Padronização**, acha a forma normal **se ela existir**.

**Fala (Yuri):** "Não usamos o `int` do Python — seria 'trapaça'. O número 3 é a
função que aplica algo 3 vezes. `MULT`, `IF`, `ISZERO` são todos termos λ puros
no `prelude.py`. E reduzimos sempre o redex mais à esquerda e externo (ordem
normal), porque é a estratégia que garante chegar ao resultado quando ele existe
— e, crucial, é o que faz o `IF` e o `Y` terminarem."

**Imagem (prompt):** *"Infográfico simples mostrando o numeral de Church 3 como
três camadas de aplicação de uma função f sobre x: `f(f(f(x)))`, com setas
indicando 'aplica 3 vezes'. Minimalista, fundo branco, fonte monoespaçada."*

---

## Slide 3 — Recursão sem recursão: o combinador Y e o problema (FACT)
**Objetivo:** explicar como o cálculo puro (sem `def`/loop) consegue recursão, e apresentar o problema-alvo.

**Conteúdo (tela):**
- O λ-cálculo puro **não tem recursão nativa**.
- **Combinador de ponto fixo Y:** `Y = λf. (λx. f (x x)) (λx. f (x x))`, com a propriedade `Y g = g (Y g)`.
- **Problema-alvo:**
  `FACT = Y (λf n. IF (ISZERO n) 1 (MULT n (f (PRED n))))`
- `Y` "amarra o nó": entrega a `f` uma cópia dela mesma para a chamada `f (PRED n)`.

**Fala (Yuri):** "Como uma função anônima chama a si mesma? Com o combinador Y.
`Y g` é um ponto fixo: satisfaz `Y g = g (Y g)`, então a função do fatorial
recebe a si própria como argumento e pode descer em `n-1`. É assim que `FACT`
existe sem nenhuma palavra-chave de recursão."

**Imagem (prompt):** *"Diagrama do combinador Y como um laço de auto-referência:
uma caixa 'g (passo do fatorial)' com uma seta circular voltando para si mesma
rotulada 'Y g = g (Y g)'. Estilo esquemático, fundo branco, uma cor de destaque."*

---

## Slide 4 — Demonstração ao vivo: `MULT 2 3 → 6` (traço completo)
**Objetivo:** provar que a resposta vem de **reescrita de termos**, passo a passo (≥7 etapas exigidas).

**Conteúdo (tela):**
- Comando: `python implementacoes/lambda_calculo/exemplos.py`
- Traço (início → fim), **7 β-reduções**:
  ```
  [0] ((λm n f. m (n f)) <2> <3>)        (2 e 3 expandidos em numerais de Church)
  ...
  [7] (λf x. f (f (f (f (f (f x))))))    = numeral 6
  ```
- Resultado decodificado: **6**.

**Fala (João):** "Aqui está a execução real. Cada linha é um termo *antes* de uma
β-redução. Em 7 passos `MULT 2 3` chega ao numeral de Church do 6 — seis
aplicações de `f`. Nosso `church_to_int` só lê essa forma e devolve 6. Nenhuma
aritmética de Python no meio."

**Imagem:** **captura de tela real** do terminal rodando `exemplos.py` na seção
`MULT 2 3`. *(Se quiser um cartão estático: prompt — "screenshot estilizado de
um terminal escuro mostrando um traço de redução lambda numerado de [0] a [7],
fonte monoespaçada, destaque na última linha".)*

---

## Slide 5 — Custo real e os limites: FACT e a parada indecidível
**Objetivo:** mostrar recursão genuína com custo crescente e conectar à indecidibilidade.

**Conteúdo (tela):**
- Fatorial via Y (valores e **custo em β-reduções**, medidos):

  | Entrada | Resultado | β-reduções |
  |---|---|---|
  | `FACT 2` | 2 | 248 |
  | `FACT 3` | 6 | 1525 |
  | `FACT 4` | 24 | 10 384 |

- **Ω = (λx. x x)(λx. x x) → Ω → Ω → …** nunca para → usamos **limite de passos**.
- Reflete a **indecidibilidade do problema da parada**.

**Fala (João):** "O fatorial não é truque: o custo explode — 4! exige 10 384
reduções. E mostramos o outro lado: o termo Ω se reduz a si mesmo para sempre.
Como *nenhum* avaliador pode decidir em geral se um termo normaliza (parada
indecidível), colocamos um limite de passos. Os testes `test_omega_nao_normaliza`
e `test_captura_evitada` cobrem esses casos."

**Imagem (prompt):** *"Gráfico de barras simples, fundo branco, comparando o
número de β-reduções de FACT 2 (248), FACT 3 (1525) e FACT 4 (10384), eixo Y em
escala log, destacando o crescimento. Rótulos em português."*

---

# PARTE II — MT Não Determinística (Opção 4)

## Slide 6 — MTND: formalismo, relação δ e aceitação por ramo
**Objetivo:** definir a MTND e o que muda em relação à MT determinística.

**Conteúdo (tela):**
- **7-upla** `M = (Q, Σ, Γ, δ, q0, b, F)`.
- δ é uma **relação**: `δ : (Q × Γ) → P(Q × Γ × {L, R, S})`.
- Um mesmo `(estado, símbolo)` → **vários destinos** ⇒ a computação é uma **árvore**, não um caminho.
- **Aceitação por existência de ramo aceitante**; **rejeição = todos os ramos morrem** (sem estado de rejeição dedicado).

**Fala (Yuri/Pedro):** "Na MT não determinística, a transição vira relação: para
o mesmo estado e símbolo pode haver mais de uma jogada. A execução vira uma
*árvore* de configurações. Aceitamos se **algum** galho chega ao estado de
aceitação; rejeitamos quando **todos** os galhos morrem por falta de transição."

**Imagem (prompt):** *"Diagrama de uma árvore de computação não determinística:
um nó raiz que se ramifica em 2 filhos, um deles novamente em 2; folhas marcadas
com '✓ aceita', '✗ morto'. Fundo branco, setas finas, rótulos em português
(configuração, ramo aceitante, ramo morto)."*

---

## Slide 7 — Problema `L = {ww}` e a ideia: adivinhar o ponto médio
**Objetivo:** apresentar o problema e a estratégia de fita (como a máquina realmente funciona).

**Conteúdo (tela):**
- **L = { ww : w ∈ {a,b}+ }** — palavra concatenada consigo mesma (`aa`, `abab`, `aabaab`). **Não é palíndromo.**
- **Γ = { a, b, A, B, Sa, Sb, C, _ }** — marcadores:
  - `A`/`B`: célula da **1ª metade** já casada; `Sa`/`Sb`: início (adivinhado) da 2ª metade; `C`: célula da 2ª metade já consumida.
- **Não determinismo:** em `qScan`, a máquina **adivinha onde termina a 1ª metade**.
- **Verificação determinística:** casa 1ª e 2ª metades **posição a posição, na mesma ordem**.

**Fala (Pedro):** "O problema é reconhecer palavras 'duplicadas'. A sacada é o não
determinismo: a máquina *chuta* onde está o meio — cada chute vira um galho.
Depois, deterministicamente, ela casa a primeira metade com a segunda, símbolo a
símbolo e na mesma ordem (não é palíndromo!). Os marcadores na fita registram o
que já foi casado."

**Imagem (prompt):** *"Ilustração de uma fita de máquina de Turing com as células
da palavra `abab`, mostrando a 1ª metade `ab` marcada como `A B` e a 2ª metade
sendo consumida em `C C`, com uma seta tracejada indicando 'ponto médio
adivinhado' entre as metades. Fundo branco, estilo didático."*

---

## Slide 8 — Tabela de transições e o ponto de não determinismo
**Objetivo:** evidenciar a complexidade (10 estados, 37 transições) e onde nasce a ramificação.

**Conteúdo (tela):**
- **|Q| = 10 (> 8)** · **37 transições (≥ 10)** — atende a Seção 7 do enunciado.
- Único ponto de **não determinismo** = estado `qScan` (dois destinos no mesmo par):
  ```
  δ(qScan, a) = { (qScan, a, R) ,  (qFindLeft, Sa, L) }
                  └ seguir na 1ª metade   └ "aqui começa a 2ª metade"
  ```
- Pares `(estado, símbolo)` **ausentes** ⇒ ramo morre.
- *(Mostrar 4–5 linhas da tabela δ do README como amostra, não a tabela inteira.)*

**Fala (Pedro):** "Aqui está a única fonte de ramificação: em `qScan`, ao ler um
símbolo, a máquina pode continuar na primeira metade **ou** declarar 'o meio é
aqui'. Os outros estados são determinísticos — fazem a verificação. São 10 estados
e 37 transições, acima do mínimo exigido."

**Imagem:** **captura** da tabela δ no [README do modelo](../implementacoes/mt_nao_deterministica/README.md) (recortar as linhas de `q0`, `qScan`, `qScanRight`).

---

## Slide 9 — Demonstração ao vivo: árvore, ramo aceitante e oráculo
**Objetivo:** mostrar aceitação, rejeição e a prova de correção.

**Conteúdo (tela):**
- Comando: `python implementacoes/mt_nao_deterministica/maquina_ww.py`
- **`ab` → rejeita** (todos os ramos morrem):
  ```
  q0: [a] b
   └─ qScan: a [b]
      ├─ qScan: a b [_]      ✗ (não tagueou → morre)
      └─ qFindLeft: [a] Sb
         └─ … qToBoundaryA: A [Sb] ✗ (a ≠ b → morre)
  ```
- **`abab` → ACEITA**: exibir o **ramo aceitante** (caminho `q0 … qAccept`).
- **Oráculo:** comparado com a definição matemática de L para **todas as 2047 cadeias** de `{a,b}*` com `|w| ≤ 10` → **0 divergências**.

**Fala (Pedro):** "Para `ab`, mostramos a árvore inteira: os dois galhos morrem,
então rejeita. Para `abab`, imprimimos o caminho que chega em `qAccept`. E para
não depender de exemplos escolhidos a dedo, um **oráculo** compara a máquina com
a definição de L em todas as 2047 cadeias até tamanho 10 — zero divergências. Isso
está no teste `test_oraculo`, entre os 32 testes."

**Imagem:** **captura de tela real** do terminal: árvore de `ab` + ramo aceitante
de `abab` + linha final do oráculo ("0 divergências").

---

## Slide 10 — Análise: computabilidade, equivalência e limites
**Objetivo:** amarrar os dois modelos à teoria (Church-Turing, hierarquia, indecidibilidade).

**Conteúdo (tela):**
- **Hipótese de Church-Turing:** λ-cálculo ≡ MT ≡ funções recursivas (Kleene, 1936). Tudo "efetivamente computável" cai numa dessas formulações.
- **Não determinismo é conveniência, não poder extra:** toda MTND é simulável por MT determinística (custo possivelmente exponencial).
- **Hierarquia de Chomsky:** `{ww}` **não é livre de contexto** (lema do bombeamento) ⇒ um autômato de pilha não basta; exige uma MT.
- **Limites:** parada **indecidível** — Ω no λ-cálculo; ramos não-parantes no caso geral de MTs ⇒ ambos os simuladores usam **limite de passos**.

**Fala (Yuri):** "Os dois modelos são faces do mesmo poder de computar: é a
Hipótese de Church-Turing. O não determinismo da nossa MT não adiciona poder — é
elegância para 'adivinhar e verificar'. E `{ww}` é exatamente um exemplo que
separa as linguagens livres de contexto das que precisam de uma MT. O limite
comum dos dois é a indecidibilidade da parada — por isso ambos têm um teto de
passos."

**Imagem (prompt):** *"Diagrama de dois painéis: (esquerda) três caixas
interligadas por '≡' — 'λ-cálculo', 'Máquina de Turing', 'Funções recursivas',
título 'Church-Turing'; (direita) círculos concêntricos da hierarquia de Chomsky
(Regular ⊂ Livre de Contexto ⊂ Sensível ao Contexto ⊂ Recursivamente Enumerável)
com `{ww}` apontado fora de 'Livre de Contexto'. Fundo branco, didático."*

---

# Slides de CAPA e CONCLUSÃO (descritos à parte)

## Slide de CAPA (abertura — não conta nos 10)
**Objetivo:** identificar o trabalho em poucos segundos (Seção 11 do enunciado).

**Conteúdo (tela):**
- Título: **AV2 — Teoria da Computabilidade · λ-Cálculo e MT Não Determinística**.
- **Turma CC5NA** — Prof. Daniel Leal Souza · Semestre 01/2026.
- **Equipe:** Yuri Aguiar · João Rath · Pedro Paulo.
- Modelos escolhidos: **Opção 7 (λ-Cálculo)** e **Opção 4 (MTND)**, com o problema de cada um (fatorial via Y; reconhecer `L = {ww}`).
- Link do repositório: `github.com/yuriaguiardev/teoria-computabilidade`.

**Fala (Yuri, ~20s):** "Boa noite. Somos a equipe Yuri, João e Pedro, da CC5NA.
Escolhemos dois modelos: o λ-cálculo, para *computar* o fatorial, e a Máquina de
Turing não determinística, para *decidir* a linguagem das palavras duplicadas.
São tarefas e formalismos diferentes, como o enunciado pede."

**Imagem (prompt opcional):** *"Capa acadêmica sóbria: à esquerda um símbolo λ
estilizado, à direita o diagrama mínimo de uma fita de máquina de Turing com
cabeçote; fundo branco/cinza-claro, tipografia limpa, espaço para título e
nomes."*

---

## Slide de CONCLUSÃO (fechamento — não conta nos 10)
**Objetivo:** consolidar o que foi mostrado, reforçar a autoria/engenharia e abrir para perguntas.

**Conteúdo (tela):**
- **O que mostramos:** um avaliador λ funcional (reescrita real de termos, fatorial via Y) e uma MTND que decide `{ww}` (árvore, ramo aceitante, oráculo).
- **Reprodutibilidade:** Python 3.10+, **só biblioteca padrão**; **32 testes** (`python -m unittest discover -s testes`); rastreamentos e saídas brutas no repositório.
- **Domínio:** formalismo **explícito** (parser + β-redução; δ como relação + árvore) — nada de "função pronta" devolvendo a resposta.
- **Encerramento:** "Perguntas?" + link do repositório e referências (Sipser 2013; Pierce 2002; Barendregt 1984; Diverio & Menezes 2011; Church 1936; Turing 1936).

**Fala (todos, ~30s):** "Para fechar: entregamos os dois modelos com implementação
própria, testes e rastreamento — tudo reproduzível e auditável no GitHub. Cada
parte do código representa explicitamente o formalismo estudado. Estamos à
disposição para perguntas."

**Imagem:** não precisa; manter limpo. (Se quiser: QR code do repositório.)

---

## Checklist rápido antes de apresentar
- [ ] Testar o `.jff` no JFLAP da sala **com a opção *Allow Stay In Transitions* habilitada** (transição `qCheckSecond → qAccept` usa `S`). Plano B: rodar `maquina_ww.py`.
- [ ] Rodar `exemplos.py` e `maquina_ww.py` uma vez antes, para as **capturas de tela** ficarem prontas (evita falha técnica ao vivo).
- [ ] Conferir que todos os números batem: `MULT 2 3` = 7 β-reduções; `FACT 4` = 10 384; `|Q|` = 10; 37 transições; oráculo = 2047 cadeias, 0 divergências; 32 testes.
- [ ] Cada integrante deve saber explicar **qualquer** slide (a nota pode ser individualizada na arguição).
