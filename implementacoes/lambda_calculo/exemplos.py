"""
exemplos.py -- Demonstrações executáveis do avaliador de Cálculo Lambda.

Execute:   python exemplos.py

Mostra, por reescrita de termos (beta-redução em ordem normal):
  1. MULT 2 3  -> 6        (traço COMPLETO, 7 passos -- atende o mínimo de 7)
  2. PRED 3    -> 2        (predecessor via pares de Church)
  3. AND/OR/NOT/ISZERO sobre booleanos de Church
  4. FACT 0..4 -> 1,1,2,6,24   (fatorial via combinador Y; problema-alvo)
  5. Omega                 (termo SEM forma normal: ilustra a parada indecidível)
"""

from __future__ import annotations

import sys

from lambda_calc import parse, normalize
from prelude import expand, church_to_int

# Garante acentuação correta mesmo no console do Windows (cmd/PowerShell).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def avaliar(src: str, max_steps: int = 500_000):
    """parse -> expande apelidos do prelúdio -> normaliza por ordem normal.
    Retorna (termo_final, num_passos, normalizou?)."""
    return normalize(expand(parse(src)), max_steps=max_steps)


def _trunc(s: str, width: int) -> str:
    return s if len(s) <= width else s[: width - 1] + "…"


def mostrar_traco(titulo: str, src: str, *, max_steps: int = 500_000,
                  max_print: int = 0, width: int = 110):
    """Imprime o traço de redução. Se `max_print` > 0 e o traço for maior,
    mostra os primeiros e os últimos passos. Linhas longas são truncadas em
    `width` colunas só para exibição."""
    print(f"\n=== {titulo} ===")
    print(f"Expressão de entrada: {src}")
    trace: list[str] = []
    final, passos, ok = normalize(
        expand(parse(src)), max_steps=max_steps,
        on_step=lambda i, term: trace.append(str(term)),
    )
    trace.append(str(final))

    def show(idx: int, s: str):
        print(f"  [{idx:>2}] {_trunc(s, width)}")

    if max_print and len(trace) > max_print:
        half = max_print // 2
        for i in range(half):
            show(i, trace[i])
        print(f"        ... ({len(trace) - max_print} passos intermediários omitidos) ...")
        for i in range(len(trace) - half, len(trace)):
            show(i, trace[i])
    else:
        for i, s in enumerate(trace):
            show(i, s)

    print(f"Total de beta-reduções: {passos}   (normalizou = {ok})")
    n = church_to_int(final) if ok else None
    if n is not None:
        print(f"Resultado decodificado como numeral de Church: {n}")
    return passos, n


def main():
    print("#" * 72)
    print("# CÁLCULO LAMBDA — avaliador por beta-redução em ordem normal")
    print("# Equipe: Yuri Aguiar, João Rath, Pedro Paulo  |  CC5NA")
    print("#" * 72)

    # 1) Multiplicação 2 * 3 = 6  (traço completo e legível -- 7 reduções).
    mostrar_traco("MULT 2 3  (esperado: 6)", "MULT 2 3")

    # 2) Predecessor pred(3) = 2.
    mostrar_traco("PRED 3  (esperado: 2)", "PRED 3", max_print=12)

    # 3) Lógica booleana de Church.
    print("\n=== Booleanos de Church ===")
    for expr, esperado in [
        ("AND TRUE FALSE", "FALSE"),
        ("OR FALSE TRUE", "TRUE"),
        ("NOT FALSE", "TRUE"),
        ("ISZERO 0", "TRUE"),
        ("ISZERO 2", "FALSE"),
    ]:
        final, passos, ok = avaliar(expr)
        print(f"  {expr:<18} -> {str(final):<10}  (esperado {esperado}; {passos} reduções)")

    # 4) FATORIAL via Y -- problema-alvo. Tabela-resumo + traço (resumido).
    print("\n" + "#" * 72)
    print("# PROBLEMA-ALVO: FATORIAL  n!  via combinador de ponto fixo Y")
    print("# FACT = Y (\\f n. IF (ISZERO n) 1 (MULT n (f (PRED n))))")
    print("#" * 72)
    for n in range(0, 5):
        final, passos, ok = avaliar(f"FACT {n}")
        val = church_to_int(final) if ok else None
        marca = "OK" if val == _fat(n) else "ERRO"
        print(f"  FACT {n}  ->  {val:<3}  [{marca}]   "
              f"({passos} beta-reduções, normalizou={ok})")

    # Evidência de que o FACT realmente reescreve termos (traço resumido).
    mostrar_traco("FACT 3  (esperado: 6) — traço resumido", "FACT 3",
                  max_print=10, width=90)

    # 5) Omega: termo SEM forma normal (diverge). A parada é indecidível.
    print("\n=== Omega = (\\x. x x) (\\x. x x)  —  NÃO possui forma normal ===")
    final, passos, ok = avaliar(r"(\x. x x) (\x. x x)", max_steps=50)
    print(f"  Após {passos} passos: normalizou={ok}  (esperado False — diverge).")
    print("  A divergência ilustra a indecidibilidade do problema da parada:")
    print("  nenhum avaliador pode, em geral, decidir se um termo tem forma normal.")


def _fat(n: int) -> int:
    r = 1
    for k in range(2, n + 1):
        r *= k
    return r


if __name__ == "__main__":
    main()
