from graphviz import Digraph

dot = Digraph("mindmap", filename="docs/ti_fflch")

# Gera PDF
dot.format = "pdf"
dot.render(cleanup=True)

# Gera JPEG
dot.format = "jpg"
dot.render(cleanup=True)

# layout geral
dot.attr(
    rankdir="TB",
    splines="ortho"
)

# estilo dos nós
dot.attr(
    "node",
    shape="box",
    style="rounded,filled",
    fillcolor="lightyellow",
    fontname="Helvetica",
)

# estilo das arestas
dot.attr('edge', 
    minlen='4',
    fontsize='22', 
    fontcolor='#8B0000',
    color='black',
    penwidth='1',
    fontname="DejaVu Sans Mono"
)

dot.node("TI", "TI FFLCH", shape="ellipse", fillcolor="lightblue")

# Desenvolvimento
dot.attr("node",fillcolor="lightpink")
dot.node("DE", "Desenvolvimento\n(DE)")
dot.edge('TI', 'DE',minlen='10')
dot.edge('DE', 'Sistemas', xlabel='dev')
#dot.node("ex-sistema", "Implementar um novo recurso em um sistema",  fillcolor='#90EE90')
#dot.edge('Sistemas','ex-sistema',minlen='2')

dot.edge('DE', 'Bibliotecas', xlabel='bib')
#dot.node("ex-packagist", "Manter packagist",  fillcolor='#90EE90')
#dot.edge('Bibliotecas','ex-packagist',minlen='3')

# Servidores
dot.attr("node",fillcolor="honeydew")
dot.node("IF", "Servidores\n(SE)")
dot.edge('TI', 'IF')

dot.edge('IF', 'Provisionamento', xlabel='pro')
#dot.node("ex-ansible", "Criar tasks no Ansible",  fillcolor='#90EE90')
#dot.edge('Provisionamento','ex-ansible',minlen='2')

dot.edge('IF', 'Hosts',xlabel='hos')
#dot.node("TD", "- Troca de discos nos storages\n- Manter sistema operacional Hosts",  fillcolor='#90EE90')
#dot.edge('Hosts','TD',minlen='3')

dot.edge('IF', 'VMs',xlabel='vms')
#dot.node("exemplo-VMs", "Gerenciamento do Windows Server\n usado no servidor de impressão",  fillcolor='#90EE90')
#dot.edge('VMs','exemplo-VMs',minlen='4')

# Suporte Informática
dot.attr("node",fillcolor="lightblue")
dot.node("SU", "Suporte\n(SU)")
dot.edge('TI', 'SU',minlen='10')

dot.edge('SU', 'Chamado Técnico', xlabel='cht')
#dot.node("exemplo-chamado", "- Trocar HD\n- Instalar GIMP",  fillcolor='#90EE90')
#dot.edge('Chamado Técnico','exemplo-chamado',minlen='2')

# Rede
dot.attr("node",fillcolor="lavender")
dot.node("RE", "Rede\n(RE)")
dot.edge('TI', 'RE')

dot.node("RP", "Camada 1")
dot.edge('RE', 'RP', xlabel="pas")
#dot.node("ex-diagrama", "Criar diagramas dos racks",  fillcolor='#90EE90')
#dot.edge('RP','ex-diagrama',minlen='1')

dot.node("RA", "Camada 2")
dot.edge('RE', 'RA', xlabel="rat")
#dot.node("ex-switch", "Configurar um switch",  fillcolor='#90EE90')
#dot.edge('RA','ex-switch',minlen='2')

dot.node("RSF", "Rede Sem fio")
dot.edge('RE', 'RSF', xlabel='rsf')
#dot.node("ex-rsf", "Monitorar APs",  fillcolor='#90EE90')
#dot.edge('RSF','ex-rsf',minlen='3')

# Sites
dot.attr("node",fillcolor="lightgray")
dot.node("SI", "Sites\n(SI)")
dot.edge('TI', 'SI',minlen='10')

dot.edge('SI', 'Drupal Core', xlabel="cor")
#dot.node("ex-drupal", "Atualizar core e módulos",  fillcolor='#90EE90')
#dot.edge('Drupal Core','ex-drupal',minlen='2')

dot.edge('SI', 'Módulos', xlabel="mod")
#dot.node("ex-modulo", "Implementar novo recurso em um módulo",  fillcolor='#90EE90')
#dot.edge('Módulos','ex-modulo',minlen='3')

dot.edge('SI', 'Suporte', xlabel="dup")
#dot.node("exemplo-drupal-suporte", "Fazer um tutorial de como criar uma galeria de imagens",  fillcolor='#90EE90')
#dot.edge('Suporte','exemplo-drupal-suporte',minlen='4')

# Administração de Sistemas
dot.attr("node",fillcolor="lightgoldenrod")
dot.node("AS", "Administração de Sistemas\n(AS)")
dot.edge('TI', 'AS')

dot.edge('AS', 'Impressoras', xlabel='imp')
#dot.node("ex-ad-print", "Inserir nova impressora no AD",  fillcolor='#90EE90')
#dot.edge('Impressoras','ex-ad-print',minlen='3')

