/*
 * Diagrama interativo de fibras entre prédios (DIOs).
 * Dados: <script id="dio-dados"> gerado por scripts/dio.py a partir de content/dio.csv.
 *
 * Prédio → TRs → racks → DIOs (retângulo com os pares/blocos em sequência). Cada ligação é
 * ponto a ponto: sai por baixo do par, corre numa "calha" e chega ao par do outro lado.
 * Feito para centenas de ligações: calhas compactadas (ligações que não se sobrepõem
 * dividem a mesma calha), zoom, busca, filtro por prédio e destaque ao passar o mouse.
 */
(function () {
    var app = document.getElementById("dio-app");
    var fonte = document.getElementById("dio-dados");
    if (!app || !fonte) return;
    var D = JSON.parse(fonte.textContent);
    var CORES = ["#2a78d6", "#e0832a", "#2e9d4f", "#c2417a", "#7a5cd6", "#0f9aa8", "#b8860b", "#d93a3a",
                 "#5b8c2a", "#a0522d", "#3b5bdb", "#d6336c"];
    var SVGNS = "http://www.w3.org/2000/svg";
    var GAP = 6;          // distância entre calhas
    var MARGEM = 5;       // folga horizontal entre ligações na mesma calha

    function esc(s) {
        return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }
    function norm(s) { return String(s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
    // "1" → "TR 1"; "ER-A-ADM" fica como está. Rack/DIO: prefixa se ainda não começar com o prefixo.
    function rotulo(prefixo, nome, soNumero) {
        nome = String(nome || "").trim();
        if (!nome) return prefixo;
        if (soNumero) return /^\d+$/.test(nome) ? prefixo + " " + nome : nome;
        return norm(nome).indexOf(norm(prefixo)) === 0 ? nome : prefixo + " " + nome;
    }
    function chavePar(p) {
        return p.externo ? "ext|" + p.predio : [p.predio, p.tr, p.rack, p.dio, p.par].join("|");
    }
    function descreve(p) {
        if (p.externo) return p.predio;
        return [p.predio, rotulo("TR", p.tr, true), rotulo("Rack", p.rack), rotulo("DIO", p.dio), "bloco " + p.par].join(" · ");
    }

    // ---------------- ordem dos prédios: o mais conectado no centro, externos nas pontas ----------------
    var grau = {};
    D.predios.forEach(function (p) { grau[p.nome] = 0; });
    D.ligacoes.forEach(function (l) { grau[l.a.predio]++; if (l.b.predio !== l.a.predio) grau[l.b.predio]++; });
    function porGrau(a, b) { return (grau[b.nome] - grau[a.nome]) || a.nome.localeCompare(b.nome); }
    var internos = D.predios.filter(function (p) { return !p.externo; }).sort(porGrau);
    var externos = D.predios.filter(function (p) { return p.externo; }).sort(porGrau);
    var meio = [];
    internos.forEach(function (p, i) { if (i % 2) meio.unshift(p); else meio.push(p); });
    var ordem = [];
    externos.forEach(function (p, i) { if (i % 2) ordem.push(p); else ordem.unshift(p); });
    var corte = Math.ceil(ordem.length / 2);
    ordem = ordem.slice(0, corte).concat(meio, ordem.slice(corte));

    // ---------------- cor por dupla de prédios ----------------
    var corDupla = {}, nCores = 0;
    D.ligacoes.forEach(function (l, i) {
        var k = [l.a.predio, l.b.predio].sort().join("⇄");
        if (!(k in corDupla)) corDupla[k] = CORES[nCores++ % CORES.length];
        l.cor = corDupla[k];
        l.i = i;
        l.texto = norm(descreve(l.a) + " " + descreve(l.b));
    });
    var ligPorPar = {};
    D.ligacoes.forEach(function (l) {
        [l.a, l.b].forEach(function (p) { (ligPorPar[chavePar(p)] = ligPorPar[chavePar(p)] || []).push(l.i); });
    });

    // ---------------- HTML ----------------
    function htmlPar(predio, tr, rack, dio, n) {
        var k = [predio, tr, rack, dio, n].join("|"), ls = ligPorPar[k] || [];
        var cor = ls.length ? D.ligacoes[ls[0]].cor : "";
        return '<span class="dio-par' + (ls.length ? " usado" : "") + '" data-par="' + esc(k) + '"'
            + (cor ? ' style="--cor:' + cor + '"' : "") + ' title="bloco ' + n + (ls.length ? "" : " (livre)") + '">' + n + "</span>";
    }
    function htmlPredio(p) {
        var h = '<section class="dio-predio' + (p.externo ? " externo" : "") + '" data-predio="' + esc(p.nome) + '">'
            + '<header title="Clique para filtrar por este prédio"><span class="dio-nome">' + (p.externo ? "🌐 " : "🏢 ") + esc(p.nome) + "</span>"
            + '<span class="dio-cont">' + grau[p.nome] + " ligaç" + (grau[p.nome] === 1 ? "ão" : "ões") + "</span></header>";
        if (p.externo || !p.trs.length) {
            h += '<div class="dio-externo" data-par="' + esc("ext|" + p.nome) + '">ponto externo</div>';
        }
        p.trs.forEach(function (tr) {
            h += '<div class="dio-tr"><div class="dio-rot">' + esc(rotulo("TR", tr.nome, true)) + '</div><div class="dio-racks">';
            tr.racks.forEach(function (rk) {
                h += '<div class="dio-rack"><div class="dio-rot">' + esc(rotulo("Rack", rk.nome)) + "</div>";
                rk.dios.forEach(function (d) {
                    h += '<div class="dio-dio"><div class="dio-dio-cab"><span>' + esc(rotulo("DIO", d.nome)) + "</span><small>"
                        + d.pares + " bloco" + (d.pares === 1 ? "" : "s") + '</small></div><div class="dio-portas">';
                    for (var n = 1; n <= d.pares; n++) h += htmlPar(p.nome, tr.nome, rk.nome, d.nome, n);
                    h += "</div></div>";
                });
                h += "</div>";
            });
            h += "</div></div>";
        });
        return h + "</section>";
    }

    app.innerHTML =
        '<div class="dio-barra">'
        + '<label>Prédio <select id="dio-filtro"><option value="">todos</option>'
        + D.predios.slice().sort(function (a, b) { return a.nome.localeCompare(b.nome); }).map(function (p) {
            return '<option value="' + esc(p.nome) + '">' + esc(p.nome) + "</option>"; }).join("")
        + "</select></label>"
        + '<input type="search" id="dio-busca" placeholder="buscar (prédio, rack, DIO, bloco…)" aria-label="Buscar ligações">'
        + '<span class="dio-zoom"><button type="button" data-zoom="-" title="Diminuir">−</button>'
        + '<span id="dio-zoom-v">100%</span><button type="button" data-zoom="+" title="Aumentar">+</button>'
        + '<button type="button" data-zoom="ajustar" title="Caber na largura">ajustar</button></span>'
        + '<span class="dio-dica">Passe o mouse num bloco ou linha para destacar · clique para fixar · clique no nome do prédio para filtrar</span></div>'
        + '<div class="dio-canvas" id="dio-canvas"><div class="dio-sizer" id="dio-sizer"><div class="dio-stage" id="dio-stage">'
        + '<svg class="dio-svg" id="dio-svg" aria-hidden="true"></svg>'
        + '<div class="dio-predios">' + ordem.map(htmlPredio).join("") + "</div></div></div></div>"
        + '<div class="dio-tip" id="dio-tip" role="status"></div>'
        + '<details class="dio-tabela"><summary>Ligações (<span id="dio-n">' + D.ligacoes.length + "</span>)</summary>"
        + '<table><thead><tr><th>Ponta A</th><th></th><th>Ponta B</th></tr></thead><tbody>'
        + D.ligacoes.map(function (l) {
            return '<tr data-lig="' + l.i + '"><td>' + esc(descreve(l.a)) + '</td><td><span class="dio-bola" style="background:'
                + l.cor + '"></span></td><td>' + esc(descreve(l.b)) + "</td></tr>";
        }).join("") + "</tbody></table></details>";

    var canvas = document.getElementById("dio-canvas"), sizer = document.getElementById("dio-sizer");
    var stage = document.getElementById("dio-stage"), svg = document.getElementById("dio-svg");
    var tip = document.getElementById("dio-tip"), filtro = document.getElementById("dio-filtro");
    var busca = document.getElementById("dio-busca");
    var fixada = null, ativa = null, filtroPredio = "", termo = "", escala = 1, ajustarAuto = true;

    var porChave = {};
    stage.querySelectorAll("[data-par]").forEach(function (e) { porChave[e.dataset.par] = e; });

    // ---------------- linhas ----------------
    function caixa(e, base) {
        var r = e.getBoundingClientRect();
        return { l: (r.left - base.left) / escala, r: (r.right - base.left) / escala,
                 t: (r.top - base.top) / escala, b: (r.bottom - base.top) / escala,
                 x: (r.left - base.left + r.width / 2) / escala };
    }
    function arredondado(pts, raio) {
        var d = "M" + pts[0][0] + "," + pts[0][1];
        for (var i = 1; i < pts.length - 1; i++) {
            var p0 = pts[i - 1], p1 = pts[i], p2 = pts[i + 1];
            var l1 = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), l2 = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]);
            var rr = Math.min(raio, l1 / 2, l2 / 2);
            if (!rr) { d += " L" + p1[0] + "," + p1[1]; continue; }
            var a = [p1[0] + (p0[0] - p1[0]) * rr / l1, p1[1] + (p0[1] - p1[1]) * rr / l1];
            var c = [p1[0] + (p2[0] - p1[0]) * rr / l2, p1[1] + (p2[1] - p1[1]) * rr / l2];
            d += " L" + a[0] + "," + a[1] + " Q" + p1[0] + "," + p1[1] + " " + c[0] + "," + c[1];
        }
        var u = pts[pts.length - 1];
        return d + " L" + u[0] + "," + u[1];
    }
    // empacota intervalos [ini, fim] em calhas: o menor índice de calha livre para cada um
    function empacotar(rotas, ini, fim) {
        var calhas = [];
        rotas.sort(function (x, y) { return (fim(x) - ini(x)) - (fim(y) - ini(y)); });
        rotas.forEach(function (r) {
            var a = ini(r) - MARGEM, b = fim(r) + MARGEM, k = 0;
            while (calhas[k] && calhas[k].some(function (iv) { return a < iv[1] && iv[0] < b; })) k++;
            (calhas[k] = calhas[k] || []).push([a, b]);
            r.calha = k;
        });
        return calhas.length;
    }
    // Medidas (posições de blocos e prédios) são refeitas só quando o layout muda;
    // as rotas são refeitas a cada filtro/busca, só para as ligações visíveis.
    var LIMITE = 60;      // acima disso, sem filtro, mostra troncos por dupla de prédios
    var med = null, dupla = "";
    function medir() {
        stage.style.transform = "none";
        var base = stage.getBoundingClientRect();
        escala = 1;
        med = { par: {}, predio: {}, fundo: 0, direita: 0 };
        Object.keys(porChave).forEach(function (k) {
            var e = porChave[k];
            med.par[k] = caixa(e, base);
            med.par[k].predio = e.closest(".dio-predio").dataset.predio;
        });
        stage.querySelectorAll(".dio-predio").forEach(function (s) {
            var c = caixa(s, base);
            med.predio[s.dataset.predio] = c;
            med.fundo = Math.max(med.fundo, c.b);
            med.direita = Math.max(med.direita, c.r);
        });
        med.larg = stage.scrollWidth;
    }
    function lado(ca, cb) { return ca === cb || ca.r <= cb.l || cb.r <= ca.l; }
    function caminho(pa, pb, horizontal, calha) {
        if (horizontal) {
            var y = med.fundo + 16 + calha * GAP;
            return { pts: [[pa.x, pa.b], [pa.x, y], [pb.x, y], [pb.x, pb.b]], y: y };
        }
        var x = med.direita + 16 + calha * GAP, s = 5 + (calha % 3) * 3;
        return { pts: [[pa.x, pa.b], [pa.x, pa.b + s], [x, pa.b + s], [x, pb.b + s], [pb.x, pb.b + s], [pb.x, pb.b]], x: x };
    }
    function grupoSvg(cls, attrs, d, cor, pts, largura) {
        var g = document.createElementNS(SVGNS, "g");
        g.setAttribute("class", cls);
        Object.keys(attrs).forEach(function (k) { g.setAttribute(k, attrs[k]); });
        g.innerHTML = '<path class="hit" d="' + d + '"></path><path class="linha" d="' + d + '" stroke="' + cor + '"'
            + (largura ? ' style="stroke-width:' + largura + 'px"' : "") + "></path>"
            + '<circle cx="' + pts[0][0] + '" cy="' + pts[0][1] + '" r="2.6" fill="' + cor + '"></circle>'
            + '<circle cx="' + pts[pts.length - 1][0] + '" cy="' + pts[pts.length - 1][1] + '" r="2.6" fill="' + cor + '"></circle>';
        return g;
    }
    function modoDetalhe() { return !!(filtroPredio || termo || dupla) || D.ligacoes.length <= LIMITE; }

    function rotear() {
        if (!med) medir();
        var frag = document.createDocumentFragment(), maxY = med.fundo, maxX = med.direita;
        var detalhe = modoDetalhe(), foco = ativa !== null ? ativa : fixada;
        var lista = D.ligacoes.filter(function (l) { return detalhe ? visivel(l) : l.i === foco; });
        var rotas = [];
        lista.forEach(function (l) {
            var pa = med.par[chavePar(l.a)], pb = med.par[chavePar(l.b)];
            if (!pa || !pb) return;
            rotas.push({ l: l, pa: pa, pb: pb, horizontal: lado(med.predio[pa.predio], med.predio[pb.predio]) });
        });
        var troncos = [];
        if (!detalhe) {
            // um tronco por dupla de prédios, saindo de pontos distribuídos na base de cada prédio
            var porDupla = {};
            D.ligacoes.forEach(function (l) {
                if (l.a.predio === l.b.predio) return;
                var k = [l.a.predio, l.b.predio].sort().join("⇄");
                (porDupla[k] = porDupla[k] || { a: k.split("⇄")[0], b: k.split("⇄")[1], n: 0, cor: l.cor, k: k }).n++;
            });
            troncos = Object.keys(porDupla).map(function (k) { return porDupla[k]; });
            var saidas = {};
            troncos.forEach(function (t) {
                [[t.a, t.b], [t.b, t.a]].forEach(function (par) { (saidas[par[0]] = saidas[par[0]] || []).push({ t: t, outro: par[1] }); });
            });
            Object.keys(saidas).forEach(function (nome) {
                var c = med.predio[nome], lista2 = saidas[nome];
                lista2.sort(function (x, y) { return med.predio[x.outro].x - med.predio[y.outro].x; });
                lista2.forEach(function (s, i) {
                    var x = c.l + (c.r - c.l) * (0.15 + 0.7 * (lista2.length === 1 ? 0.5 : i / (lista2.length - 1)));
                    s.t[s.t.a === nome ? "pa" : "pb"] = { x: x, b: c.b, predio: nome };
                });
            });
            troncos.forEach(function (t) { rotas.push({ tronco: t, pa: t.pa, pb: t.pb, horizontal: lado(med.predio[t.a], med.predio[t.b]) }); });
        }
        var hs = rotas.filter(function (r) { return r.horizontal; }), vs = rotas.filter(function (r) { return !r.horizontal; });
        var GAPT = detalhe ? GAP : 9;
        var gapAntes = GAP; GAP = GAPT;
        empacotar(hs, function (r) { return Math.min(r.pa.x, r.pb.x); }, function (r) { return Math.max(r.pa.x, r.pb.x); });
        empacotar(vs, function (r) { return Math.min(r.pa.b, r.pb.b); }, function (r) { return Math.max(r.pa.b, r.pb.b); });
        rotas.forEach(function (r) {
            var c = caminho(r.pa, r.pb, r.horizontal, r.calha), d = arredondado(c.pts, 7);
            if (c.y) maxY = Math.max(maxY, c.y); if (c.x) maxX = Math.max(maxX, c.x);
            if (r.tronco) {
                var t = r.tronco, larg = Math.min(9, 2 + Math.log2(t.n + 1) * 1.6);
                var g = grupoSvg("dio-lig dio-tronco", { "data-dupla": t.k }, d, t.cor, c.pts, larg);
                var mx = (c.pts[1][0] + c.pts[2][0]) / 2, my = c.pts[1][1];
                if (!r.horizontal) { mx = c.pts[2][0]; my = (c.pts[2][1] + c.pts[3][1]) / 2; }
                g.innerHTML += '<g class="dio-rot-tronco" transform="translate(' + mx + "," + my + ')"><rect x="-13" y="-8" width="26" height="16" rx="8" fill="'
                    + t.cor + '"></rect><text text-anchor="middle" dy="4">' + t.n + "</text></g>"
                    + "<title>" + esc(t.a + " ⇄ " + t.b + ": " + t.n + " ligaç" + (t.n === 1 ? "ão" : "ões") + " — clique para ver as fibras") + "</title>";
                frag.appendChild(g);
            } else {
                frag.appendChild(grupoSvg("dio-lig", { "data-lig": r.l.i }, d, r.l.cor, c.pts));
            }
        });
        GAP = gapAntes;
        svg.innerHTML = "";
        svg.appendChild(frag);
        app.classList.toggle("dio-resumo", !detalhe);

        var larg = Math.max(med.larg, maxX + 12), alt = maxY + 14;
        stage.style.paddingBottom = Math.max(0, alt - stage.querySelector(".dio-predios").offsetHeight) + "px";
        svg.setAttribute("width", larg);
        svg.setAttribute("height", alt);
        stage.dataset.w = larg;
        stage.dataset.h = alt;
        if (ajustarAuto) escala = Math.max(0.6, Math.min(1, (canvas.clientWidth - 8) / larg));   // abaixo de 60%: rolar
        aplicarEscala();
    }
    function desenhar() { med = null; rotear(); aplicarEstado(); }
    function aplicarEscala() {
        stage.dataset.escala = escala;
        stage.style.transform = escala === 1 ? "none" : "scale(" + escala + ")";
        sizer.style.width = (+stage.dataset.w * escala) + "px";
        sizer.style.height = (+stage.dataset.h * escala) + "px";
        document.getElementById("dio-zoom-v").textContent = Math.round(escala * 100) + "%";
    }
    // ---------------- destaque / filtro / busca ----------------
    function visivel(l) {
        if (filtroPredio && l.a.predio !== filtroPredio && l.b.predio !== filtroPredio) return false;
        if (dupla && [l.a.predio, l.b.predio].sort().join("⇄") !== dupla) return false;
        if (termo && l.texto.indexOf(termo) < 0) return false;
        return true;
    }
    function aplicarEstado() {
        var foco = ativa !== null ? ativa : fixada;
        var filtrando = !!(filtroPredio || termo || dupla);
        app.classList.toggle("dio-foco", foco !== null);
        var vis = {}, nVis = 0, predVis = {};
        D.ligacoes.forEach(function (l) {
            if (visivel(l)) { vis[l.i] = true; nVis++; predVis[l.a.predio] = predVis[l.b.predio] = true; }
        });
        svg.querySelectorAll(".dio-lig[data-lig]").forEach(function (g) {
            var i = +g.dataset.lig;
            g.classList.toggle("oculta", !vis[i]);
            g.classList.toggle("ativa", foco === i);
        });
        if (foco !== null) { var ga = svg.querySelector('.dio-lig[data-lig="' + foco + '"]'); if (ga) svg.appendChild(ga); }
        stage.querySelectorAll("[data-par]").forEach(function (e) {
            var ls = ligPorPar[e.dataset.par] || [];
            e.classList.toggle("ativa", foco !== null && ls.indexOf(foco) >= 0);
            e.classList.toggle("fora", filtrando && ls.length > 0 && !ls.some(function (i) { return vis[i]; }));
        });
        stage.querySelectorAll(".dio-predio").forEach(function (s) {
            s.classList.toggle("apagado", filtrando && !predVis[s.dataset.predio]);
        });
        app.querySelectorAll("tr[data-lig]").forEach(function (tr) {
            var i = +tr.dataset.lig;
            tr.hidden = !vis[i];
            tr.classList.toggle("ativa", foco === i);
        });
        document.getElementById("dio-n").textContent = filtrando ? nVis + " de " + D.ligacoes.length : D.ligacoes.length;
        if (foco !== null) {
            var l = D.ligacoes[foco];
            tip.innerHTML = '<span class="dio-bola" style="background:' + l.cor + '"></span> ' + esc(descreve(l.a))
                + " <b>⇄</b> " + esc(descreve(l.b)) + (fixada === foco ? " <small>(fixada — clique fora para soltar)</small>" : "");
            tip.classList.add("visivel");
        } else {
            tip.innerHTML = filtrando
                ? nVis + " ligação(ões) no filtro" + (dupla ? " · " + esc(dupla) + ' <button type="button" class="dio-limpar">mostrar tudo</button>' : "")
                : (modoDetalhe() ? "" : D.ligacoes.length + " ligações: mostrando um tronco por dupla de prédios — clique num tronco, escolha um prédio ou busque para ver as fibras");
            tip.classList.toggle("visivel", !!tip.innerHTML);
        }
    }
    function ligDoAlvo(t) {
        var g = t.closest && t.closest("[data-lig]");
        if (g) return +g.dataset.lig;
        var p = t.closest && t.closest("[data-par]");
        if (p && ligPorPar[p.dataset.par]) return ligPorPar[p.dataset.par][0];
        return null;
    }
    function atualizar() { if (!modoDetalhe()) rotear(); aplicarEstado(); }
    app.addEventListener("mouseover", function (e) {
        var i = ligDoAlvo(e.target);
        if (i !== ativa) { ativa = i; atualizar(); }
    });
    app.addEventListener("mouseleave", function () { ativa = null; atualizar(); });
    app.addEventListener("click", function (e) {
        if (e.target.closest("select, input, summary, .dio-zoom")) return;
        if (e.target.closest(".dio-limpar")) { dupla = ""; filtroPredio = ""; filtro.value = ""; termo = ""; busca.value = ""; fixada = null; rotear(); aplicarEstado(); return; }
        var tr = e.target.closest && e.target.closest("[data-dupla]");
        if (tr) { dupla = tr.dataset.dupla; fixada = null; ativa = null; rotear(); aplicarEstado(); return; }
        var h = e.target.closest(".dio-predio header");
        if (h) {
            var nome = h.parentNode.dataset.predio;
            filtroPredio = filtroPredio === nome ? "" : nome;
            filtro.value = filtroPredio;
            dupla = "";
            fixada = null;
            rotear();
            aplicarEstado();
            return;
        }
        var i = ligDoAlvo(e.target);
        fixada = (i === null || i === fixada) ? null : i;
        ativa = null;
        atualizar();
    });
    filtro.addEventListener("change", function () { filtroPredio = filtro.value; dupla = ""; fixada = null; rotear(); aplicarEstado(); });
    var tBusca;
    busca.addEventListener("input", function () {
        clearTimeout(tBusca);
        tBusca = setTimeout(function () { termo = norm(busca.value.trim()); fixada = null; rotear(); aplicarEstado(); }, 150);
    });
    app.querySelector(".dio-zoom").addEventListener("click", function (e) {
        var z = e.target.dataset && e.target.dataset.zoom;
        if (!z) return;
        if (z === "ajustar") { ajustarAuto = true; rotear(); return; }
        ajustarAuto = false;
        escala = Math.max(0.3, Math.min(2, Math.round((escala + (z === "+" ? 0.1 : -0.1)) * 10) / 10));
        aplicarEscala();
    });

    var larguraAnterior = 0;
    function aoRedimensionar() {
        if (canvas.clientWidth === larguraAnterior) return;
        larguraAnterior = canvas.clientWidth;
        desenhar();
    }
    desenhar();
    if (window.ResizeObserver) new ResizeObserver(aoRedimensionar).observe(canvas);
    else window.addEventListener("resize", aoRedimensionar);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(desenhar);
})();
