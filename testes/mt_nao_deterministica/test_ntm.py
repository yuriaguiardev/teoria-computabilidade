"""
Testes automatizados da MTND para L = { ww : w ∈ {a,b}+ } (unittest, stdlib).

Inclui um ORÁCULO de força bruta: compara a máquina com a definição matemática
de L para TODAS as cadeias de {a,b}* até comprimento 10.

Execute da raiz do repositório:
    python -m unittest discover -s testes
"""

import os
import sys
import unittest
from itertools import product

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "implementacoes", "mt_nao_deterministica"))

from ntm import NTM  # noqa: E402
from maquina_ww import build_machine, na_linguagem  # noqa: E402


class TestFormalismo(unittest.TestCase):
    def setUp(self):
        self.M = build_machine()

    def test_mais_de_8_estados(self):
        self.assertGreater(len(self.M.Q), 8, "AV2 exige > 8 estados")

    def test_pelo_menos_10_transicoes(self):
        self.assertGreaterEqual(self.M.num_transitions(), 10,
                                "AV2 recomenda >= 10 transições")

    def test_consistencia_do_formalismo(self):
        # Σ ⊆ Γ, branco em Γ e fora de Σ, inicial em Q, F ⊆ Q.
        self.assertTrue(self.M.Sigma <= self.M.Gamma)
        self.assertIn(self.M.blank, self.M.Gamma)
        self.assertNotIn(self.M.blank, self.M.Sigma)
        self.assertIn(self.M.q0, self.M.Q)
        self.assertTrue(self.M.F <= self.M.Q)


class TestCasosDestacados(unittest.TestCase):
    def setUp(self):
        self.M = build_machine()

    def aceita(self, s):
        self.assertTrue(self.M.run(s).accepted, f"{s!r} deveria ser ACEITA")

    def rejeita(self, s):
        self.assertFalse(self.M.run(s).accepted, f"{s!r} deveria ser REJEITADA")

    def test_aceitos(self):
        for s in ["aa", "bb", "abab", "aabaab", "ababab"[:4], "babbab"]:
            self.aceita(s)

    def test_rejeitados_metades_diferentes(self):
        for s in ["ab", "ba", "abba", "baab"]:  # palíndromos NÃO são ww
            self.rejeita(s)

    def test_rejeitados_impares(self):
        for s in ["a", "aba", "ababa"]:
            self.rejeita(s)

    def test_rejeitados_vazio_e_invalidos(self):
        self.rejeita("")            # w deve ser não-vazia
        self.rejeita("abc")         # 'c' ∉ Σ
        self.rejeita("aax")

    def test_caminho_aceitante_existe(self):
        r = self.M.run("abab")
        self.assertTrue(r.accepted)
        self.assertIsNotNone(r.accepting_path)
        # o caminho começa no estado inicial e termina em aceitação
        self.assertEqual(r.accepting_path[0].state, "q0")
        self.assertIn(r.accepting_path[-1].state, self.M.F)

    def test_arvore_de_computacao_renderiza(self):
        node = self.M.computation_tree("aa", max_depth=20)
        texto = self.M.render_tree(node)
        self.assertIn("ACEITA", texto)


class TestOraculoForcaBruta(unittest.TestCase):
    """Garante L(M) == L exatamente, para todo |w| <= 10."""

    def test_oraculo(self):
        M = build_machine()
        divergencias = []
        total = 0
        for n in range(0, 11):
            for tup in product("ab", repeat=n):
                s = "".join(tup)
                total += 1
                if M.run(s).accepted != na_linguagem(s):
                    divergencias.append(s)
        self.assertEqual(divergencias, [],
                         f"{len(divergencias)} divergências em {total} cadeias")


if __name__ == "__main__":
    unittest.main(verbosity=2)
