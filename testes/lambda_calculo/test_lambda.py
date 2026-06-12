"""
Testes automatizados do avaliador de Cálculo Lambda (unittest, stdlib).

Execute da raiz do repositório:
    python -m unittest discover -s testes
ou diretamente:
    python testes/lambda_calculo/test_lambda.py
"""

import os
import sys
import unittest

# Torna importáveis os módulos da implementação.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "implementacoes", "lambda_calculo"))

from lambda_calc import (  # noqa: E402
    Var, Abs, App, parse, normalize, free_vars, substitute, alpha_equal,
)
from prelude import expand, church_numeral, church_to_int  # noqa: E402


def avaliar(src, max_steps=500_000):
    return normalize(expand(parse(src)), max_steps=max_steps)


def valor(src, max_steps=500_000):
    """Avalia e decodifica o numeral de Church resultante (ou None)."""
    final, _, ok = avaliar(src, max_steps)
    return church_to_int(final) if ok else None


def fatorial(n):
    r = 1
    for k in range(2, n + 1):
        r *= k
    return r


class TestParserEPrettyPrint(unittest.TestCase):
    def test_roundtrip_identidade(self):
        t = parse(r"\x. x")
        self.assertIsInstance(t, Abs)
        self.assertEqual(t.param, "x")
        self.assertIsInstance(t.body, Var)

    def test_aplicacao_assoc_esquerda(self):
        # a b c  ==  ((a b) c)
        t = parse("a b c")
        self.assertEqual(t, App(App(Var("a"), Var("b")), Var("c")))

    def test_lambda_multiparam(self):
        # \x y. x  ==  \x. (\y. x)
        self.assertTrue(alpha_equal(parse(r"\x y. x"), parse(r"\x. \y. x")))

    def test_lambda_sintaxe_unicode(self):
        self.assertTrue(alpha_equal(parse(r"λx. x"), parse(r"\x. x")))


class TestVariaveisLivresESubstituicao(unittest.TestCase):
    def test_free_vars(self):
        self.assertEqual(free_vars(parse(r"\x. x y")), {"y"})
        self.assertEqual(free_vars(parse(r"x (\y. y)")), {"x"})

    def test_substituicao_simples(self):
        # (x y)[x := \z. z]  ==  (\z. z) y
        r = substitute(parse("x y"), "x", parse(r"\z. z"))
        self.assertTrue(alpha_equal(r, parse(r"(\z. z) y")))

    def test_substituicao_nao_atinge_ligada(self):
        # (\x. x)[x := y] permanece \x. x (x está ligada)
        r = substitute(parse(r"\x. x"), "x", Var("y"))
        self.assertTrue(alpha_equal(r, parse(r"\x. x")))

    def test_captura_evitada(self):
        # (\y. x)[x := y]  NÃO pode capturar o y livre:
        # resultado deve ser alfa-equiv a \z. y  (y permanece LIVRE).
        r = substitute(parse(r"\y. x"), "x", Var("y"))
        self.assertIsInstance(r, Abs)
        self.assertNotEqual(r.param, "y")          # parâmetro renomeado
        self.assertIn("y", free_vars(r))           # y continua livre
        self.assertTrue(alpha_equal(r, parse(r"\w. y")))


class TestNumeraisChurch(unittest.TestCase):
    def test_encode_decode(self):
        for n in range(0, 8):
            self.assertEqual(church_to_int(church_numeral(n)), n)

    def test_literais_numericos(self):
        for n in range(0, 6):
            self.assertEqual(valor(str(n)), n)

    def test_nao_numeral_retorna_none(self):
        self.assertIsNone(church_to_int(parse(r"\x y. x")))  # é um booleano


class TestAritmetica(unittest.TestCase):
    def test_succ(self):
        self.assertEqual(valor("SUCC 4"), 5)

    def test_plus(self):
        self.assertEqual(valor("PLUS 2 3"), 5)
        self.assertEqual(valor("PLUS 0 0"), 0)

    def test_mult(self):
        self.assertEqual(valor("MULT 2 3"), 6)
        self.assertEqual(valor("MULT 3 0"), 0)

    def test_pred(self):
        self.assertEqual(valor("PRED 3"), 2)
        self.assertEqual(valor("PRED 0"), 0)  # predecessor truncado em zero


class TestBooleanos(unittest.TestCase):
    def _eh_true(self, src):
        return alpha_equal(avaliar(src)[0], parse(r"\x y. x"))

    def _eh_false(self, src):
        return alpha_equal(avaliar(src)[0], parse(r"\x y. y"))

    def test_and(self):
        self.assertTrue(self._eh_true("AND TRUE TRUE"))
        self.assertTrue(self._eh_false("AND TRUE FALSE"))
        self.assertTrue(self._eh_false("AND FALSE TRUE"))

    def test_or(self):
        self.assertTrue(self._eh_true("OR FALSE TRUE"))
        self.assertTrue(self._eh_false("OR FALSE FALSE"))

    def test_not(self):
        self.assertTrue(self._eh_true("NOT FALSE"))
        self.assertTrue(self._eh_false("NOT TRUE"))

    def test_iszero(self):
        self.assertTrue(self._eh_true("ISZERO 0"))
        self.assertTrue(self._eh_false("ISZERO 1"))
        self.assertTrue(self._eh_false("ISZERO 5"))


class TestFatorialViaY(unittest.TestCase):
    def test_fatorial(self):
        for n in range(0, 6):
            self.assertEqual(valor(f"FACT {n}"), fatorial(n),
                             msg=f"FACT {n} deveria ser {fatorial(n)}")

    def test_fatorial_gera_muitos_passos(self):
        # Requisito AV2: >= 7 etapas de redução. FACT 3 faz centenas.
        _, passos, ok = avaliar("FACT 3")
        self.assertTrue(ok)
        self.assertGreaterEqual(passos, 7)


class TestDivergencia(unittest.TestCase):
    def test_omega_nao_normaliza(self):
        # Omega = (\x. x x)(\x. x x) não tem forma normal: deve estourar o limite.
        _, passos, ok = avaliar(r"(\x. x x) (\x. x x)", max_steps=100)
        self.assertFalse(ok)
        self.assertEqual(passos, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
