Figuras:

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

Generate:

    python3 generate_site.py   # também gera o diagrama de DIOs (content/dio.csv), topologia.png e vlans.html

Gestão de tarefas e issues (`bin/`):

    python3 bin/create_task.py     # nova atividade (pessoas escolhidas de content/pessoas.csv)
    python3 bin/edit_task.py       # responsáveis/estagiários; marcar estagiário como inativo
    python3 bin/create_issue.py    # nova issue (ajuda opcional do Claude na redação)
    python3 bin/edit_issue.py [N]      # editar descrição/responsável da issue #N (sem N: escolhe na lista)
    python3 bin/close_issue.py [N]     # fechar a issue #N (grava data_fechamento)
    python3 bin/comment_issue.py [N]   # comentar na issue #N (comentário sem autor, com data)
    python3 bin/claude_housekeeping_issues.py [prefixo]  # revisa as issues abertas uma a uma: fecha ou melhora o texto com o Claude
    python3 bin/claude_housekeeping_github.py     # repos de fflch/uspdev (gh) → content/github.json (versionar!) → docs/github.html
    python3 bin/aplicar_mudancas.py        # aplica os "Baixar mudanças" pendentes de content/mudancas/ (controle em aplicadas.json)
    python3 bin/create_meeting.py          # nova reunião: participantes, issues abertas, texto; pergunta se dispara o e-mail
    python3 bin/edit_meeting.py            # edita uma reunião agendada (título, data, horário, issues, participantes, texto)
    python3 bin/cancel_meeting.py          # cancela uma reunião agendada; pergunta se avisa por e-mail

Ao atribuir tarefa ou issue, os scripts perguntam se devem avisar a pessoa por
e-mail (via `msmtp -a sti`, remetente fflchsti@usp.br).

- `content/pessoas.csv`: cadastro de servidores e estagiários (nome completo, e-mail, vínculo).
- Reuniões: `content/meetings/AAAA-MM-DD-<titulo>.json` com `titulo`, `data`, `horario`, `participantes`,
  `issues` (códigos), `texto` e, quando houver, `email_enviado_em`, `cancelada_em`, `motivo_cancelamento`.
  Também podem ser criadas/editadas/canceladas em `docs/reunioes.html`: a página baixa um `mudancas-reuniao-*.json`
  que é aplicado pelo `aplicar_mudancas.py` (que pergunta se dispara o e-mail).
- Issues têm um número global sequencial (`"numero"` no JSON), exibido como **#N** no site, nos scripts e
  nos e-mails. O nome do arquivo (`<tarefa>-<n>.json`) é só interno; ao mudar de tarefa o arquivo muda, o #N não.
  Os códigos de tarefa (ex: `rat003`) também são internos: as páginas mostram o título.
- Comentários de issue ficam no próprio JSON: `"comentarios": [{"data": "dd/mm/aaaa", "texto": "..."}]`.
  Podem ser feitos pelo terminal (`comment_issue.py`) ou pelo 💬 da página de acompanhamento (vão no arquivo de mudanças).
- Estagiários nas tarefas: `{"nome": "...", "ativo": true}`; com `"ativo": false` não aparecem no site.
- `content/siglas.csv`: sigla, significado e área (código de `AREAS` em generate_site.py); o organograma interativo da home mostra só siglas com atividade ativa.
- Páginas geradas: `docs/dashboard.html` (estatísticas por pessoa) e `docs/issues-resolvidas.html` (relatório).



- Criar fflch/ansible-role-deploy-pixelfed
- Criar provisioner-dev mongodb, redis, minio

 https://github.com/fflch/ansible-role-deploy-pixelfed



 cabeamento:
https://portal.if.usp.br/ccifusp/pt-br/node/592
https://portal.if.usp.br/ccifusp/sites/portal.if.usp.br.ccifusp/files/Aviso%20de%20Contrata%C3%A7%C3%A3o%20-%2020-2025.pdf


Insumos de informática

     Pregão eletrônico no 17/2025 - IFUSP;


     Material de infraestrutura de rede de dados

     Pregão eletrônico no 20/2025 - IFUSP;

     Processo SEI no 154.00004881/2024-88;




