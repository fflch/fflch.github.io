"""
Cria uma reunião: participantes, issues abertas como pauta, texto livre e (opcional) e-mail.

    python3 bin/create_meeting.py

Grava content/meetings/AAAA-MM-DD-<titulo>.json e, se você quiser, dispara o e-mail de
convocação para os participantes (via msmtp, igual aos avisos de issue).
A mesma reunião pode ser montada pela página docs/reunioes.html ("+ Nova reunião") e
aplicada com bin/aplicar_mudancas.py.
"""
import os
import re
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import (  # noqa: E402
    load_pessoas, perguntar_sim_nao, ler_texto_multilinha, editar_no_editor,
    salvar_reuniao, oferecer_email_reuniao, data_reuniao_br, rotulo_issue,
    ISSUES_DIR, TASKS_DIR,
)


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def ler_indices(texto, total):
    """'1,3,5-7' → {0, 2, 4, 5, 6}; None se inválido."""
    out = set()
    for parte in texto.replace(" ", "").split(","):
        if not parte:
            continue
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", parte)
        if not m:
            return None
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if not (1 <= a <= b <= total):
            return None
        out.update(range(a - 1, b))
    return out


def issues_abertas():
    tarefas = {}
    for f in os.listdir(TASKS_DIR):
        if f.endswith(".json"):
            tarefas[f[:-5]] = carregar(os.path.join(TASKS_DIR, f))
    out = []
    for f in sorted(os.listdir(ISSUES_DIR)):
        if not f.endswith(".json"):
            continue
        i = carregar(os.path.join(ISSUES_DIR, f))
        cod = f[:-5]
        task = tarefas.get(cod.rsplit("-", 1)[0], {})
        if i.get("status") is True and task.get("status") is True:
            out.append({"codigo": cod, "numero": i.get("numero"), "descricao": i.get("descricao", ""),
                        "responsavel": (i.get("responsavel") or "").strip(),
                        "titulo_task": task.get("titulo", "")})
    return out


def escolher_issues(iniciais=()):
    """Escolhe as issues da pauta. iniciais: códigos já na pauta (ao editar uma reunião)."""
    todas = sorted(issues_abertas(), key=lambda i: (i["responsavel"] or "~", i["codigo"]))
    if not todas and not iniciais:
        print("\nℹ Nenhuma issue aberta.")
        return [], {}
    selecionadas = list(iniciais)
    while True:
        filtro = input(f"\nIssues abertas ({len(todas)}). Filtrar por texto (tarefa, descrição, pessoa; Enter = todas): ").strip().lower()
        vis = [i for i in todas if not filtro or filtro in
               f"#{i['numero']} {i['titulo_task']} {i['descricao']} {i['responsavel']}".lower()]
        if not vis:
            print("Nada encontrado.")
            continue
        resp_atual = None
        for n, i in enumerate(vis, 1):
            if i["responsavel"] != resp_atual:
                resp_atual = i["responsavel"]
                print(f"\n  👤 {resp_atual or 'sem responsável'}")
            marca = "✓" if i["codigo"] in selecionadas else " "
            print(f"  {marca}{'#' + str(i['numero']):>5} · {i['titulo_task']}")
            print(f"        {i['descricao'][:150]}")
        r = input("\nNúmeros (#) das issues para a pauta (ex: 12,40; número já marcado desmarca; Enter = nenhuma): ").strip()
        if r:
            por_num = {i["numero"]: i["codigo"] for i in vis}
            nums = [x.strip().lstrip("#") for x in r.split(",") if x.strip()]
            if not all(x.isdigit() and int(x) in por_num for x in nums):
                print("Entrada inválida: use os números (#) mostrados na lista.")
                continue
            for x in nums:
                c = por_num[int(x)]
                selecionadas.remove(c) if c in selecionadas else selecionadas.append(c)
        print("Pauta: " + (", ".join(rotulo_issue(resolver_dados(c)) for c in selecionadas) or "(nenhuma issue)"))
        if not perguntar_sim_nao("Adicionar mais issues (outro filtro)?"):
            return selecionadas, {i["codigo"]: i for i in todas}


