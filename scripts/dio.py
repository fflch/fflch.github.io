import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Garante a criação do diretório docs/files
output_dir = os.path.join("docs", "files")
os.makedirs(output_dir, exist_ok=True)

# Configuração da figura e eixos
fig, ax = plt.subplots(figsize=(16, 10), dpi=200)
ax.set_xlim(0, 160)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor('#F8F9FA')

# Função auxiliar para desenhar o painel do DIO
def draw_dio_panel(ax, x, y, width, height, title, bg_color, border_color):
    # Corpo principal do painel
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.5", 
                                 linewidth=2, edgecolor=border_color, facecolor=bg_color)
    ax.add_patch(rect)
    # Cabeçalho do painel
    header = patches.FancyBboxPatch((x, y + height - 7), width, 7, boxstyle="round,pad=0.2", 
                                     linewidth=1, edgecolor=border_color, facecolor=border_color)
    ax.add_patch(header)
    ax.text(x + width/2, y + height - 3.5, title, color="white", weight="bold", 
            fontsize=10, ha="center", va="center")

# Função auxiliar para desenhar a porta (caixinha)
def draw_port(ax, x, y, size, label, bg_color):
    port = patches.Rectangle((x, y), size, size, linewidth=1.2, edgecolor="#333333", facecolor=bg_color)
    ax.add_patch(port)
    ax.text(x + size/2, y + size/2, label, fontsize=8.5, weight="bold", ha="center", va="center")
    # Retorna as coordenadas exatas: (centro_x, borda_inferior_y, borda_superior_y)
    return (x + size/2, y, y + size)

# --- PROVEDORES EXTERNOS ---
cloud1 = patches.FancyBboxPatch((5, 75), 30, 14, boxstyle="round,pad=0.3", linewidth=1.5, edgecolor="#0288D1", facecolor="#E1F5FE")
ax.add_patch(cloud1)
ax.text(20, 82, "Provedor CETISP", fontsize=9, weight="bold", color="#01579B", ha="center", va="center")

cloud2 = patches.FancyBboxPatch((5, 12), 30, 14, boxstyle="round,pad=0.3", linewidth=1.5, edgecolor="#0288D1", facecolor="#E1F5FE")
ax.add_patch(cloud2)
ax.text(20, 19, "Provedor IPEN", fontsize=9, weight="bold", color="#01579B", ha="center", va="center")

# --- DIO CIÊNCIAS SOCIAIS (12 Portas) ---
draw_dio_panel(ax, 48, 38, 64, 25, "Prédio Ciências Sociais (Sala TR) - DIO 12 Portas", "#FFFFFF", "#1565C0")

cs_ports = {}
for i in range(1, 13):
    px = 50 + (i - 1) * 5.0
    py = 48
    color = "#90CAF9" if i <= 4 else ("#FFCC80" if i <= 8 else "#A5D6A7")
    cs_ports[i] = draw_port(ax, px, py, 4, str(i), color)

# Rótulos dos pares posicionados acima das portas
ax.text(54, 53.5, "CETISP (1, 2)", fontsize=7, ha="center", color="#0D47A1", weight="bold")
ax.text(64, 53.5, "IPEN (3, 4)", fontsize=7, ha="center", color="#0D47A1", weight="bold")
ax.text(74, 53.5, "Letras (5, 6)", fontsize=7, ha="center", color="#E65100", weight="bold")
ax.text(84, 53.5, "Letras (7, 8)", fontsize=7, ha="center", color="#E65100", weight="bold")
ax.text(94, 53.5, "Admin (9, 10)", fontsize=7, ha="center", color="#1B5E20", weight="bold")
ax.text(104, 53.5, "Admin (11, 12)", fontsize=7, ha="center", color="#1B5E20", weight="bold")

# --- DIO LETRAS (4 Portas) ---
draw_dio_panel(ax, 122, 65, 32, 28, "Prédio Letras (TR) - 4 Portas", "#FFFFFF", "#EF6C00")
letras_ports = {}
for i in range(1, 5):
    px = 124 + (i - 1) * 7
    py = 77
    letras_ports[i] = draw_port(ax, px, py, 5, str(i), "#FFCC80")

ax.text(131, 70, "Vindo de CS (1, 2)", fontsize=7.5, ha="center", color="#E65100", weight="bold")
ax.text(145, 70, "Vindo de CS (3, 4)", fontsize=7.5, ha="center", color="#E65100", weight="bold")

# --- DIO ADMINISTRAÇÃO (4 Portas) ---
draw_dio_panel(ax, 122, 7, 32, 28, "Prédio Admin (TR) - 4 Portas", "#FFFFFF", "#2E7D32")
admin_ports = {}
for i in range(1, 5):
    px = 124 + (i - 1) * 7
    py = 19
    admin_ports[i] = draw_port(ax, px, py, 5, str(i), "#A5D6A7")

