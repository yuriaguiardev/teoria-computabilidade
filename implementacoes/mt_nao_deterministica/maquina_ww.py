"""
maquina_ww.py -- MTND que reconhece  L = { ww : w ∈ {a,b}+ }.

PROBLEMA: aceitar exatamente as cadeias que são a CONCATENAÇÃO DE UMA PALAVRA
CONSIGO MESMA (palavras "duplicadas"): aa, abab, aabaab, ...  e rejeitar tudo o
mais (ímpares, metades diferentes, símbolos inválidos, vazia).

POR QUE UMA MTND (e por que não determinismo é natural aqui):
  - L NÃO é livre de contexto (prova-se pelo lema do bombeamento para LLCs);
    logo um autômato de pilha não a reconhece -- precisamos do poder da MT.
  - A máquina ADIVINHA, de forma não determinística, ONDE termina a 1ª metade
    (o "ponto médio"). Para cada palpite nasce um ramo. Em seguida ela VERIFICA,
    deterministicamente, se as duas metades coincidem POSIÇÃO A POSIÇÃO (mesma
    ordem -- não é palíndromo!). Aceita-se sse ALGUM ramo confirmar o palpite.

ESTRATÉGIA DE FITA (alfabeto Γ):
    a, b      símbolos ainda não processados
    A, B      célula da 1ª metade já casada (era a / era b)
    Sa, Sb    "tag": início da 2ª metade, adivinhado (guarda o valor a / b)
    C         célula da 2ª metade já consumida
    _         branco

A cada iteração: marca-se o símbolo mais à esquerda ainda não casado da 1ª metade
e procura-se o símbolo mais à esquerda ainda não consumido da 2ª metade; se forem
iguais, ambos são marcados; senão o ramo morre. Aceita quando as duas metades se
esgotam JUNTAS (mesmo comprimento + mesmo conteúdo).

Estados (10): q0, qScan, qFindLeft, qScanRight, qToBoundaryA, qToBoundaryB,
qSeekSecondA, qSeekSecondB, qCheckSecond, qAccept (>8, conforme exigido).
Transições: contadas em tempo de execução (>> 10).
"""

from __future__ import annotations

import sys
from itertools import product

from ntm import NTM, LEFT, RIGHT, STAY

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def build_machine() -> NTM:
    A, B, Sa, Sb, C, blk = "A", "B", "Sa", "Sb", "C", "_"

    # δ : (estado, símbolo) -> lista de (novo_estado, escreve, move)
    delta = {
        # ---- q0: força a 1ª célula a pertencer à 1ª metade (w não-vazia) ----
        ("q0", "a"): [("qScan", "a", RIGHT)],
        ("q0", "b"): [("qScan", "b", RIGHT)],

        # ---- qScan: varre a 1ª metade e ADIVINHA o ponto médio -------------
        # (a) manter o símbolo na 1ª metade e seguir;  (b) tagueá-lo como
        #     início da 2ª metade (escolha NÃO DETERMINÍSTICA).
        ("qScan", "a"): [("qScan", "a", RIGHT), ("qFindLeft", Sa, LEFT)],
        ("qScan", "b"): [("qScan", "b", RIGHT), ("qFindLeft", Sb, LEFT)],
        # qScan lendo '_' (chegou ao fim sem taguear) -> ramo morre.

        # ---- qFindLeft: volta ao extremo esquerdo da fita ------------------
        ("qFindLeft", "a"): [("qFindLeft", "a", LEFT)],
        ("qFindLeft", "b"): [("qFindLeft", "b", LEFT)],
        ("qFindLeft", A):   [("qFindLeft", A, LEFT)],
        ("qFindLeft", B):   [("qFindLeft", B, LEFT)],
        ("qFindLeft", Sa):  [("qFindLeft", Sa, LEFT)],
        ("qFindLeft", Sb):  [("qFindLeft", Sb, LEFT)],
        ("qFindLeft", C):   [("qFindLeft", C, LEFT)],
        ("qFindLeft", blk): [("qScanRight", blk, RIGHT)],  # passou da pos.0; entra nela

        # ---- qScanRight: acha o símbolo mais à esquerda NÃO casado da 1ª ----
        ("qScanRight", A): [("qScanRight", A, RIGHT)],   # pula já casados
        ("qScanRight", B): [("qScanRight", B, RIGHT)],
        ("qScanRight", "a"): [("qToBoundaryA", A, RIGHT)],  # casa 'a', leva valor a
        ("qScanRight", "b"): [("qToBoundaryB", B, RIGHT)],
        ("qScanRight", C): [("qCheckSecond", C, RIGHT)],    # 1ª metade esgotada
        # qScanRight lendo Sa/Sb -> 1ª metade esgotada mas 2ª metade maior -> morre.

        # ---- qToBoundaryA: carrega 'a'; pula resto da 1ª metade ------------
        ("qToBoundaryA", "a"): [("qToBoundaryA", "a", RIGHT)],
        ("qToBoundaryA", "b"): [("qToBoundaryA", "b", RIGHT)],
        ("qToBoundaryA", A):   [("qToBoundaryA", A, RIGHT)],
        ("qToBoundaryA", B):   [("qToBoundaryA", B, RIGHT)],
        ("qToBoundaryA", Sa):  [("qFindLeft", C, LEFT)],   # tag valor a == a -> casa
        # ("qToBoundaryA", Sb) -> valor b != a -> morre
        ("qToBoundaryA", C):   [("qSeekSecondA", C, RIGHT)],  # tag já consumido

        # ---- qToBoundaryB: carrega 'b' -------------------------------------
        ("qToBoundaryB", "a"): [("qToBoundaryB", "a", RIGHT)],
        ("qToBoundaryB", "b"): [("qToBoundaryB", "b", RIGHT)],
        ("qToBoundaryB", A):   [("qToBoundaryB", A, RIGHT)],
        ("qToBoundaryB", B):   [("qToBoundaryB", B, RIGHT)],
        ("qToBoundaryB", Sb):  [("qFindLeft", C, LEFT)],
        # ("qToBoundaryB", Sa) -> morre
        ("qToBoundaryB", C):   [("qSeekSecondB", C, RIGHT)],

        # ---- qSeekSecondA: pula C's e casa o 1º símbolo livre da 2ª (=a) ----
        ("qSeekSecondA", C):   [("qSeekSecondA", C, RIGHT)],
        ("qSeekSecondA", "a"): [("qFindLeft", C, LEFT)],   # casa
        # ("qSeekSecondA", "b") -> morre (mismatch)
        # ("qSeekSecondA", "_") -> morre (2ª metade acabou, 1ª não)

        # ---- qSeekSecondB ---------------------------------------------------
        ("qSeekSecondB", C):   [("qSeekSecondB", C, RIGHT)],
        ("qSeekSecondB", "b"): [("qFindLeft", C, LEFT)],
        # ("qSeekSecondB", "a") -> morre

        # ---- qCheckSecond: 1ª metade ok; 2ª metade deve ser só C até o fim --
        ("qCheckSecond", C):   [("qCheckSecond", C, RIGHT)],
        ("qCheckSecond", blk): [("qAccept", blk, STAY)],   # tudo casado -> ACEITA
        # qCheckSecond lendo a/b/Sa/Sb -> 2ª metade tem célula sobrando -> morre.
    }

    states = {
        "q0", "qScan", "qFindLeft", "qScanRight", "qToBoundaryA", "qToBoundaryB",
        "qSeekSecondA", "qSeekSecondB", "qCheckSecond", "qAccept",
    }
    return NTM(
        states=states,
        input_alphabet={"a", "b"},
        tape_alphabet={"a", "b", A, B, Sa, Sb, C, blk},
        delta=delta,
        start="q0",
        blank=blk,
        accept={"qAccept"},
        name="MTND para L = { ww : w ∈ {a,b}+ }",
    )


