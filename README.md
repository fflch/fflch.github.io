Figuras:

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

Generate:

    python3 generate_site.py   # também gera dio.png, topologia.png e vlans.html

Gestão de tarefas e issues (`bin/`):

    python3 bin/create_task.py     # nova atividade (pessoas escolhidas de content/pessoas.csv)
    python3 bin/edit_task.py       # responsáveis/estagiários; marcar estagiário como inativo
    python3 bin/create_issue.py    # nova issue (ajuda opcional do Claude na redação)
    python3 bin/edit_issue.py      # editar descrição/responsável de uma issue
    python3 bin/close_issue.py     # fechar issue (grava data_fechamento)
    python3 bin/comment_issue.py [codigo]  # comentar numa issue (comentário sem autor, com data)
    python3 bin/claude_housekeeping_issues.py [prefixo]  # revisa as issues abertas uma a uma: fecha ou melhora o texto com o Claude
    python3 bin/claude_housekeeping_github.py     # repos de fflch/uspdev (gh) → content/github.json (versionar!) → docs/github.html
    python3 bin/aplicar_mudancas.py        # aplica os "Baixar mudanças" pendentes de content/mudancas/ (controle em aplicadas.json)

Ao atribuir tarefa ou issue, os scripts perguntam se devem avisar a pessoa por
e-mail (via `msmtp -a sti`, remetente fflchsti@usp.br).

- `content/pessoas.csv`: cadastro de servidores e estagiários (nome completo, e-mail, vínculo).
  A reunião TI usa todos os servidores ativos daqui como participantes.
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