ax.text(131, 12, "Vindo de CS (1, 2)", fontsize=7.5, ha="center", color="#1B5E20", weight="bold")
ax.text(145, 12, "Vindo de CS (3, 4)", fontsize=7.5, ha="center", color="#1B5E20", weight="bold")

# --- CABEAMENTO ORTOGONAL PERFEITAMENTE ALINHADO ÀS PORTAS ---

# 1. CETISP -> CS Portas 1 e 2 (Entram pela borda inferior da caixinha)
ax.plot([35, 43, 43, cs_ports[1][0]], [83, 83, 44, 44], color="#0288D1", lw=1.8)
ax.plot([cs_ports[1][0], cs_ports[1][0]], [44, cs_ports[1][1]], color="#0288D1", lw=1.8)
ax.plot([cs_ports[1][0]], [cs_ports[1][1]], marker="^", color="#0288D1", ms=4)

ax.plot([35, 45, 45, cs_ports[2][0]], [80, 80, 42, 42], color="#0288D1", lw=1.8)
ax.plot([cs_ports[2][0], cs_ports[2][0]], [42, cs_ports[2][1]], color="#0288D1", lw=1.8)
ax.plot([cs_ports[2][0]], [cs_ports[2][1]], marker="^", color="#0288D1", ms=4)

# 2. IPEN -> CS Portas 3 e 4 (Entram diretamente na borda inferior da caixinha)
ax.plot([35, 43, 43, cs_ports[3][0]], [20, 20, 28, 28], color="#0288D1", lw=1.8)
ax.plot([cs_ports[3][0], cs_ports[3][0]], [28, cs_ports[3][1]], color="#0288D1", lw=1.8)
ax.plot([cs_ports[3][0]], [cs_ports[3][1]], marker="^", color="#0288D1", ms=4)

ax.plot([35, 45, 45, cs_ports[4][0]], [17, 17, 26, 26], color="#0288D1", lw=1.8)
ax.plot([cs_ports[4][0], cs_ports[4][0]], [26, cs_ports[4][1]], color="#0288D1", lw=1.8)
ax.plot([cs_ports[4][0]], [cs_ports[4][1]], marker="^", color="#0288D1", ms=4)

# 3. CS Portas 5-8 -> LETRAS Portas 1-4 (Saem pelo topo da caixinha de CS e entram na base da caixinha de Letras)
offsets_letras = [letras_ports[1][0], letras_ports[2][0], letras_ports[3][0], letras_ports[4][0]]
heights_letras = [88, 90, 92, 94]

for idx, p_num in enumerate([5, 6, 7, 8]):
    target_x = offsets_letras[idx]
    h = heights_letras[idx]
    # Sobe de CS -> Vai na horizontal -> Desce diretamente para a caixinha de Letras
    ax.plot([cs_ports[p_num][0], cs_ports[p_num][0], target_x, target_x], 
            [cs_ports[p_num][2], h, h, letras_ports[idx+1][2] + 7], 
            color="#EF6C00" if idx<2 else "#E65100", lw=1.8)
    ax.plot([target_x, target_x], [letras_ports[idx+1][2] + 7, letras_ports[idx+1][2]], 
            color="#EF6C00" if idx<2 else "#E65100", lw=1.8)
    ax.plot([target_x], [letras_ports[idx+1][2]], marker="v", color="#EF6C00" if idx<2 else "#E65100", ms=4)

# 4. CS Portas 9-12 -> ADMIN Portas 1-4 (Saem pela base da caixinha de CS e entram na base da caixinha de Admin)
offsets_admin = [admin_ports[1][0], admin_ports[2][0], admin_ports[3][0], admin_ports[4][0]]
heights_admin = [2, 4, 6, 8]

for idx, p_num in enumerate([9, 10, 11, 12]):
    target_x = offsets_admin[idx]
    h = heights_admin[idx]
    # Desce de CS -> Vai na horizontal -> Sobe diretamente para a caixinha de Admin
    ax.plot([cs_ports[p_num][0], cs_ports[p_num][0], target_x, target_x], 
            [cs_ports[p_num][1], h, h, admin_ports[idx+1][1]], 
            color="#2E7D32" if idx<2 else "#1B5E20", lw=1.8)
    ax.plot([target_x], [admin_ports[idx+1][1]], marker="^", color="#2E7D32" if idx<2 else "#1B5E20", ms=4)

plt.title("Diagrama de Conexões entre DIOs com Linhas Alinhadas às Portas", fontsize=14, weight="bold", pad=20)

file_path = os.path.join(output_dir, "dio.png")
plt.savefig(file_path, bbox_inches="tight")
plt.close()

print(f"Diagrama atualizado salvo em: {file_path}")