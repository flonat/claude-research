# Spatial Organization Strategies

> Header, content area, and footer layout strategies with sizing guidelines and LaTeX implementations.
> See also: [poster_layout_grids.md](poster_layout_grids.md) for grid systems.

## Spatial Organization Strategies

### Header/Title Area

**Typical Size**: 10-15% of total poster height

**Essential Elements**:
- **Title**: Concise, descriptive (10-15 words max)
- **Authors**: Full names, presenting author emphasized
- **Affiliations**: Institutions, departments
- **Logos**: University, funding agencies (2-4 max)
- **Conference info** (optional): Name, date, location

**Layout Options**:

**Centered**:
```
+----------------------------------------+
|  [Logo]    POSTER TITLE HERE    [Logo]|
|         Authors and Affiliations       |
|           email@university.edu         |
+----------------------------------------+
```

**Left-aligned**:
```
+----------------------------------------+
| POSTER TITLE HERE            [Logo]   |
| Authors and Affiliations     [Logo]   |
+----------------------------------------+
```

**Split**:
```
+----------------------------------------+
| [Logo]           | Authors & Affil.    |
| POSTER TITLE     | email@edu          |
|                  | [QR Code]          |
+----------------------------------------+
```

**LaTeX Header (beamerposter)**:
```latex
\begin{columns}[T]
  \begin{column}{.15\linewidth}
    \includegraphics[width=\linewidth]{logo1.pdf}
  \end{column}

  \begin{column}{.7\linewidth}
    \centering
    {\VeryHuge\textbf{Your Research Title Here}}\\[0.5cm]
    {\Large Author One\textsuperscript{1}, Author Two\textsuperscript{2}}\\[0.3cm]
    {\normalsize \textsuperscript{1}University A, \textsuperscript{2}University B}
  \end{column}

  \begin{column}{.15\linewidth}
    \includegraphics[width=\linewidth]{logo2.pdf}
  \end{column}
\end{columns}
```

### Main Content Area

**Typical Size**: 70-80% of total poster

**Organization Principles**:

**1. Top-to-Bottom Flow**:
```
Introduction/Background
        ↓
Methods/Approach
        ↓
Results (Multiple panels)
        ↓
Discussion/Conclusions
```

**2. Left-to-Right, Top-to-Bottom**:
```
[Intro] [Results 1] [Results 3]
[Methods] [Results 2] [Discussion]
```

**3. Centralized Main Figure**:
```
[Intro]  [Main Figure]  [Discussion]
[Methods]   (center)    [Conclusions]
```

**Section Sizing**:
- Introduction: 10-15% of content area
- Methods: 15-20%
- Results: 40-50% (largest section)
- Discussion/Conclusions: 15-20%

### Footer Area

**Typical Size**: 5-10% of total poster height

**Common Elements**:
- References (abbreviated, 5-10 key citations)
- Acknowledgments (funding, collaborators)
- Contact information
- QR codes (paper, code, data)
- Social media handles (optional)
- Conference hashtags

**Layout**:
```
+----------------------------------------+
| References: 1. Author (2023) ... |  📱  |
| Acknowledgments: Funded by ...   | QR   |
| Contact: name@email.edu          | Code |
+----------------------------------------+
```

**LaTeX Footer**:
```latex
\begin{block}{}
  \footnotesize
  \begin{columns}[T]
    \begin{column}{0.7\linewidth}
      \textbf{References}
      \begin{enumerate}
        \item Author A et al. (2023). Journal. doi:...
        \item Author B et al. (2024). Conference.
      \end{enumerate}

      \textbf{Acknowledgments}
      This work was supported by Grant XYZ.

      \textbf{Contact}: firstname.lastname@university.edu
    \end{column}

    \begin{column}{0.25\linewidth}
      \centering
      \qrcode[height=3cm]{https://doi.org/10.1234/paper}\\
      \tiny Scan for full paper
    \end{column}
  \end{columns}
\end{block}
```
