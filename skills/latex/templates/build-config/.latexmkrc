# Robust .latexmkrc — auto-detects engine, builds to out/, copies PDF back to source.
# Works with: pdflatex, xelatex, lualatex; terminal latexmk; VS Code LaTeX Workshop (with -cd).
# Canonical source: Task-Management/templates/latexmkrc/.latexmkrc
$out_dir = 'out';

# Engine commands (latexmk picks one based on $pdf_mode below)
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$xelatex  = 'xelatex  -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';

# Auto-detect: lualatex if luacode/lua-ul/luamplib, xelatex if fontspec, else pdflatex.
sub detect_engine {
    my ($file, $seen) = @_;
    $seen //= {};
    return 0 if $seen->{$file}++;
    my $fp = -e $file ? $file : -e "$file.tex" ? "$file.tex" : return 0;
    open(my $fh, '<', $fp) or return 0;
    my $dir = $fp =~ s|/[^/]*$||r; $dir = '.' if $dir eq $fp;
    my $found = 0;
    while (<$fh>) {
        if (/\\usepackage(?:\[[^\]]*\])?\{(?:luacode|lua-ul|luamplib)\}/) { $found = 4; last; }
        if (/\\usepackage(?:\[[^\]]*\])?\{fontspec\}/ && !$found)         { $found = 5; }
        if (/\\(?:input|include)\{([^}]+)\}/) {
            my $sub = $1; $sub = "$dir/$sub" unless $sub =~ m|^/|;
            my $r = detect_engine($sub, $seen);
            if ($r == 4) { $found = 4; last; }
            $found = $r if $r && !$found;
        }
    }
    close($fh);
    return $found;
}

$pdf_mode = 1;  # default: pdflatex
foreach my $file (@ARGV) {
    my $m = detect_engine($file);
    if ($m) { $pdf_mode = $m; last; }
}

# Copy compiled PDF back to source directory
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
