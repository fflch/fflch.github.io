import os
import pandas as pd
from graphviz import Digraph

def generate_topology():
    csv_path = 'assets/camada2/camada2.csv'

    if not os.path.exists(csv_path):
        print(f"Aviso: Certifique-se de que o arquivo existe no caminho {csv_path}")
        return

    df = pd.read_csv(csv_path)

    ALL_BUILDINGS = ['adm', 'letras', 'fcs', 'gh', 'ccj']

    dot = Digraph('Network_Topology', comment='Topologia Radial Limpa')
    
    # Layout hierárquico limpo
    dot.attr(
        layout='dot',
        rankdir='TB',
        overlap='false',
        splines='true',
        nodesep='0.8',
        ranksep='1.5',
        bgcolor='#FAFAFA', 
        fontname='Helvetica, Arial, sans-serif'
    )
    
    dot.attr('node', fontname='Helvetica, Arial, sans-serif')
    dot.attr('edge', fontname='Helvetica, Arial, sans-serif', penwidth='1.5', color='#546E7A')

    # Nó Central (CORE L3)
    dot.node('CORE', 'CORE L3', 
             fillcolor='#1E88E5', fontcolor='white', shape='rectangle', 
             style='filled,rounded', width='3.0', height='1.2', fontsize='40')

    building_vlans = {b: [] for b in ALL_BUILDINGS}

    # Processamento e agrupamento das VLANs
    for idx, row in df.iterrows():
        vlan = str(row['vlan']).strip()
        name = str(row['name']).strip()
        network = str(row['network']).strip()
        nat = str(row['nat']).strip()
        predio_attr = str(row['predio']).strip().lower()

        if predio_attr == 'none' or not predio_attr:
            continue

        if predio_attr == 'all':
            target_buildings = ALL_BUILDINGS
        else:
            target_buildings = [b.strip() for b in predio_attr.split(',') if b.strip() in ALL_BUILDINGS]

        vlan_info = f"• {vlan} | {name} | {network} | {nat}"

        for b in target_buildings:
            building_vlans[b].append(vlan_info)

    # Criação da estrutura limpa sem colisão de texto
    for b in ALL_BUILDINGS:
        building_node_id = f"BUILDING_{b}"
        vlan_node_id = f"VLAN_BOX_{b}"
        
        # 1. Nó do Prédio (Destino)
        dot.node(building_node_id, f'{b.upper()}', 
                 fillcolor='#43A047', fontcolor='white', shape='rectangle', 
                 style='filled,rounded', width='2.5', height='1.0', fontsize='50')

        vlans = building_vlans[b]
        
        if vlans:
            # \l ao final de cada linha força o alinhamento à esquerda no Graphviz
            stacked_label = "\\l".join(vlans) + "\\l"
            
            # 2. Nó intermediário com fonte maior (fontsize='11')
            dot.node(vlan_node_id, stacked_label, 
                     shape='box', style='filled,rounded', fillcolor='#ECEFF1', 
                     fontcolor='#263238', fontsize='35', bold='true', width='3.5', height='1.5')
            
            # Conexões limpas: CORE -> CAIXA DE VLANs -> PRÉDIO
            dot.edge('CORE', vlan_node_id, arrowhead='none')
            dot.edge(vlan_node_id, building_node_id)
        else:
            # Caso não haja VLANs
            dot.edge('CORE', building_node_id, label="Sem VLANs dedicadas", color='#B0BEC5', fontcolor='#78909C')

    output_filename = dot.render('docs/topologia', format='png', cleanup=True)
    print(f"Topologia gerada com sucesso: {output_filename}")

def generate_html_table():
    csv_path = 'assets/camada2/camada2.csv'
    output_html_path = 'docs/vlans.html'

    if not os.path.exists(csv_path):
        print(f"Aviso: Certifique-se de que o arquivo existe no caminho {csv_path}")
        return

    # Leitura do CSV
    df = pd.read_csv(csv_path)

    # Início do HTML com estilo idêntico à tabela fornecida
    html_content = [
        '<table style="width: 100%; border-collapse: collapse; border: 1px solid #000000; font-family: Arial, sans-serif; font-size: 14px;">',
        '  <thead>',
        '    <tr style="background-color: #f2f2f2;">',
        '      <th style="border: 1px solid #000000; padding: 8px; text-align: center;">VLAN</th>',
        '      <th style="border: 1px solid #000000; padding: 8px; text-align: left;">Nome</th>',
        '      <th style="border: 1px solid #000000; padding: 8px; text-align: left;">Rede Pública</th>',
        '      <th style="border: 1px solid #000000; padding: 8px; text-align: left;">NAT</th>',
        '      <th style="border: 1px solid #000000; padding: 8px; text-align: center;">Prédio</th>',
        '    </tr>',
        '  </thead>',
        '  <tbody>'
    ]

    # Iteração sobre cada linha do CSV
    for idx, row in df.iterrows():
        vlan = str(row['vlan']).strip()
        name = str(row['name']).strip()
        network = str(row['network']).strip()
        nat = str(row['nat']).strip()
        predio = str(row['predio']).strip()

        # Verifica se o prédio é 'none' (insensível a maiúsculas/minúsculas)
        is_none = predio.lower() == 'none' or not predio

        # Aplica o fundo vermelho claro (#ffcdd2) para 'none'
        bg_style = ' background-color: #ffcdd2;' if is_none else ''

        row_html = (
            f'    <tr style="{bg_style}">\n'
            f'      <td style="border: 1px solid #000000; padding: 8px; text-align: center;"><strong>{vlan}</strong></td>\n'
            f'      <td style="border: 1px solid #000000; padding: 8px;">{name}</td>\n'
            f'      <td style="border: 1px solid #000000; padding: 8px;">{network}</td>\n'
            f'      <td style="border: 1px solid #000000; padding: 8px;">{nat}</td>\n'
            f'      <td style="border: 1px solid #000000; padding: 8px; text-align: center;"><strong>{predio}</strong></td>\n'
            f'    </tr>'
        )
        html_content.append(row_html)

    # Fechamento das tags HTML
    html_content.append('  </tbody>')
    html_content.append('</table>')

    # Garante a existência do diretório de saída
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)

    # Escreve o resultado no arquivo HTML
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))

    print(f"Tabela HTML gerada com sucesso em: {output_html_path}")
    
if __name__ == '__main__':
    generate_topology()
    generate_html_table()