dot.edge('AS', 'Permissões', xlabel='per')
#dot.node("ex-copaco", "- Cadastrar novo estagiário no copaco\n- Remover estagiário do Copaco",  fillcolor='#90EE90')
#dot.edge('Permissões','ex-copaco',minlen='4')

dot.edge('AS', 'IoT', xlabel='iot')
#dot.node("exemplo-iot", "- Colocar um projetor na rede\n- Colocar um alarme na rede",  fillcolor='#90EE90')
#dot.edge('IoT','exemplo-iot',minlen='5')

# Gestão
dot.attr("node",fillcolor="lightcoral")
dot.node("GE", "Gestão\n(GE)")
dot.edge('TI', 'GE',minlen='10')

dot.edge('GE', 'Documentação', xlabel='doc')
#dot.node("ex-ges", "Manter material do curso de Laravel",  fillcolor='#90EE90')
#dot.edge('Documentação','ex-ges',minlen='2')

dot.edge('GE', 'Administração',xlabel='adm')
#dot.node("exemplo-adm", "Aprovação de Férias",  fillcolor='#90EE90')
#dot.edge('Administração','exemplo-adm',minlen='3')

dot.edge('GE', 'STI', xlabel='sti')
#dot.node("ex-autentusp", "Cadastrar pessoas no Autentusp",  fillcolor='#90EE90')
#dot.edge('STI','ex-autentusp',minlen='4')

dot.edge('GE', 'Compras', xlabel='com')
#dot.node("ex-fechaduras", "Compra do Fluke",  fillcolor='#90EE90')
#dot.edge('Compras','ex-fechaduras',minlen='5')

# Computação Científica
dot.attr("node",fillcolor="aliceblue")
dot.node("CC", "Computação Científica\n(CC)")
dot.edge('TI', 'CC')

dot.edge('CC', 'Infraestrutura para Pesquisa', xlabel='cci')
#dot.node("ex-cci", "Hospedagem de Aplicações Científicas",  fillcolor='#90EE90')
#dot.edge('Infraestrutura para Pesquisa','ex-cci',minlen='3')

dot.edge('CC', 'Acompanhamento de Desenvolvimento', xlabel='ccd')
#dot.node("ex-ccd", "Análise de Pull Request de Aplicações Científicas",  fillcolor='#90EE90')
#dot.edge('Acompanhamento de Desenvolvimento','ex-ccd',minlen='4')

dot.edge('CC', 'Suporte Tecnológico', xlabel='ccs')
#dot.node("ex-ccs", "Curso de Bash Linux para Pós-graduandos",  fillcolor='#90EE90')
#dot.edge('Suporte Tecnológico','ex-ccs',minlen='5')

# Projetos USP
dot.attr("node",fillcolor="beige")
dot.node("PU", "Projetos USP\n(PU)")
dot.edge('TI', 'PU',minlen='10')

dot.edge('PU', 'COI', xlabel='coi')
#dot.node("exemplo-coi", "Plugin wordpress no site do COI",  fillcolor='#90EE90')
#dot.edge('COI','exemplo-coi',minlen='3')

dot.edge('PU', 'ABCD', xlabel='abc')
#dot.node("exemplo-abcd", "Módulo Drupal Indicadores",  fillcolor='#90EE90')
#dot.edge('ABCD','exemplo-abcd',minlen='4')

dot.edge('PU', 'prceu', xlabel='prc')
#dot.node("exemplo-prceu", "Plugin Moodle para integração com o Apolo",  fillcolor='#90EE90')
#dot.edge('prceu','exemplo-prceu',minlen='5')

dot.edge('PU', 'fediverso', xlabel='fed')
#dot.node("exemplo-fediverso", "Integração pixeldef com senha única",  fillcolor='#90EE90')
#dot.edge('fediverso','exemplo-fediverso',minlen='5')

# ===== Legenda =====
#with dot.subgraph(name='cluster_legenda') as legend:
#    # Nó invisivel, só para deslocar os outros nós para baixo
#    legend.node(
#        'leg0',
#        shape='point', width='0',
#        fillcolor='#FFFFFF',
#    )
#        
#    legend.node(
#        'leg1',
#        label='Categoria Principal',
#        shape='box',
#        fillcolor='#FFFFFF',
#    )
#
#    legend.node(
#        'leg2',
#        label='Subcategoria',
#        shape='box',
#        fillcolor='#FFFFFF'
#    )
#
#    legend.node(
#        'leg3',
#        label='Exemplos',
#        shape='box',
#        fillcolor='#90EE90'
#    )

    # força layout vertical
#   legend.edge('leg0', 'leg1', style='invis')
#   legend.edge('leg1', 'leg2',xlabel='Prefixo\ncódigo\nda\ntarefa', fontsize='16', fontcolor='#8B0000',fontname="DejaVu Sans Mono")
#    legend.edge('leg2', 'leg3')

dot.render(cleanup=True)
