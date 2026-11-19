.PHONY: all render check check-demos downloads preview clean

all: render

render: downloads
	quarto render
	@touch docs/.nojekyll
	python3 tools/check_site.py

check: check-demos
	Rscript --vanilla tools/check_carbonate.R
	Rscript --vanilla tools/check_course.R

check-demos:
	node --test demos/tests/*.test.cjs

downloads:
	python3 tools/package_downloads.py

preview:
	quarto preview

clean:
	rm -rf docs .quarto
