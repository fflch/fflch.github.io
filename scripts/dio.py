"""
Diagrama de fibras entre prédios (DIOs), gerado a partir de content/dio.csv.

Cada linha do CSV é um par de fibra ligado ponto a ponto entre dois DIOs:

    predio1,tr1,rack1,dio1,par1,predio2,tr2,rack2,dio2,par2
    Administração,1,A1,1,1,Letras,2,B1,1,1

- prédio → várias TRs (Telecommunications Room) → vários racks → vários DIOs → vários pares.
- Um lado sem DIO (tr/rack/dio/par vazios) é tratado como ponto externo (ex: provedor).
- Linhas começando com "#" são ignoradas (comentários, ligações ainda incompletas).

Gera docs/dio.html: um fragmento (dados JSON + scripts) incluído na documentação da tarefa
"Diagramas" via [[include_html:../docs/dio.html]]. O desenho é feito no navegador por
assets/dio/dio.js (interativo: destacar ligação, filtrar por prédio, tabela).
"""
import csv
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "content", "dio.csv")
SAIDA = os.path.join(BASE_DIR, "docs", "dio.html")
COLUNAS = ["predio1", "tr1", "rack1", "dio1", "par1", "predio2", "tr2", "rack2", "dio2", "par2"]


def _ponta(row, lado):
    p = {k: (row.get(f"{k}{lado}") or "").strip() for k in ("predio", "tr", "rack", "dio", "par")}
    p["externo"] = not p["dio"]
    if p["par"] and not p["par"].isdigit():
        raise ValueError(f"par deve ser um número: {p['par']!r}")
    return p


def carregar(caminho=CSV_PATH):
    with open(caminho, newline="", encoding="utf-8") as f:
        # linhas começando com "#" são comentários (anotações, ligações pendentes)
        leitor = csv.DictReader(l for l in f if not l.lstrip().startswith("#"))
        faltando = [c for c in COLUNAS if c not in (leitor.fieldnames or [])]
        if faltando:
            raise ValueError(f"{caminho}: colunas faltando: {', '.join(faltando)}")
        linhas = list(leitor)

    predios = {}   # nome -> {trs: {tr: {racks: {rack: {dio: max_par}}}}, externo}
    ligacoes, usados, avisos = [], {}, []

    def registrar(p):
        pr = predios.setdefault(p["predio"], {"trs": {}, "externo": False})
        if p["externo"]:
            pr["externo"] = True
            return
        dios = pr["trs"].setdefault(p["tr"], {}).setdefault(p["rack"], {})
        dios[p["dio"]] = max(dios.get(p["dio"], 0), int(p["par"] or 0))

    for n, row in enumerate(linhas, 2):
        if not any((v or "").strip() for v in row.values()):
            continue
        try:
            a, b = _ponta(row, 1), _ponta(row, 2)
        except ValueError as e:
            avisos.append(f"linha {n}: {e}")
            continue
        if not a["predio"] or not b["predio"]:
            avisos.append(f"linha {n}: prédio vazio — ignorada")
            continue
        for p in (a, b):
            if not p["externo"]:
                if not p["par"]:
                    avisos.append(f"linha {n}: {p['predio']} DIO {p['dio']} sem par — ignorada")
                    break
                chave = (p["predio"], p["tr"], p["rack"], p["dio"], p["par"])
                if chave in usados:
                    avisos.append(f"linha {n}: par {p['par']} do DIO {p['dio']} ({p['predio']}) "
                                  f"já usado na linha {usados[chave]}")
                usados[chave] = n
        else:
            registrar(a)
            registrar(b)
            ligacoes.append({"a": a, "b": b})

    def ordenar(d):
        return sorted(d, key=lambda x: (not str(x).isdigit(), int(x) if str(x).isdigit() else 0, str(x)))

    saida = []
    for nome, pr in predios.items():
        saida.append({
            "nome": nome,
            "externo": pr["externo"] and not pr["trs"],
            "trs": [{"nome": tr, "racks": [{"nome": rk, "dios": [{"nome": d, "pares": pr["trs"][tr][rk][d]}
                                                                 for d in ordenar(pr["trs"][tr][rk])]}
                                           for rk in ordenar(pr["trs"][tr])]}
                    for tr in ordenar(pr["trs"])],
        })
    return {"predios": saida, "ligacoes": ligacoes}, avisos


def main():
    if not os.path.exists(CSV_PATH):
        print(f"ℹ {CSV_PATH} não existe; diagrama de DIOs não gerado.")
        return
    dados, avisos = carregar()
    for a in avisos:
        print(f"⚠ dio.csv {a}")
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    js = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    # tudo em poucas linhas, sem linhas em branco: o fragmento passa pelo Markdown
    html = (
        '<link rel="stylesheet" href="../assets/dio/dio.css">\n'
        '<div class="dio-app" id="dio-app"><noscript>O diagrama precisa de JavaScript.</noscript></div>\n'
        f'<script type="application/json" id="dio-dados">{js}</script>\n'
        '<script src="../assets/dio/dio.js"></script>\n'
    )
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Diagrama de DIOs: {len(dados['ligacoes'])} ligação(ões), {len(dados['predios'])} prédio(s) → {SAIDA}")


if __name__ == "__main__":
    sys.exit(main())
