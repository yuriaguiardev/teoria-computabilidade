"""
gerar_jflap.py -- Gera o arquivo JFLAP (.jff) da MTND de L = { ww }.

O JFLAP exige símbolos de fita de UM caractere. A máquina em `maquina_ww.py` usa
rótulos de dois caracteres (Sa, Sb) por clareza; aqui eles são remapeados:

    Python :  a  b  A  B  Sa  Sb  C   _(branco)
    JFLAP  :  a  b  A  B  X   Y   Z   (branco vazio)

Significado em JFLAP:
    X = início (adivinhado) da 2ª metade, valor 'a'   (era Sa)
    Y = início (adivinhado) da 2ª metade, valor 'b'   (era Sb)
    Z = célula da 2ª metade já consumida              (era C)

O branco é representado por elemento vazio (<read/> / <write/>), padrão do JFLAP.

Uso:
    python gerar_jflap.py        # escreve maquina_ww.jff
"""

from __future__ import annotations

import os
from xml.sax.saxutils import escape

from maquina_ww import build_machine

# Remapeamento de símbolos Python -> JFLAP (1 caractere). None = branco (vazio).
REMAP = {"a": "a", "b": "b", "A": "A", "B": "B",
         "Sa": "X", "Sb": "Y", "C": "Z", "_": None}

# Posições (x, y) de cada estado no diagrama do JFLAP.
LAYOUT = {
    "q0":           (90, 90),
    "qScan":        (250, 90),
    "qFindLeft":    (430, 90),
    "qScanRight":   (610, 90),
    "qToBoundaryA": (760, 200),
    "qToBoundaryB": (760, 330),
    "qSeekSecondA": (590, 330),
    "qSeekSecondB": (430, 330),
    "qCheckSecond": (250, 330),
    "qAccept":      (90, 330),
}


def _sym(s: str) -> str:
    """Converte um símbolo Python no conteúdo do campo <read>/<write> do JFLAP."""
    mapped = REMAP[s]
    return "" if mapped is None else escape(mapped)


def gerar_jff() -> str:
    M = build_machine()
    # ids estáveis para os estados (ordem do LAYOUT)
    ids = {name: i for i, name in enumerate(LAYOUT)}

    linhas = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        "<!--Gerado por gerar_jflap.py para a AV2 (CC5NA) — MTND de L = { ww }.-->",
        "<structure>",
        "\t<type>turing</type>",
        "\t<automaton>",
        "\t\t<!--Lista de estados.-->",
    ]
    for name, (x, y) in LAYOUT.items():
        linhas.append(f'\t\t<state id="{ids[name]}" name="{escape(name)}">')
        linhas.append(f"\t\t\t<x>{float(x)}</x>")
        linhas.append(f"\t\t\t<y>{float(y)}</y>")
        if name == M.q0:
            linhas.append("\t\t\t<initial/>")
        if name in M.F:
            linhas.append("\t\t\t<final/>")
        linhas.append("\t\t</state>")

    linhas.append("\t\t<!--Lista de transições.-->")
    n_trans = 0
    for (estado, simbolo), moves in M.delta.items():
        for (novo, escreve, mov) in moves:
            linhas.append("\t\t<transition>")
            linhas.append(f"\t\t\t<from>{ids[estado]}</from>")
            linhas.append(f"\t\t\t<to>{ids[novo]}</to>")
            linhas.append(f"\t\t\t<read>{_sym(simbolo)}</read>")
            linhas.append(f"\t\t\t<write>{_sym(escreve)}</write>")
            linhas.append(f"\t\t\t<move>{mov}</move>")
            linhas.append("\t\t</transition>")
            n_trans += 1

    linhas.append("\t</automaton>")
    linhas.append("</structure>")
    return "\n".join(linhas) + "\n", len(ids), n_trans


def main():
    xml, n_estados, n_trans = gerar_jff()
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maquina_ww.jff")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Arquivo JFLAP gerado: {destino}")
    print(f"  estados: {n_estados}   transições: {n_trans}")


if __name__ == "__main__":
    main()
