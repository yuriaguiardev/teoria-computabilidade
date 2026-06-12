# Declaração de uso de Inteligência Artificial

**Disciplina:** Teoria da Computabilidade — AV2 · **Turma:** CC5NA
**Equipe:** Yuri Aguiar, João Rath, Pedro Paulo

> Esta declaração atende à Seção 8 do enunciado. O uso de IA foi **de apoio** e
> **não substituiu** o estudo, a implementação conceitual nem o domínio dos temas.

## 1. Ferramenta utilizada e data
- **Ferramenta:** Claude (Anthropic), via assistente de código.
- **Data aproximada de uso:** **junho de 2026** (semana da entrega da AV2).

## 2. Finalidade do uso
- Organização da estrutura do repositório conforme o enunciado.
- **Geração inicial (scaffolding)** do código dos dois modelos e da documentação.
- Apoio à **depuração** e à criação dos testes/oráculo de verificação.
- Revisão textual dos READMEs e dos slides.

## 3. Resumo dos prompts e dos trechos aproveitados
- *“Implementar um avaliador de λ-cálculo (parser, substituição com captura
  evitada, β-redução em ordem normal) e calcular o fatorial via combinador Y.”*
  → aproveitado em `implementacoes/lambda_calculo/` (núcleo + prelúdio + exemplos).
- *“Implementar uma MT não determinística genérica (δ como relação, árvore de
  computação, aceitação por ramo) e uma máquina que reconheça L = {ww}.”*
  → aproveitado em `implementacoes/mt_nao_deterministica/`.
- *“Criar testes unittest e um oráculo de força bruta para validar a linguagem.”*
  → aproveitado em `testes/`.

## 4. O que a equipe revisou, modificou, corrigiu ou rejeitou
- A equipe **executou** todas as demonstrações e os 32 testes, conferindo as
  saídas (em particular o **oráculo**, que prova `L(M) = {ww}` até |w| = 10).
- A equipe **conferiu manualmente** o ramo aceitante de `abab` passo a passo e a
  contagem de β-reduções de `MULT 2 3` (7 passos) contra a teoria.
- Decisões de modelagem foram **compreendidas e justificadas** pela equipe (ver
  Seção 5), e não simplesmente aceitas: escolha da **ordem normal** (para o Y
  terminar), do **PRED por pares**, e do esquema de **marcação/tag** da MTND.
- Nenhum trecho foi incorporado sem ser entendido; trechos pouco claros foram
  reescritos/comentados em português pela equipe.

## 5. Pontos que todos os integrantes sabem explicar (autoria)
**λ-Cálculo:** sintaxe (variável/abstração/aplicação); variáveis livres × ligadas;
α-equivalência; substituição **com captura evitada**; **β-redução** como única
regra; **ordem normal** e normalização; **numerais/booleanos de Church**;
**combinador Y** e por que o cálculo puro precisa dele para recursão; divergência
de Ω e a **parada indecidível**.

**MTND:** a 7-upla `(Q, Σ, Γ, δ, q0, b, F)` (rejeição por morte do ramo, sem
estado de rejeição dedicado); δ como **relação**; **árvore de
computação** e **aceitação por ramo**; por que `L = {ww}` **não é livre de
contexto**; o papel do **não determinismo** (adivinhar o ponto médio) e a
verificação determinística; equivalência **MTND ≡ MT determinística**.

## 6. Declaração final
**Declaramos que todos os integrantes da equipe revisaram, testaram e
compreendem integralmente os trechos de código, os formalismos e os resultados
incorporados a este trabalho, sendo capazes de explicá-los durante a arguição.**

Assinam: Yuri Aguiar ___________  ·  João Rath ___________  ·  Pedro Paulo ___________
