@default_files = ('main.tex');
$out_dir = 'out';
$pdflatex = 'lualatex -interaction=nonstopmode -halt-on-error %O %S';
$pdf_mode = 4;
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
