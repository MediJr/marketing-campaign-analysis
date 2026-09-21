# Rapport LaTeX — Analyse des performances des campagnes marketing

Copie de travail du template [sikatikenmogne/latex-report-template](https://github.com/sikatikenmogne/latex-report-template) (licence MIT). Le dépôt amont n'est pas modifié.

## Compilation

Depuis ce dossier :

```bash
python scripts/check.py
python scripts/compile.py
```

Le PDF de compilation se trouve dans `build/main.pdf`. Le livrable nommé est `rapport_analyse_marketing.pdf`.

Compilateur attendu : pdfLaTeX + Biber.

## Contenu

- `main.tex` — document principal
- `config/` — métadonnées, couleurs, style, packages
- `content/chapters/` — chapitres du projet
- `content/frontmatter/titlepage.tex` — page de garde
- `content/backmatter/bibliography.bib` — bibliographie
- `assets/images/charts/` — visualisations Matplotlib du projet
- `internshipreport.cls` — classe du template
