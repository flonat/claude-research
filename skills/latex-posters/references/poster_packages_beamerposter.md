# LaTeX Poster Packages: beamerposter & tikzposter

> Overview, comparison matrix, and detailed guides for beamerposter and tikzposter.
> See also: [poster_packages_baposter.md](poster_packages_baposter.md) for baposter & selection guide.


## Overview

Three major LaTeX packages dominate research poster creation: beamerposter, tikzposter, and baposter. Each has distinct strengths, syntax, and use cases. This guide provides detailed comparisons and practical examples.

## Package Comparison Matrix

| Feature | beamerposter | tikzposter | baposter |
|---------|--------------|------------|----------|
| **Learning Curve** | Easy (if familiar with Beamer) | Moderate | Moderate |
| **Flexibility** | Moderate | High | Moderate-High |
| **Default Aesthetics** | Traditional/Academic | Modern/Colorful | Professional/Clean |
| **Theme Support** | Extensive (Beamer themes) | Built-in + Custom | Limited built-in |
| **Customization** | Moderate effort | Easy with TikZ | Structured approach |
| **Layout System** | Frame-based | Block-based | Box-based with grid |
| **Multi-column** | Manual | Automatic | Automatic |
| **Graphics Integration** | Standard includegraphics | TikZ + includegraphics | Standard + advanced |
| **Community Support** | Large (Beamer community) | Growing | Smaller |
| **Best For** | Traditional academic, institutional branding | Creative designs, custom graphics | Structured multi-column layouts |
| **File Size** | Small | Medium-Large (TikZ overhead) | Medium |
| **Compilation Speed** | Fast | Slower (TikZ processing) | Fast-Medium |

## 1. beamerposter

### Overview

beamerposter extends the popular Beamer presentation class for poster-sized documents. It inherits all Beamer functionality, themes, and customization options.

### Advantages

- **Familiar syntax**: If you know Beamer, you know beamerposter
- **Extensive themes**: Access to all Beamer themes and color schemes
- **Institutional branding**: Easy to match university templates
- **Stable and mature**: Well-tested, extensive documentation
- **Block structure**: Clear organizational units
- **Good for traditional posters**: Academic conferences, thesis defenses

### Disadvantages

- **Less flexible layouts**: Column-based system can be restrictive
- **Manual positioning**: Requires careful spacing adjustments
- **Traditional aesthetics**: Can look dated compared to modern designs
- **Limited built-in styling**: Requires theme customization for unique looks

### Basic Template

```latex
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}
\usetheme{Berlin}
\usecolortheme{beaver}

% Configure fonts
\setbeamerfont{title}{size=\VeryHuge,series=\bfseries}
\setbeamerfont{author}{size=\Large}
\setbeamerfont{block title}{size=\large,series=\bfseries}

\title{Your Research Title}
\author{Author Names}
\institute{Institution}

\begin{document}
\begin{frame}[t]
  
  % Title block
  \begin{block}{}
    \maketitle
  \end{block}
  
  \begin{columns}[t]
    \begin{column}{.45\linewidth}
      
      \begin{block}{Introduction}
        Your introduction text here...
      \end{block}
      
      \begin{block}{Methods}
        Your methods text here...
      \end{block}
      
    \end{column}
    
    \begin{column}{.45\linewidth}
      
      \begin{block}{Results}
        Your results text here...
        \includegraphics[width=\linewidth]{figure.pdf}
      \end{block}
      
      \begin{block}{Conclusions}
        Your conclusions here...
      \end{block}
      
    \end{column}
  \end{columns}
  
\end{frame}
\end{document}
```

### Popular Themes

```latex
% Traditional academic
\usetheme{Berlin}
\usecolortheme{beaver}

% Modern minimal
\usetheme{Madrid}
\usecolortheme{whale}

% Blue professional
\usetheme{Singapore}
\usecolortheme{dolphin}

% Dark theme
\usetheme{Warsaw}
\usecolortheme{seahorse}
```

### Custom Colors

```latex
% Define custom colors
\definecolor{primarycolor}{RGB}{0,51,102}      % Dark blue
\definecolor{secondarycolor}{RGB}{204,0,0}     % Red
\definecolor{accentcolor}{RGB}{255,204,0}      % Gold

% Apply to beamer elements
\setbeamercolor{structure}{fg=primarycolor}
\setbeamercolor{block title}{bg=primarycolor,fg=white}
\setbeamercolor{block body}{bg=primarycolor!10,fg=black}
```

### Advanced Customization

```latex
% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Custom title formatting
\setbeamertemplate{title page}{
  \begin{center}
    {\usebeamerfont{title}\usebeamercolor[fg]{title}\inserttitle}\\[1cm]
    {\usebeamerfont{author}\insertauthor}\\[0.5cm]
    {\usebeamerfont{institute}\insertinstitute}
  \end{center}
}

% Custom block style
\setbeamertemplate{block begin}{
  \par\vskip\medskipamount
  \begin{beamercolorbox}[colsep*=.75ex,rounded=true]{block title}
    \usebeamerfont*{block title}\insertblocktitle
  \end{beamercolorbox}
  {\parskip0pt\par}
  \usebeamerfont{block body}
  \begin{beamercolorbox}[colsep*=.75ex,vmode,rounded=true]{block body}
}
```

### Three-Column Layout

