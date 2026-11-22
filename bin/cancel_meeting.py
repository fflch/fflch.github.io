"""
Cancela uma reunião agendada (de hoje em diante).

    python3 bin/cancel_meeting.py

A reunião continua em content/meetings/ marcada com "cancelada_em" (aparece riscada na
página) e o script pergunta se avisa os participantes por e-mail.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import reunioes_agendadas, cancelar_reuniao, data_reuniao_br, perguntar_sim_nao  # noqa: E402


def main():
    agendadas = reunioes_agendadas()
    if not agendadas:
        print("Nenhuma reunião agendada de hoje em diante.")
        return
    print("\nReuniões agendadas:\n")
    for n, (_, d) in enumerate(agendadas, 1):
        print(f"  [{n}] {d['titulo']} · {data_reuniao_br(d['data'])}" + (f" · {d['horario']}" if d.get("horario") else ""))
    r = input("\nQual cancelar? (número, Enter = nenhuma): ").strip()
    if not r:
        return
    if not r.isdigit() or not 1 <= int(r) <= len(agendadas):
        sys.exit("Opção inválida.")
    caminho, d = agendadas[int(r) - 1]
    motivo = input("Motivo (opcional): ").strip()
    if not perguntar_sim_nao(f"Cancelar \"{d['titulo']}\" de {data_reuniao_br(d['data'])}?", padrao=True):
        print("Nada foi alterado.")
        return
    cancelar_reuniao(caminho, motivo, padrao_email=True)
    print("\nRegenere o site (python3 generate_site.py) e faça commit/push.")


if __name__ == "__main__":
    main()
