.PHONY: all render check preview clean

all: render

render:
	quarto render
	@touch docs/.nojekyll

check:
	Rscript --vanilla tools/check_carbonate.R

preview:
	quarto preview

clean:
	rm -rf docs .quarto
