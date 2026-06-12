"""
prelude.py -- Biblioteca de definições em Cálculo Lambda PURO.

Tudo aqui é "açúcar": cada nome (PLUS, MULT, Y, FACT, numerais ...) é apenas um
APELIDO para um termo lambda puro. A função `expand` troca esses apelidos pelos
respectivos termos, de modo que a redução em lambda_calc.py opere somente com a
regra beta sobre variáveis, abstrações e aplicações -- sem "trapacear" usando
aritmética do Python.

Codificações usadas:
  - Numerais de Church:   n  =  \\f x. f (f ... (f x))   (n aplicações de f)
  - Booleanos de Church:  TRUE = \\x y. x   /   FALSE = \\x y. y
  - Pares:                PAIR x y = \\f. f x y
  - Recursão:             via combinador de ponto fixo Y (lambda puro não tem
                          recursão nativa; Y a "fabrica").
"""

from __future__ import annotations

from typing import Optional

from lambda_calc import Term, Var, Abs, App, parse, free_vars, substitute


# ----------------------------------------------------------------------------
# Numerais de Church
# ----------------------------------------------------------------------------
def church_numeral(n: int) -> Term:
    """Constrói o numeral de Church de n:  \\f x. f^n x."""
    if n < 0:
        raise ValueError("Numerais de Church não representam negativos.")
    body: Term = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)
    return Abs("f", Abs("x", body))


def church_to_int(t: Term) -> Optional[int]:
    """Decodifica um numeral de Church em forma normal de volta para um int.
    Retorna None se o termo não tiver a forma de um numeral. Funciona a menos de
    alpha-renomeação (os nomes ligados podem ter sido trocados pela redução)."""
    if not (isinstance(t, Abs) and isinstance(t.body, Abs)):
        return None
    f_name = t.param
    x_name = t.body.param
    body = t.body.body
    n = 0
    while True:
        if isinstance(body, Var) and body.name == x_name:
            return n
        if isinstance(body, App) and isinstance(body.func, Var) and body.func.name == f_name:
            n += 1
            body = body.arg
            continue
        return None  # não é um numeral de Church


# ----------------------------------------------------------------------------
# Definições nomeadas (em texto). Podem referenciar umas às outras.
# ----------------------------------------------------------------------------
_RAW: dict[str, str] = {
    # Combinadores básicos
    "I":     r"\x. x",
    "K":     r"\x y. x",
    "S":     r"\x y z. x z (y z)",

    # Booleanos e condicional
    "TRUE":  r"\x y. x",
    "FALSE": r"\x y. y",
    "IF":    r"\b t e. b t e",
    "AND":   r"\p q. p q FALSE",
    "OR":    r"\p q. p TRUE q",
    "NOT":   r"\p. p FALSE TRUE",

    # Numerais e aritmética
    "ZERO":  r"\f x. x",
    "SUCC":  r"\n f x. f (n f x)",
    "PLUS":  r"\m n f x. m f (n f x)",
    "MULT":  r"\m n f. m (n f)",
    "ISZERO": r"\n. n (\x. FALSE) TRUE",

    # Pares (usados para construir o predecessor)
    "PAIR":  r"\x y f. f x y",
    "FST":   r"\p. p TRUE",
    "SND":   r"\p. p FALSE",
    # PRED: itera o "shift" (a,b) -> (b, b+1) n vezes sobre (0,0); FST do
    # resultado é n-1. Para n=0 devolve 0 (predecessor truncado em zero).
    "SHIFT": r"\p. PAIR (SND p) (SUCC (SND p))",
    "PRED":  r"\n. FST (n SHIFT (PAIR ZERO ZERO))",

    # Recursão: combinador de ponto fixo de Curry.
    "Y":     r"\f. (\x. f (x x)) (\x. f (x x))",

    # FATORIAL via Y (o problema-alvo da implementação).
    # FACT = Y (\f n. IF (ISZERO n) 1 (MULT n (f (PRED n))))
    "FACT":  r"Y (\f n. IF (ISZERO n) ONE (MULT n (f (PRED n))))",
    "ONE":   r"\f x. f x",
}


def _is_number(name: str) -> bool:
    return name.isdigit()


# Resolução com memoização: cada apelido vira um termo lambda 100% puro
# (sem nenhum nome definido sobrando como variável livre).
_resolved: dict[str, Term] = {}


def _resolve(name: str, stack: tuple[str, ...] = ()) -> Term:
    if _is_number(name):
        return church_numeral(int(name))
    if name in _resolved:
        return _resolved[name]
    if name in stack:
        raise ValueError(f"Ciclo de definições detectado em {name!r}.")
    if name not in _RAW:
        raise KeyError(f"Nome não definido no prelúdio: {name!r}")
    term = parse(_RAW[name])
    term = _expand(term, stack + (name,))
    _resolved[name] = term
    return term


def _expand(term: Term, stack: tuple[str, ...]) -> Term:
    """Substitui toda variável LIVRE que seja um apelido definido (ou numeral)
    pelo termo puro correspondente, repetindo até não sobrar nenhum."""
    while True:
        defined = {
            v for v in free_vars(term)
            if _is_number(v) or v in _RAW
        }
        if not defined:
            return term
        for v in defined:
            term = substitute(term, v, _resolve(v, stack))


def expand(term: Term) -> Term:
    """Expande um termo do usuário, trocando apelidos do prelúdio e numerais
    por lambda puro. O resultado contém SOMENTE Var/Abs/App 'cruas'."""
    return _expand(term, ())


# Dicionário público com todas as definições já resolvidas (termos puros).
def all_definitions() -> dict[str, Term]:
    return {name: _resolve(name) for name in _RAW}
