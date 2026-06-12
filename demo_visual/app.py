"""
app.py -- Visualizador de apresentação (servidor local) para a AV2.

NÃO é a implementação dos modelos: é apenas uma "vitrine" que CHAMA o código
formal já existente em ../implementacoes e mostra os resultados no navegador.
A lógica do lambda-cálculo e da MTND continua 100% nos módulos originais
(lambda_calc.py, prelude.py, ntm.py, maquina_ww.py) -- aqui só apresentamos.

Como usar:
    python app.py
    # depois abra http://localhost:8000 no navegador

Usa SOMENTE a biblioteca padrão do Python (sem pip install, sem internet).
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# --- localizar e importar os módulos formais já existentes ------------------
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(ROOT, "implementacoes", "lambda_calculo"))
sys.path.insert(0, os.path.join(ROOT, "implementacoes", "mt_nao_deterministica"))

from lambda_calc import parse, normalize                  # noqa: E402
from prelude import expand, church_to_int                 # noqa: E402
from maquina_ww import build_machine, na_linguagem        # noqa: E402

MACHINE = build_machine()

PORT = 8000


# ---------------------------------------------------------------------------
# Lambda: roda o avaliador real e devolve o traço de beta-reducoes.
# ---------------------------------------------------------------------------
def api_lambda(expr: str) -> dict:
    expr = (expr or "").strip()
    if not expr:
        return {"erro": "Expressão vazia."}
    try:
        term = expand(parse(expr))
    except Exception as e:  # erro de parsing / nome desconhecido
        return {"erro": f"Não consegui interpretar: {e}"}

    trace: list[str] = []
    final, steps, ok = normalize(
        term, max_steps=20000, on_step=lambda i, t: trace.append(str(t))
    )
    trace.append(str(final))

    total = len(trace)
    boundary = None
    omitted = 0
    if total > 300:                       # paga payload menor p/ termos enormes
        head = [[i, trace[i]] for i in range(200)]
        tail = [[i, trace[i]] for i in range(total - 80, total)]
        boundary = 200
        omitted = total - 280
        passos_mostrados = head + tail
    else:
        passos_mostrados = [[i, s] for i, s in enumerate(trace)]

    decoded = church_to_int(final) if ok else None
    return {
        "ok": ok,
        "steps": steps,
        "result": str(final),
        "decoded": decoded,
        "passos": passos_mostrados,
        "total": total,
        "boundary": boundary,
        "omitted": omitted,
    }


# ---------------------------------------------------------------------------
# MTND: roda a máquina real e devolve veredito, caminho aceitante e árvore.
# ---------------------------------------------------------------------------
def _config_cells(cfg) -> dict:
    cells = []
    for i, c in enumerate(cfg.tape):
        sym = "_" if c == MACHINE.blank else c
        cells.append({"sym": sym, "head": i == cfg.head})
    return {"state": cfg.state, "cells": cells}


def api_ntm(word: str) -> dict:
    word = word or ""
    invalido = any(ch not in MACHINE.Sigma for ch in word)
    r = MACHINE.run(word)
    path = None
    if r.accepting_path:
        path = [_config_cells(c) for c in r.accepting_path]
    arvore = MACHINE.render_tree(
        MACHINE.computation_tree(word, max_depth=20, max_nodes=400)
    )
    return {
        "word": word,
        "accepted": r.accepted,
        "configs": r.configs_explored,
        "depth": r.max_depth,
        "path": path,
        "tree": arvore,
        "oraculo": na_linguagem(word),
        "invalido": invalido,
        "n_estados": len(MACHINE.Q),
        "n_transicoes": MACHINE.num_transitions(),
    }


# ---------------------------------------------------------------------------
# Servidor HTTP mínimo (biblioteca padrão).
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj: dict) -> None:
        self._send(200, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 (assinatura da stdlib)
        parsed = urlparse(self.path)
        route = parsed.path
        qs = parse_qs(parsed.query)

        if route in ("/", "/index.html"):
            path = os.path.join(BASE, "index.html")
            with open(path, "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
            return

        if route == "/api/lambda":
            self._json(api_lambda(qs.get("expr", [""])[0]))
            return

        if route == "/api/ntm":
            self._json(api_ntm(qs.get("word", [""])[0]))
            return

        self._send(404, b"Nao encontrado", "text/plain; charset=utf-8")

    def log_message(self, *args) -> None:  # silencia o log padrao
        pass


def main() -> None:
    print("=" * 60)
    print("  Visualizador da AV2 — Teoria da Computabilidade")
    print("  Equipe: Yuri Aguiar, João Rath, Pedro Paulo (CC5NA)")
    print("=" * 60)
    print(f"  MTND: {len(MACHINE.Q)} estados, {MACHINE.num_transitions()} transições")
    print(f"\n  >>> Abra no navegador:  http://localhost:{PORT}\n")
    print("  (Ctrl+C para encerrar)")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Encerrado.")
        server.shutdown()


if __name__ == "__main__":
    main()
