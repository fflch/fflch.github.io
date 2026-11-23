"""
Edita uma reunião agendada (de hoje em diante): título, data, horário, issues, participantes, texto.

    python3 bin/edit_meeting.py

O arquivo e o link da reunião continuam os mesmos. No fim mostra o que mudou, grava e
pergunta se envia aos participantes um e-mail avisando da atualização.
"""
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fflch_common import (  # noqa: E402
    reunioes_agendadas, data_reuniao_br, perguntar_sim_nao, editar_no_editor,
    diferencas_reuniao, atualizar_reuniao, CAMPOS_EDITAVEIS,
)
import create_meeting as cm  # noqa: E402  (mesmas telas de escolha de issues e participantes)


def resumo(d):
    return f"{d['titulo']} · {data_reuniao_br(d['data'])}" + (f" · {d['horario']}" if d.get("horario") else "")


def main():
    agendadas = reunioes_agendadas()
    if not agendadas:
        print("Nenhuma reunião agendada de hoje em diante.")
        return
    print("\nReuniões agendadas:\n")
    for n, (_, d) in enumerate(agendadas, 1):
        print(f"  [{n}] {resumo(d)}")
    r = input("\nQual editar? (número, Enter = nenhuma): ").strip()
    if not r:
        return
    if not r.isdigit() or not 1 <= int(r) <= len(agendadas):
        sys.exit("Opção inválida.")
    caminho, antes = agendadas[int(r) - 1]
    novo = {k: (list(antes[k]) if isinstance(antes.get(k), list) else antes.get(k, "")) for k in CAMPOS_EDITAVEIS}

    while True:
        print("\n" + "=" * 63)
        print(resumo(novo))
        print(f"Participantes ({len(novo['participantes'])}): " + ", ".join(novo["participantes"]))
        print(f"Issues ({len(novo['issues'])}): "
              + (", ".join(cm.rotulo_issue(cm.resolver_dados(c)) for c in novo["issues"]) or "nenhuma"))
        if novo["texto"]:
            print("Texto:\n  " + novo["texto"].replace("\n", "\n  "))
        print("=" * 63)
        op = input("[t]ítulo  [d]ata  [h]orário  [i]ssues  [p]articipantes  [x] texto  "
                   "[s]alvar  [c]ancelar edição: ").strip().lower()
        if op == "t":
            novo["titulo"] = input(f"Título [{novo['titulo']}]: ").strip() or novo["titulo"]
        elif op == "d":
            v = input(f"Data (AAAA-MM-DD) [{novo['data']}]: ").strip() or novo["data"]
            try:
                datetime.strptime(v, "%Y-%m-%d")
                novo["data"] = v
            except ValueError:
                print("Data inválida.")
        elif op == "h":
            v = input(f"Horário [{novo['horario'] or 'vazio'}] (\"-\" apaga): ").strip()
            novo["horario"] = "" if v == "-" else (v or novo["horario"])
        elif op == "i":
            novo["issues"], _ = cm.escolher_issues(novo["issues"])
            novos_resp = [n for n in cm.responsaveis(novo["issues"]) if n not in novo["participantes"]]
            if novos_resp and perguntar_sim_nao("Incluir nos participantes os responsáveis das issues novas ("
                                                + ", ".join(novos_resp) + ")?", padrao=True):
                novo["participantes"] += novos_resp
        elif op == "p":
            novo["participantes"] = cm.escolher_participantes(cm.responsaveis(novo["issues"]), novo["participantes"])
        elif op == "x":
            novo["texto"] = editar_no_editor(novo["texto"] or "")
        elif op == "c":
            print("Nada foi alterado.")
            return
        elif op == "s":
            mudancas = diferencas_reuniao(antes, novo)
            if not mudancas:
                print("Nenhuma alteração.")
                return
            print("\nAlterações:\n  " + "\n  ".join(mudancas))
            if not perguntar_sim_nao("Gravar?", padrao=True):
                continue
            atualizar_reuniao(caminho, novo, padrao_email=False)
            print("\nRegenere o site (python3 generate_site.py) e faça commit/push.")
            return


if __name__ == "__main__":
    main()
