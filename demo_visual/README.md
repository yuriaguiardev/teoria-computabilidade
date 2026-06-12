# Visualizador de execução (auxílio de apresentação)

> **Isto NÃO é a implementação dos modelos.** É apenas uma "vitrine" web que
> **chama o código formal já existente** em [`../implementacoes/`](../implementacoes/)
> e mostra os resultados de forma visual para a defesa do seminário.
>
> A lógica do λ-cálculo e da MTND continua 100% nos módulos originais
> (`lambda_calc.py`, `prelude.py`, `ntm.py`, `maquina_ww.py`). Aqui só
> apresentamos as saídas — nada é recalculado de outra forma.

## Como rodar

```bash
python app.py
```

Depois abra no navegador: **http://localhost:8000**

- **Sem instalação:** usa apenas a biblioteca padrão do Python (sem `pip install`).
- **Funciona offline:** nenhum CSS/JS vem de internet (tudo embutido). Ideal para
  demonstração ao vivo, mesmo sem rede.

## O que dá para mostrar

**Aba λ-Cálculo** — digite (ou clique num exemplo) e veja o **traço de β-reduções**
passo a passo, com controles ◀ ▶ ▶️ e o resultado decodificado como número:
- `MULT 2 3` → 6 (7 passos, ótimo para narrar célula a célula)
- `AND TRUE FALSE`, `ISZERO 0`, `PRED 3`
- `FACT 3` → 6 (1525 reduções; o problema-alvo, via combinador Y)
- `(\x. x x) (\x. x x)` → diverge (sem forma normal — a parada indecidível)

**Aba MT Não Determinística** — digite uma palavra e veja o veredito
**ACEITA/REJEITA**, a **fita animada** do ramo aceitante (cabeçote destacado),
a **árvore de computação** e a conferência contra a definição matemática (oráculo):
- `aa`, `abab`, `aabaab` → ACEITA
- `abba` (palíndromo ≠ ww), `aba` (ímpar), `abc` (símbolo inválido) → REJEITA

## Observação para a correção

Esta pasta foi adicionada como **apoio visual ao seminário**. Os pontos de
implementação, formalização e testes referem-se ao código em `../implementacoes/`
e `../testes/`, que é autossuficiente e roda sem este visualizador.
