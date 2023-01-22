default:	Cours_1.pdf Cours_2.pdf Cours_3.pdf Cours_4.pdf

Cours_1.pdf:	Cours_1.tex
	pdflatex -shell-escape Cours_1.tex

Cours_2.pdf:	Cours_2.tex
	pdflatex -shell-escape Cours_2.tex

Cours_3.pdf:	Cours_3.tex
	pdflatex -shell-escape Cours_3.tex

Cours_4.pdf:	Cours_4.tex
	pdflatex -shell-escape Cours_4.tex

clean:
	rm -fr *.vrb *.toc *.aux *.log *~ *.out *latexmk *.snm _minted* *.nav

cleanall:	clean
	rm *.pdf




