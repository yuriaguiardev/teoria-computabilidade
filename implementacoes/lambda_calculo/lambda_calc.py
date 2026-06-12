"""
lambda_calc.py -- Núcleo de um avaliador de Cálculo Lambda não tipado.

Este módulo IMPLEMENTA EXPLICITAMENTE o formalismo do lambda-cálculo (Opção 7 da
AV2). Nada aqui usa uma "função pronta" da linguagem para produzir a resposta: a
computação acontece por REESCRITA DE TERMOS, aplicando beta-reduções sobre uma
árvore de sintaxe abstrata (AST) que construímos à mão.

Componentes formais representados:
  - Sintaxe (gramática):   M ::= x | (\\x. M) | (M M)
        x       -> Var      (variável)
        \\x. M  -> Abs      (abstração / função anônima)
        M N     -> App      (aplicação)
  - Variáveis livres e ligadas .......... free_vars / bound binding em Abs
  - alfa-equivalência ................... resolvida via alpha-renomeação automática
  - Substituição com captura evitada .... substitute(...)
  - beta-redução (única regra de cálculo): (\\x. M) N  ->  M[x := N]
  - Estratégia de avaliação ............. ORDEM NORMAL (leftmost-outermost),
        que, pelo Teorema da Padronização, encontra a forma normal se ela existir.

Referências: Barendregt, "The Lambda Calculus"; Pierce, "TAPL", cap. 5.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Callable, Optional


# ----------------------------------------------------------------------------
# 1) ÁRVORE DE SINTAXE ABSTRATA (AST)
# ----------------------------------------------------------------------------
# Um termo lambda é UMA das três formas abaixo. Usamos dataclasses imutáveis
# (frozen) porque termos são valores matemáticos -- nunca mutamos um termo no
# lugar; sempre construímos um novo. Isso espelha a definição indutiva da sintaxe.

class Term:
    """Classe base abstrata de um termo lambda."""
    pass


@dataclass(frozen=True)
class Var(Term):
    """Variável, p.ex. x, y, f."""
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Abs(Term):
    """Abstração (\\param. corpo): a 'função anônima' do lambda-cálculo."""
    param: str
    body: Term

    def __str__(self) -> str:
        # Compacta lambdas aninhados: \x. \y. M  vira  \x y. M
        params = [self.param]
        body = self.body
        while isinstance(body, Abs):
            params.append(body.param)
            body = body.body
        return f"(\\{' '.join(params)}. {body})"


@dataclass(frozen=True)
class App(Term):
    """Aplicação (função argumento)."""
    func: Term
    arg: Term

    def __str__(self) -> str:
        return f"({self.func} {self.arg})"


# ----------------------------------------------------------------------------
# 2) VARIÁVEIS LIVRES
# ----------------------------------------------------------------------------
def free_vars(t: Term) -> set[str]:
    """Conjunto das variáveis LIVRES de um termo (definição indutiva clássica).

        FV(x)        = {x}
        FV(\\x. M)   = FV(M) \\ {x}      (x é LIGADA dentro de M)
        FV(M N)      = FV(M) ∪ FV(N)
    """
    if isinstance(t, Var):
        return {t.name}
    if isinstance(t, Abs):
        return free_vars(t.body) - {t.param}
    if isinstance(t, App):
        return free_vars(t.func) | free_vars(t.arg)
    raise TypeError(f"Termo desconhecido: {t!r}")


# Gerador de nomes frescos para a alpha-renomeação. O '#' garante que o nome
# nunca colide com identificadores escritos pelo usuário (que não usam '#').
_fresh_counter = count(0)


def _fresh_name(base: str) -> str:
    return f"{base}#{next(_fresh_counter)}"


# ----------------------------------------------------------------------------
# 3) SUBSTITUIÇÃO COM CAPTURA EVITADA  M[x := s]
# ----------------------------------------------------------------------------
def substitute(t: Term, x: str, s: Term) -> Term:
    """Substitui as ocorrências LIVRES de `x` em `t` pelo termo `s`.

    O ponto delicado é EVITAR CAPTURA: ao entrar em uma abstração \\y. M, se `y`
    for livre em `s`, renomeamos `y` (alpha-conversão) para um nome fresco antes
    de descer -- caso contrário uma variável livre de `s` seria "capturada" pelo
    ligador `y`, mudando o significado do termo.
    """
    if isinstance(t, Var):
        return s if t.name == x else t

    if isinstance(t, App):
        return App(substitute(t.func, x, s), substitute(t.arg, x, s))

    if isinstance(t, Abs):
        if t.param == x:
            # x está re-ligado aqui; não há ocorrência livre de x mais abaixo.
            return t
        if t.param not in free_vars(s):
            # Sem risco de captura: desce direto.
            return Abs(t.param, substitute(t.body, x, s))
        # Risco de captura -> alpha-renomeia o parâmetro para um nome fresco.
        fresh = _fresh_name(t.param)
        renamed_body = substitute(t.body, t.param, Var(fresh))
        return Abs(fresh, substitute(renamed_body, x, s))

    raise TypeError(f"Termo desconhecido: {t!r}")


# ----------------------------------------------------------------------------
# 4) BETA-REDUÇÃO EM ORDEM NORMAL (leftmost-outermost)
# ----------------------------------------------------------------------------
# Um redex é uma aplicação (\\x. M) N. A beta-regra contrai (\\x. M) N -> M[x:=N].
# "Ordem normal" sempre contrai o redex mais à ESQUERDA e mais EXTERNO primeiro;
# essa estratégia é normalizante: se o termo tem forma normal, ela é alcançada.

def _reduce_once(t: Term) -> Optional[Term]:
    """Aplica UMA beta-redução em ordem normal. Retorna None se já está em
    forma normal (nenhum redex restante)."""
    if isinstance(t, App):
        # 1) O próprio nó é o redex mais externo?  (\\x. M) N
        if isinstance(t.func, Abs):
            return substitute(t.func.body, t.func.param, t.arg)
        # 2) Senão, tenta reduzir à ESQUERDA (mais externo/esquerda) primeiro.
        reduced_func = _reduce_once(t.func)
        if reduced_func is not None:
            return App(reduced_func, t.arg)
        # 3) Só então o argumento.
        reduced_arg = _reduce_once(t.arg)
        if reduced_arg is not None:
            return App(t.func, reduced_arg)
        return None

    if isinstance(t, Abs):
        # Reduz dentro do corpo (necessário para chegar à forma normal completa).
        reduced_body = _reduce_once(t.body)
        if reduced_body is not None:
            return Abs(t.param, reduced_body)
        return None

    # Var: nunca é redex.
    return None


# Um passo de traço: o termo ANTES da redução (para imprimir a sequência).
TraceStep = str


def normalize(
    t: Term,
    max_steps: int = 100_000,
    on_step: Optional[Callable[[int, Term], None]] = None,
) -> tuple[Term, int, bool]:
    """Reduz `t` até a forma normal por ordem normal.

    Retorna (termo_final, num_passos, normalizou?).
      - normalizou? == True  -> alcançou forma normal dentro de max_steps.
      - normalizou? == False -> atingiu max_steps sem parar (termo possivelmente
        sem forma normal, p.ex. Omega). Isso ilustra a indecidibilidade da parada.

    `on_step(i, termo)` é chamado a cada passo com o termo ANTES da i-ésima
    redução, permitindo construir o rastreamento de execução.
    """
    current = t
    steps = 0
    while steps < max_steps:
        nxt = _reduce_once(current)
        if nxt is None:
            return current, steps, True  # forma normal alcançada
        if on_step is not None:
            on_step(steps, current)
        current = nxt
        steps += 1
    return current, steps, False  # limite atingido (não normalizou)


def reduction_trace(t: Term, max_steps: int = 100_000) -> list[TraceStep]:
    """Devolve a lista de termos visitados (como strings), do inicial ao final.
    Útil para mostrar os >= 7 passos de redução exigidos pela AV2."""
    trace: list[TraceStep] = []
    final, _, _ = normalize(
        t, max_steps=max_steps, on_step=lambda i, term: trace.append(str(term))
    )
    trace.append(str(final))
    return trace


# ----------------------------------------------------------------------------
# 5) PARSER (texto -> AST)
# ----------------------------------------------------------------------------
# Gramática reconhecida (aplicação associa à esquerda; corpo do lambda estende-se
# o máximo possível à direita):
#
#   term   ::= app
#   app    ::= atom { atom }            (aplicação, esq-associativa)
#   atom   ::= var | number | '(' term ')' | lambda
#   lambda ::= ('\\' | 'λ') ident { ident } '.' term
#
# Açúcares: 'λ' é aceito como sinônimo de '\\'; \\x y. M  ==  \\x. \\y. M.
# Identificadores podem ser nomes do prelúdio (PLUS, MULT, Y, ...). Um literal
# numérico (p.ex. 3) é resolvido pelo chamador via tabela de definições.

class ParseError(Exception):
    pass


def _tokenize(src: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    specials = {"(", ")", ".", "\\", "λ"}
    while i < len(src):
        c = src[i]
        if c.isspace():
            i += 1
            continue
        if c in specials:
            tokens.append("\\" if c == "λ" else c)
            i += 1
            continue
        # identificador: letras, dígitos, '_' (números são identificadores aqui)
        j = i
        while j < len(src) and (src[j].isalnum() or src[j] in "_'"):
            j += 1
        if j == i:
            raise ParseError(f"Caractere inesperado: {c!r} na posição {i}")
        tokens.append(src[i:j])
        i = j
    return tokens


class _Parser:
    def __init__(self, tokens: list[str]):
        self.toks = tokens
        self.pos = 0

    def _peek(self) -> Optional[str]:
        return self.toks[self.pos] if self.pos < len(self.toks) else None

    def _next(self) -> str:
        tok = self._peek()
        if tok is None:
            raise ParseError("Fim inesperado da expressão.")
        self.pos += 1
        return tok

    def _expect(self, tok: str) -> None:
        got = self._next()
        if got != tok:
            raise ParseError(f"Esperava {tok!r}, encontrei {got!r}.")

    def parse(self) -> Term:
        term = self._parse_app()
        if self._peek() is not None:
            raise ParseError(f"Token extra ao final: {self._peek()!r}")
        return term

    def _parse_app(self) -> Term:
        # Uma aplicação é uma sequência de átomos: a b c == ((a b) c)
        term = self._parse_atom()
        while True:
            nxt = self._peek()
            if nxt is None or nxt in (")", "."):
                break
            term = App(term, self._parse_atom())
        return term

    def _parse_atom(self) -> Term:
        tok = self._peek()
        if tok is None:
            raise ParseError("Esperava um átomo, mas a expressão acabou.")
        if tok == "(":
            self._next()
            term = self._parse_app()
            self._expect(")")
            return term
        if tok == "\\":
            return self._parse_lambda()
        if tok in (")", "."):
            raise ParseError(f"Token inesperado: {tok!r}")
        # identificador (variável ou nome do prelúdio)
        self._next()
        return Var(tok)

    def _parse_lambda(self) -> Term:
        self._expect("\\")
        params: list[str] = []
        while self._peek() is not None and self._peek() not in (".", "(", "\\", ")"):
            params.append(self._next())
        if not params:
            raise ParseError("Lambda sem parâmetros.")
        self._expect(".")
        body = self._parse_app()
        # \x y. M  ->  \x. (\y. M)
        for p in reversed(params):
            body = Abs(p, body)
        return body


def parse(src: str) -> Term:
    """Converte uma string de lambda-expressão em AST."""
    return _Parser(_tokenize(src)).parse()


# ----------------------------------------------------------------------------
# 6) alfa-EQUIVALÊNCIA (para testes/verificação de resultados)
# ----------------------------------------------------------------------------
def alpha_equal(a: Term, b: Term, env: Optional[dict[str, str]] = None) -> bool:
    """True se `a` e `b` são iguais a menos de renomeação de variáveis ligadas."""
    if env is None:
        env = {}
    if isinstance(a, Var) and isinstance(b, Var):
        # nomes ligados são comparados via env; livres devem ser idênticos.
        return env.get(a.name, a.name) == b.name
    if isinstance(a, App) and isinstance(b, App):
        return alpha_equal(a.func, b.func, env) and alpha_equal(a.arg, b.arg, env)
    if isinstance(a, Abs) and isinstance(b, Abs):
        return alpha_equal(a.body, b.body, {**env, a.param: b.param})
    return False
