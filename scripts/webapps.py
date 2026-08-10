from graphviz import Digraph

dot = Digraph("mindmap", filename="docs/webapps")

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
dot.attr(
    "edge",
    minlen="2",
    fontsize="22",
    fontcolor="#8B0000",
    color="black",
    penwidth="1",
    fontname="DejaVu Sans Mono"
)

# ===== Nó principal =====
dot.node("webapps", "webapps\n(Thiago)", shape="ellipse", fillcolor="lightblue")

# ===== Filhos diretos =====
dot.attr("node", fillcolor="lightpink")
dot.node("gwmariadb", "gwmariadb\n(Thiago)")
dot.node("minio", "MinIO S3\n(Ricardo)")
dot.node("swarm", "Docker Swarm\n(Ricardo)")
dot.node("nginx", "Nginx Proxy Manager\n(Augusto)")

dot.edge("webapps", "gwmariadb", minlen="3")
dot.edge("webapps", "minio", minlen="3")
dot.edge("webapps", "swarm", minlen="3")
dot.edge("webapps", "nginx", minlen="3")

# ===== Filho de gwmariadb =====
dot.attr("node", fillcolor="lightgreen")
dot.node("galera", "Galera Cluster MariaDB\n(Mônica)")

dot.edge("gwmariadb", "galera")

# ===== Renderização =====
dot.format = "pdf"
dot.render(cleanup=True)

dot.format = "jpg"
dot.render(cleanup=True)