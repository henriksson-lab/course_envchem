.PHONY: all render check downloads preview clean

all: render

render: downloads
	quarto render
	@touch docs/.nojekyll
	python3 tools/check_site.py

check:
	Rscript --vanilla tools/check_carbonate.R
	Rscript --vanilla tools/check_course.R

downloads:
	python3 tools/package_downloads.py

preview:
	quarto preview

clean:
	rm -rf docs .quarto