def resolver_dados(cod):
    caminho = os.path.join(ISSUES_DIR, f"{cod}.json")
    return carregar(caminho) if os.path.exists(caminho) else {}


def escolher_participantes(sugeridos, iniciais=None):
    """iniciais: participantes já marcados (ao editar); sem isso, marca os sugeridos."""
    pessoas = [p["nome"] for p in sorted((p for p in load_pessoas().values() if p["ativo"]),
                                         key=lambda p: (p.get("vinculo") != "servidor", p["nome"]))]
    pessoas += [n for n in list(sugeridos) + list(iniciais or []) if n not in pessoas]
    vinculo = {p["nome"]: p.get("vinculo") for p in load_pessoas().values()}
    marcados = [n for n in pessoas if n in (iniciais if iniciais is not None else sugeridos)]
    while True:
        print("\nParticipantes (✓ = marcado; 🔗 = responsável por issue da pauta):\n")
        for n, nome in enumerate(pessoas, 1):
            print(f"  {'✓' if nome in marcados else ' '}[{n:02d}] {nome}  ({vinculo.get(nome) or '-'})"
                  + ("  🔗" if nome in sugeridos else ""))
        print("\nNúmeros/faixas marcam ou desmarcam (ex: 3,5-8). Atalhos: s = + servidores · e = + estagiários · l = limpar")
        r = input("Enter confirma a seleção: ").strip().lower()
        if not r:
            if marcados:
                return marcados
            print("Escolha ao menos um participante.")
            continue
        if r in ("s", "e"):
            v = "servidor" if r == "s" else "estagiario"
            marcados += [n for n in pessoas if vinculo.get(n) == v and n not in marcados]
        elif r == "l":
            marcados = []
        else:
            idx = ler_indices(r, len(pessoas))
            if idx is None:
                print("Entrada inválida.")
                continue
            for k in sorted(idx):
                nome = pessoas[k]
                marcados.remove(nome) if nome in marcados else marcados.append(nome)
        marcados = [n for n in pessoas if n in marcados]


def responsaveis(codigos):
    return list(dict.fromkeys(r for r in ((resolver_dados(c).get("responsavel") or "").strip() for c in codigos) if r))


def main():
    print("\n--- Nova reunião ---")
    titulo = input("Título [Reunião Planejamento TI FFLCH]: ").strip() or "Reunião Planejamento TI FFLCH"
    hoje = datetime.now().strftime("%Y-%m-%d")
    while True:
        data = input(f"Data (AAAA-MM-DD) [{hoje}]: ").strip() or hoje
        try:
            datetime.strptime(data, "%Y-%m-%d")
            break
        except ValueError:
            print("Data inválida.")
    horario = input("Horário (ex: 10h às 11h; opcional): ").strip()

    issues, por_codigo = escolher_issues()
    sugeridos = responsaveis(issues)
    participantes = escolher_participantes(sugeridos)

    if perguntar_sim_nao("\nEscrever o texto adicional no editor?"):
        texto = editar_no_editor("")
    else:
        texto = ler_texto_multilinha("\nTexto adicional (outras pautas, avisos, link da sala…)")

    print("\n" + "=" * 63)
    print(f"{titulo} · {data_reuniao_br(data)}" + (f" · {horario}" if horario else ""))
    print(f"Participantes ({len(participantes)}): " + ", ".join(participantes))
    print(f"Issues ({len(issues)}): " + (", ".join(rotulo_issue(resolver_dados(c)) for c in issues) or "nenhuma"))
    if texto:
        print("Texto:\n  " + texto.replace("\n", "\n  "))
    print("=" * 63)
    if not perguntar_sim_nao("Salvar reunião?", padrao=True):
        print("Nada foi gravado.")
        return

    caminho = salvar_reuniao({"titulo": titulo, "data": data, "horario": horario,
                              "participantes": participantes, "issues": issues, "texto": texto})
    print(f"✔ {os.path.relpath(caminho, BASE_DIR)}")
    oferecer_email_reuniao(caminho, padrao=False)
    print("\nRegenere o site (python3 generate_site.py) e faça commit/push.")


if __name__ == "__main__":
    main()
