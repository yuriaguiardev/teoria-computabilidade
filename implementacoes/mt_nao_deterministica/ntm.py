"""
ntm.py -- Simulador de uma MÁQUINA DE TURING NÃO DETERMINÍSTICA (MTND).

Implementa EXPLICITAMENTE o formalismo da Opção 4 da AV2. A diferença para a MT
determinística está na função de transição, que aqui é uma RELAÇÃO:

        δ : (Q × Γ)  →  P(Q × Γ × {L, R, S})

ou seja, para um mesmo par (estado, símbolo lido) pode haver VÁRIAS transições
possíveis. A computação deixa de ser um caminho e passa a ser uma ÁRVORE de
configurações. O critério de aceitação é por EXISTÊNCIA DE RAMO ACEITANTE:

        w ∈ L(M)  sse  ALGUM ramo da árvore atinge um estado de aceitação.

Componentes formais (uma MTND é a 7-upla):
        M = (Q, Σ, Γ, δ, q0, b, F)
    Q   ... conjunto finito de estados
    Σ   ... alfabeto de entrada
    Γ   ... alfabeto de fita  (Σ ⊆ Γ, e b ∈ Γ \\ Σ)
    δ   ... relação de transição (não determinística)
    q0  ... estado inicial
    b   ... símbolo branco
    F   ... conjunto de estados de aceitação
A REJEIÇÃO é por MORTE DO RAMO (ausência de transição aplicável), não por um
estado dedicado. O parâmetro `q_rej` do construtor é uma extensão OPCIONAL (não
usada por esta máquina) e não faz parte da 7-upla formal.

O simulador explora a árvore por BUSCA EM LARGURA (BFS), com um conjunto de
configurações já visitadas (evita laços) e um limite de passos. Também sabe
construir e desenhar a árvore de computação para entradas pequenas.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Optional


# Direções do cabeçote. 'S' (stay) = movimento estacionário.
LEFT, RIGHT, STAY = "L", "R", "S"

# Uma transição-destino: (novo_estado, símbolo_escrito, movimento).
Move = tuple[str, str, str]
# A relação δ: mapeia (estado, símbolo_lido) -> lista de Move possíveis.
Delta = dict[tuple[str, str], list[Move]]


@dataclass(frozen=True)
class Config:
    """Uma CONFIGURAÇÃO INSTANTÂNEA (snapshot) da máquina: estado + fita + posição
    do cabeçote. Imutável e hashável para podermos detectar repetições."""
    state: str
    tape: tuple[str, ...]   # conteúdo da fita (sem brancos supérfluos nas pontas)
    head: int               # índice do cabeçote dentro de `tape`

    def render(self, blank: str) -> str:
        """Desenha a fita com o cabeçote destacado por colchetes. Ex.: q3: a b [a] b"""
        cells = []
        for i, c in enumerate(self.tape):
            sym = c if c != blank else "_"
            cells.append(f"[{sym}]" if i == self.head else sym)
        return f"{self.state}: " + " ".join(cells)


@dataclass
class TreeNode:
    """Nó da árvore de computação (para visualização)."""
    config: Config
    children: list["TreeNode"]
    status: str  # "interno", "aceita", "morto" (sem transições), "corte" (limite)


@dataclass
class Result:
    """Resultado de uma simulação."""
    accepted: bool
    configs_explored: int
    max_depth: int
    accepting_path: Optional[list[Config]]
    cut_by_limit: bool   # True se a busca parou por causa do limite de passos


class NTM:
    def __init__(
        self,
        states: Iterable[str],
        input_alphabet: Iterable[str],
        tape_alphabet: Iterable[str],
        delta: Delta,
        start: str,
        blank: str,
        accept: Iterable[str],
        reject: Optional[str] = None,
        name: str = "MTND",
    ):
        self.Q = set(states)
        self.Sigma = set(input_alphabet)
        self.Gamma = set(tape_alphabet)
        self.delta = delta
        self.q0 = start
        self.blank = blank
        self.F = set(accept)
        self.q_rej = reject
        self.name = name
        self._validate()

    # ---- validação básica do formalismo --------------------------------
    def _validate(self) -> None:
        assert self.blank in self.Gamma, "branco precisa estar em Γ"
        assert self.blank not in self.Sigma, "branco não pode estar em Σ"
        assert self.Sigma <= self.Gamma, "Σ deve ser subconjunto de Γ"
        assert self.q0 in self.Q, "estado inicial deve estar em Q"
        assert self.F <= self.Q, "estados de aceitação devem estar em Q"
        for (q, a), moves in self.delta.items():
            assert q in self.Q, f"estado {q!r} fora de Q"
            assert a in self.Gamma, f"símbolo {a!r} fora de Γ"
            for (q2, a2, d) in moves:
                assert q2 in self.Q, f"destino {q2!r} fora de Q"
                assert a2 in self.Gamma, f"escrita {a2!r} fora de Γ"
                assert d in (LEFT, RIGHT, STAY), f"movimento {d!r} inválido"

    # ---- contagem de transições (requisito de complexidade) ------------
    def num_transitions(self) -> int:
        return sum(len(v) for v in self.delta.values())

    # ---- configuração inicial ------------------------------------------
    def initial_config(self, word: str) -> Config:
        tape = tuple(word) if word else (self.blank,)
        return Config(self.q0, tape, 0)

    # ---- normalização da fita (canônica p/ detecção de visitados) ------
    def _normalize(self, cells: list[str], head: int) -> tuple[tuple[str, ...], int]:
        # remove brancos à esquerda (mantendo o cabeçote válido)
        while head > 0 and cells[0] == self.blank:
            cells.pop(0)
            head -= 1
        # remove brancos à direita além do cabeçote
        while len(cells) > head + 1 and cells[-1] == self.blank:
            cells.pop()
        if not cells:
            cells = [self.blank]
            head = 0
        return tuple(cells), head

    # ---- sucessores de uma configuração (o passo não determinístico) ---
    def successors(self, cfg: Config) -> list[Config]:
        read = cfg.tape[cfg.head]
        moves = self.delta.get((cfg.state, read), [])
        result: list[Config] = []
        for (q2, write, d) in moves:
            cells = list(cfg.tape)
            cells[cfg.head] = write
            head = cfg.head
            if d == RIGHT:
                head += 1
                if head == len(cells):
                    cells.append(self.blank)
            elif d == LEFT:
                if head == 0:
                    cells.insert(0, self.blank)
                else:
                    head -= 1
            # STAY: não move
            tape, head = self._normalize(cells, head)
            result.append(Config(q2, tape, head))
        return result

    def is_accepting(self, cfg: Config) -> bool:
        return cfg.state in self.F

    # ---- simulação por BFS sobre a árvore de configurações -------------
    def run(self, word: str, max_steps: int = 100_000) -> Result:
        """Aceita sse ALGUM ramo atingir um estado de F. Usa BFS com conjunto de
        visitados (evita reexplorar configurações) e limite de passos."""
        # rejeita já na entrada símbolos fora de Σ
        for ch in word:
            if ch not in self.Sigma:
                return Result(False, 0, 0, None, cut_by_limit=False)

        start = self.initial_config(word)
        if self.is_accepting(start):
            return Result(True, 1, 0, [start], cut_by_limit=False)

        visited: set[Config] = {start}
        parent: dict[Config, Optional[Config]] = {start: None}
        depth: dict[Config, int] = {start: 0}
        queue: deque[Config] = deque([start])
        explored = 0
        max_depth = 0
        cut = False

        while queue:
            cfg = queue.popleft()
            explored += 1
            max_depth = max(max_depth, depth[cfg])
            if depth[cfg] >= max_steps:
                cut = True
                continue
            for nxt in self.successors(cfg):
                if nxt in visited:
                    continue
                visited.add(nxt)
                parent[nxt] = cfg
                depth[nxt] = depth[cfg] + 1
                if self.is_accepting(nxt):
                    return Result(True, explored + 1, depth[nxt],
                                  self._path(parent, nxt), cut_by_limit=False)
                queue.append(nxt)

        return Result(False, explored, max_depth, None, cut_by_limit=cut)

    @staticmethod
    def _path(parent: dict[Config, Optional[Config]], end: Config) -> list[Config]:
        path = [end]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])  # type: ignore[arg-type]
        path.reverse()
        return path

    # ---- construção da árvore de computação (para visualização) --------
    def computation_tree(self, word: str, max_depth: int = 12,
                         max_nodes: int = 400) -> TreeNode:
        """Constrói a árvore de computação (com repetições, p/ enxergar a
        ramificação) até `max_depth` níveis ou `max_nodes` nós."""
        for ch in word:
            if ch not in self.Sigma:
                root = TreeNode(self.initial_config(word), [], "morto")
                return root

        count = [0]

        def build(cfg: Config, d: int) -> TreeNode:
            count[0] += 1
            if self.is_accepting(cfg):
                return TreeNode(cfg, [], "aceita")
            if d >= max_depth or count[0] >= max_nodes:
                return TreeNode(cfg, [], "corte")
            succs = self.successors(cfg)
            if not succs:
                return TreeNode(cfg, [], "morto")
            return TreeNode(cfg, [build(s, d + 1) for s in succs], "interno")

        return build(self.initial_config(word), 0)

    def render_tree(self, node: TreeNode, prefix: str = "", is_last: bool = True) -> str:
        """Desenha a árvore de computação em ASCII."""
        marks = {"aceita": " ✓ ACEITA", "morto": " ✗ (sem transições)",
                 "corte": " … (limite)", "interno": ""}
        connector = "└─ " if is_last else "├─ "
        line = prefix + (connector if prefix else "") + \
            node.config.render(self.blank) + marks[node.status]
        lines = [line]
        child_prefix = prefix + ("   " if is_last else "│  ")
        for i, child in enumerate(node.children):
            lines.append(self.render_tree(child, child_prefix,
                                          i == len(node.children) - 1))
        return "\n".join(lines)