```latex
\begin{columns}[t]
  \begin{column}{.3\linewidth}
    % Left column content
  \end{column}
  \begin{column}{.3\linewidth}
    % Middle column content
  \end{column}
  \begin{column}{.3\linewidth}
    % Right column content
  \end{column}
\end{columns}
```

## 2. tikzposter

### Overview

tikzposter is built on the powerful TikZ graphics package, offering modern designs with extensive customization through TikZ commands.

### Advantages

- **Modern aesthetics**: Contemporary, colorful designs out-of-the-box
- **Flexible block placement**: Easy positioning anywhere on poster
- **Beautiful themes**: Multiple professionally designed themes included
- **TikZ integration**: Seamless graphics and custom drawings
- **Color customization**: Easy to create custom color palettes
- **Automatic spacing**: Intelligent block spacing and alignment

### Disadvantages

- **Compilation time**: TikZ processing can be slow for large posters
- **File size**: PDFs can be larger due to TikZ elements
- **Learning curve**: TikZ syntax can be complex for advanced customization
- **Less institutional theme support**: Requires more work to match branding

### Basic Template

```latex
\documentclass[25pt, a0paper, portrait, margin=0mm, innermargin=15mm,
     blockverticalspace=15mm, colspace=15mm, subcolspace=8mm]{tikzposter}

\title{Your Research Title}
\author{Author Names}
\institute{Institution}

% Choose theme and color style
\usetheme{Rays}
\usecolorstyle{Denmark}

\begin{document}

\maketitle

% First column
\begin{columns}
  \column{0.5}
  
  \block{Introduction}{
    Your introduction text here...
  }
  
  \block{Methods}{
    Your methods text here...
  }
  
  % Second column
  \column{0.5}
  
  \block{Results}{
    Your results text here...
    \begin{tikzfigure}
      \includegraphics[width=0.9\linewidth]{figure.pdf}
    \end{tikzfigure}
  }
  
  \block{Conclusions}{
    Your conclusions here...
  }
  
\end{columns}

\end{document}
```

### Available Themes

```latex
% Modern with radiating background
\usetheme{Rays}

% Clean with decorative wave
\usetheme{Wave}

% Minimal with envelope corners
\usetheme{Envelope}

% Traditional academic
\usetheme{Basic}

% Board-style with texture
\usetheme{Board}

% Clean minimal
\usetheme{Simple}

% Professional with lines
\usetheme{Default}

% Autumn color scheme
\usetheme{Autumn}

% Desert color palette
\usetheme{Desert}
```

### Color Styles

```latex
% Professional blue
\usecolorstyle{Denmark}

% Warm colors
\usecolorstyle{Australia}

% Cool tones
\usecolorstyle{Sweden}

% Earth tones
\usecolorstyle{Britain}

% Default color scheme
\usecolorstyle{Default}
```

### Custom Color Definition

```latex
\definecolorstyle{CustomStyle}{
  \definecolor{colorOne}{RGB}{0,51,102}      % Dark blue
  \definecolor{colorTwo}{RGB}{255,204,0}     % Gold
  \definecolor{colorThree}{RGB}{204,0,0}     % Red
}{
  % Background Colors
  \colorlet{backgroundcolor}{white}
  \colorlet{framecolor}{colorOne}
  % Title Colors
  \colorlet{titlefgcolor}{white}
  \colorlet{titlebgcolor}{colorOne}
  % Block Colors
  \colorlet{blocktitlebgcolor}{colorOne}
  \colorlet{blocktitlefgcolor}{white}
  \colorlet{blockbodybgcolor}{white}
  \colorlet{blockbodyfgcolor}{black}
  % Innerblock Colors
  \colorlet{innerblocktitlebgcolor}{colorTwo}
  \colorlet{innerblocktitlefgcolor}{black}
  \colorlet{innerblockbodybgcolor}{colorTwo!10}
  \colorlet{innerblockbodyfgcolor}{black}
  % Note colors
  \colorlet{notefgcolor}{black}
  \colorlet{notebgcolor}{colorThree!20}
}

\usecolorstyle{CustomStyle}
```

### Block Placement and Sizing

```latex
% Full-width block
\block{Title}{Content}

% Specify width
\block[width=0.8\linewidth]{Title}{Content}

% Position manually
\block[x=10, y=50, width=30]{Title}{Content}

% Inner blocks (nested, different styling)
\block{Outer Title}{
  \innerblock{Inner Title}{
    Highlighted content
  }
}

% Note blocks (for emphasis)
\note[width=0.4\linewidth]{
  Important note text
}
```

### Advanced Features

```latex
% QR codes with tikzposter styling
\block{Scan for More}{
  \begin{center}
    \qrcode[height=5cm]{https://github.com/project}\\
    \vspace{0.5cm}
    Visit our GitHub repository
  \end{center}
}

% Multi-column within block
\block{Results}{
  \begin{tabular}{cc}
    \includegraphics[width=0.45\linewidth]{fig1.pdf} &
    \includegraphics[width=0.45\linewidth]{fig2.pdf}
  \end{tabular}
}

% Custom TikZ graphics
\block{Methodology}{
  \begin{tikzpicture}
    \node[draw, rectangle, fill=blue!20] (A) {Step 1};
    \node[draw, rectangle, fill=green!20, right=of A] (B) {Step 2};
    \draw[->, thick] (A) -- (B);
  \end{tikzpicture}
}
```

