FILE=main

.PHONY: clean fast clean

fast:
	lualatex -interaction=nonstopmode -halt-on-error $(FILE).tex 
	lualatex -interaction=nonstopmode -halt-on-error $(FILE).tex
	lualatex -interaction=nonstopmode -halt-on-error $(FILE).tex
	lualatex -interaction=nonstopmode -halt-on-error $(FILE).tex
# sudo apt install tex4ht
#	make4ht -u -f html5+unihtf+mathjax -d versao_html/ main.tex
	make clean
	
clean:
	rm -rf *.aux *.bbl *.toc *.out *.log *.nls *.nlo \
               *.lof *.lot *.blg *.ilg *.synctex.gz *.4ct *.4tc *.dvi *.idv *.lg *.tmp *.xref *.fls *.fdb_latexmk 
	rm -rf */*.aux */*.bbl */*.toc */*.out */*.log   \
               */*.nls */*.nlo */*.lof */*.lot */*.blg */*.ilg */*.synctex.gz */*.4ct */*.4tc */*.dvi */*.idv */*.lg */*.tmp */*.xref */*.fls */*.fdb_latexmk 