# ----------------------------------------------------------------------------
# ORÁCULO: definição matemática independente, para validar a máquina.
# ----------------------------------------------------------------------------
def na_linguagem(s: str) -> bool:
    """True sse s = ww para algum w ∈ {a,b}+."""
    n = len(s)
    if n < 2 or n % 2 != 0:
        return False
    if any(c not in "ab" for c in s):
        return False
    return s[: n // 2] == s[n // 2:]


def verificar_oraculo(max_len: int = 9) -> tuple[int, list[str]]:
    """Compara a MTND com o oráculo para TODA cadeia de {a,b}* até `max_len`.
    Retorna (qtde_testada, lista_de_divergências)."""
    M = build_machine()
    divergencias: list[str] = []
    total = 0
    for n in range(0, max_len + 1):
        for tup in product("ab", repeat=n):
            s = "".join(tup)
            total += 1
            obtido = M.run(s).accepted
            esperado = na_linguagem(s)
            if obtido != esperado:
                divergencias.append(f"{s!r}: MTND={obtido}, oráculo={esperado}")
    return total, divergencias


def _demo():
    M = build_machine()
    print("#" * 72)
    print(f"# {M.name}")
    print("# Equipe: Yuri Aguiar, João Rath, Pedro Paulo  |  CC5NA")
    print("#" * 72)
    print(f"Estados (|Q| = {len(M.Q)}): {sorted(M.Q)}")
    print(f"Transições definidas em δ: {M.num_transitions()}")
    print(f"Γ = {sorted(M.Gamma)}   Σ = {sorted(M.Sigma)}   inicial = {M.q0}   F = {M.F}")

    casos = ["aa", "abab", "aabaab", "ab", "abba", "aba", "abc", "a", ""]
    print("\n--- Resultados (aceita/rejeita) ---")
    for s in casos:
        r = M.run(s)
        veredito = "ACEITA " if r.accepted else "rejeita"
        print(f"  {s!r:>10}  ->  {veredito}   "
              f"(configs exploradas={r.configs_explored}, prof.={r.max_depth})  "
              f"[oráculo: {'sim' if na_linguagem(s) else 'não'}]")

    print("\n--- Árvore de computação para 'aa' (ACEITA) ---")
    print(M.render_tree(M.computation_tree("aa", max_depth=20)))

    print("\n--- Árvore de computação para 'ab' (REJEITA: todos os ramos morrem) ---")
    print(M.render_tree(M.computation_tree("ab", max_depth=20)))

    print("\n--- Ramo aceitante (caminho) para 'abab' ---")
    r = M.run("abab")
    if r.accepting_path:
        for i, cfg in enumerate(r.accepting_path):
            print(f"  passo {i:>2}: {cfg.render(M.blank)}")

    print("\n--- Verificação contra o oráculo (todas as cadeias |w| <= 9) ---")
    total, div = verificar_oraculo(9)
    if not div:
        print(f"  OK: {total} cadeias testadas, 0 divergências. "
              f"A máquina reconhece EXATAMENTE L.")
    else:
        print(f"  FALHA: {len(div)} divergências em {total} cadeias:")
        for d in div[:20]:
            print("   ", d)


if __name__ == "__main__":
    _demo()
