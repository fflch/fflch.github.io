function limparTOCParaExportacao(clone) {
    const toc = clone.querySelector('.toc');
    if (toc) {
        toc.style.background = 'none';
        toc.style.border = 'none';
        toc.style.padding = '0';
        toc.style.margin = '0 0 20px 0';

        const links = toc.querySelectorAll('a');
        links.forEach(a => {
            const span = document.createElement('span');
            span.textContent = a.textContent;
            span.style.color = '#000000';
            span.style.textDecoration = 'none';
            a.parentNode.replaceChild(span, a);
        });

        const uls = toc.querySelectorAll('ul');
        uls.forEach(ul => {
            ul.style.listStyleType = 'disc';
            ul.style.paddingLeft = '20px';
            ul.style.margin = '4px 0';
            ul.style.color = '#000000';
        });
    }
}

function exportarPDF(nomeArquivo) {
    const element = document.getElementById('export-content');
    const clone = element.cloneNode(true);

    const headerClone = clone.querySelector('#header-timbrado-export');
    if (headerClone) {
        headerClone.style.display = 'block';
    }

    limparTOCParaExportacao(clone);

    if (!nomeArquivo) {
        const pathSegments = window.location.pathname.split('/');
        const lastSegment = pathSegments[pathSegments.length - 1] || 'documento.html';
        nomeArquivo = lastSegment.replace(/\.html?$/i, '') + '.pdf';
    }

    const opt = {
        margin:       [10, 10, 10, 10],
        filename:     nomeArquivo,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
    };

    html2pdf().set(opt).from(clone).save();
}

function exportarWord(titulo, nomeArquivo) {
    const element = document.getElementById('export-content');
    const clone = element.cloneNode(true);

    const headerClone = clone.querySelector('#header-timbrado-export');
    if (headerClone) {
        headerClone.style.display = 'block';
    }

    limparTOCParaExportacao(clone);

    if (!titulo) {
        const h1 = clone.querySelector('h1');
        titulo = h1 ? h1.textContent : (document.title || 'Documento');
    }

    if (!nomeArquivo) {
        const pathSegments = window.location.pathname.split('/');
        const lastSegment = pathSegments[pathSegments.length - 1] || 'documento.html';
        nomeArquivo = lastSegment.replace(/\.html?$/i, '') + '.docx';
    }

    const headerHTML = "<html xmlns:o='urn:schemas-microsoft-com:office:office' " +
        "xmlns:w='urn:schemas-microsoft-com:office:word' " +
        "xmlns='http://www.w3.org/TR/REC-html40'>" +
        "<head><meta charset='utf-8'><title>" + titulo + "</title>" +
        "<style>" +
        "body { font-family: Arial, sans-serif; font-size: 11pt; color: #000; }" +
        "table { border-collapse: collapse; width: 100%; }" +
        "td, th { border: 1px solid #ddd; padding: 6px; }" +
        "ul { padding-left: 20px; }" +
        "li { margin-bottom: 3px; }" +
        "pre { background: #f4f4f4; padding: 10px; border-radius: 4px; font-family: Courier New; }" +
        "</style></head><body>";

    const footerHTML = "</body></html>";
    const sourceHTML = headerHTML + clone.innerHTML + footerHTML;

    const blob = new Blob(['\ufeff', sourceHTML], { type: 'application/msword' });
    saveAs(blob, nomeArquivo);
}

