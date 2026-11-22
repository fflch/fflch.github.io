"""
Fecha uma issue (status false + data_fechamento).

    python3 bin/close_issue.py        # escolhe na lista pelo número (#N)
    python3 bin/close_issue.py 12     # fecha direto a issue #12
"""
import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import ISSUES_DIR, escolher_issue_cli, resolver_issue, rotulo_issue, perguntar_sim_nao  # noqa: E402


def main():
    if len(sys.argv) > 1:
        codigo = resolver_issue(sys.argv[1])
        if not codigo:
            sys.exit(f"Issue {sys.argv[1]} não encontrada.")
    else:
        codigo = escolher_issue_cli(msg="Número da issue a fechar (#)")
        if not codigo:
            return
    caminho = os.path.join(ISSUES_DIR, f"{codigo}.json")
    with open(caminho, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("status") is not True:
        print(f"Issue {rotulo_issue(data)} já está fechada.")
        return
    print(f"\nIssue {rotulo_issue(data)}: {data.get('descricao', '')}")
    if not perguntar_sim_nao("Fechar?", padrao=True):
        print("Nada foi alterado.")
        return
    data["status"] = False
    data["data_fechamento"] = datetime.now().strftime("%d/%m/%Y")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✔ Issue {rotulo_issue(data)} fechada.")


if __name__ == "__main__":
    main()
