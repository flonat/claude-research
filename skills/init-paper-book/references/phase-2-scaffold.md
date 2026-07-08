# Phase 2: Scaffold

```bash
mkdir -p ~/vault/books/"$SLUG"/figures
cp "$BIB" ~/vault/books/"$SLUG"/references.bib

# Copy ONLY paper-cited figures. Inspect tex for \includegraphics{...} paths,
# resolve them, then copy or convert as needed:
# - if a .png exists at that path, copy directly
# - if only a .pdf exists (common in NeurIPS/ACM submissions), convert to
#   .png via pdftoppm so atlas can serve to browsers (PNG/SVG/WebP only)
grep -oE '\\includegraphics(\[[^]]*\])?\{[^}]+\}' "$PAPER_TEX" \
  | grep -oE '\{[^}]+\}' | tr -d '{}' \
  | while read -r fig; do
      # Resolve to absolute path (project_path-relative or absolute)
      [[ "$fig" == /* ]] && src="$fig" || src="$PROJECT_PATH/$fig"
      base=$(basename "$fig" | sed 's/\.[^.]*$//')  # strip extension
      out=~/vault/books/"$SLUG"/figures/"$base"
      # Search for png anywhere — paper tex includes might omit extension or
      # point to PDF while a PNG twin lives elsewhere in the project tree.
      png_src=$(find "$PROJECT_PATH" -name "${base}.png" -type f 2>/dev/null | head -1)
      if [[ -n "$png_src" ]]; then
          cp "$png_src" "${out}.png"
          continue
      fi
      # Fall back to PDF → PNG conversion via pdftoppm (poppler)
      pdf_src=$(find "$PROJECT_PATH" -name "${base}.pdf" -type f 2>/dev/null | head -1)
      if [[ -n "$pdf_src" ]] && command -v pdftoppm >/dev/null; then
          pdftoppm -png -r 150 "$pdf_src" "$out" 2>/dev/null
          # pdftoppm appends `-1` (or `-01` for ≥10-page docs) per page; flatten
          mv "${out}-1.png" "${out}.png" 2>/dev/null \
            || mv "${out}-01.png" "${out}.png" 2>/dev/null
      fi
    done
```

**Note on PNG vs PDF.** Atlas serves files as-is via FileResponse, but browsers can't render PDF inline as a `<figure>` image — only PNG/SVG/WebP/JPG. Always end with `.png` files in the vault `figures/` dir; never publish a `.pdf` figure expecting it to render.
