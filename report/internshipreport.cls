% =====================================================
% CLASS: internshipreport.cls
% =====================================================

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{internshipreport}[2025/08/18 v2.0 Professional Internship Report Class]

% Base class
\LoadClass[12pt,a4paper,openright]{report}

% =====================================================
% CORE PACKAGES
% =====================================================

% Encoding and language
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{lmodern}

% Geometry and layout
\RequirePackage[left=2.54cm,right=2.54cm,top=2.54cm,bottom=2.54cm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{setspace}
\RequirePackage{indentfirst}
\RequirePackage{tocloft}

% Graphics and colors
\RequirePackage{graphicx}
\RequirePackage{wrapfig}
\RequirePackage{subfig}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage[table]{xcolor}
\RequirePackage{colortbl}
\RequirePackage{float}
\RequirePackage{tcolorbox}
\tcbuselibrary{most}

% Advanced tables
\RequirePackage{array}
\RequirePackage{tabularx}
\RequirePackage{longtable}
\RequirePackage{multirow}
\RequirePackage{multicol}
\RequirePackage{booktabs}

% Lists and enumerations
\RequirePackage{enumitem}
\RequirePackage{listings}
\RequirePackage{fancyvrb}

% Mathematics and algorithms
\RequirePackage{amsmath}
\RequirePackage{amsfonts}
\RequirePackage{amssymb}
\RequirePackage{algorithm}
\RequirePackage{algpseudocode}

% Bibliography and references
\RequirePackage[backend=biber,style=apa,sorting=none]{biblatex}
\RequirePackage[hidelinks]{hyperref}
\RequirePackage{url}
\RequirePackage{cleveref}

% Professional fonts (Times New Roman style)
\RequirePackage{times}
\RequirePackage{mathptmx}

% Advanced graphics
\RequirePackage{tikz}
\RequirePackage{pgfplots}
\pgfplotsset{compat=1.18}

% Decorative elements
\RequirePackage{fancybox}
\RequirePackage{eso-pic}
% \RequirePackage{wallpaper}

% Miscellaneous
\RequirePackage{lipsum}
\RequirePackage{afterpage}
\RequirePackage[normalem]{ulem}

% =====================================================
% COLOR SCHEME (Inspired  but Generic)
% =====================================================

% Primary color palette (Professional blue-red scheme)
\definecolor{primarycolor}{RGB}{25,118,210}        % Professional red
\definecolor{primarydark}{RGB}{13,71,161}         % Dark red
\definecolor{primarylight}{RGB}{144,202,249}     % Light red

% Secondary colors
\definecolor{secondarycolor}{RGB}{30,30,30}       % Professional black
\definecolor{accentcolor}{RGB}{0,82,147}          % Professional blue
\definecolor{successcolor}{RGB}{0,130,62}         % Professional green

% Neutral colors
\definecolor{textcolor}{RGB}{30,30,30}            % Text color
\definecolor{graycolor}{RGB}{110,110,110}         % Standard gray
\definecolor{lightgray}{RGB}{250,250,250}         % Very light gray
\definecolor{mediumgray}{RGB}{180,180,180}        % Medium gray

% Table colors (Word-like)
\definecolor{tableheader}{RGB}{235,235,235}       % Table headers
\definecolor{tablealternate}{RGB}{247,247,247}    % Alternate rows

% Code colors
\definecolor{codecomment}{RGB}{142,142,142}
\definecolor{codekeyword}{RGB}{220,80,80}
\definecolor{codestring}{RGB}{0,130,62}
\definecolor{codenumber}{RGB}{0,82,147}

% =====================================================
% METADATA VARIABLES
% =====================================================

% Report information
\newcommand{\reporttitle}[1]{\renewcommand{\@reporttitle}{#1}}
\newcommand{\@reporttitle}{}

\newcommand{\reportsubtitle}[1]{\renewcommand{\@reportsubtitle}{#1}}
\newcommand{\@reportsubtitle}{}

\newcommand{\reporttype}[1]{\renewcommand{\@reporttype}{#1}}
\newcommand{\@reporttype}{INTERNSHIP REPORT}

% Author information
\newcommand{\reportauthor}[1]{\renewcommand{\@reportauthor}{#1}}
\newcommand{\@reportauthor}{}

\newcommand{\studentid}[1]{\renewcommand{\@studentid}{#1}}
\newcommand{\@studentid}{}

\newcommand{\program}[1]{\renewcommand{\@program}{#1}}
\newcommand{\@program}{}

\newcommand{\academicyear}[1]{\renewcommand{\@academicyear}{#1}}
\newcommand{\@academicyear}{}

\newcommand{\internshipperiod}[1]{\renewcommand{\@internshipperiod}{#1}}
\newcommand{\@internshipperiod}{}

% Institution information
\newcommand{\university}[1]{\renewcommand{\@university}{#1}}
\newcommand{\@university}{}

\newcommand{\department}[1]{\renewcommand{\@department}{#1}}
\newcommand{\@department}{}

\newcommand{\academicsupervisor}[1]{\renewcommand{\@academicsupervisor}{#1}}
\newcommand{\@academicsupervisor}{}

\newcommand{\supervisorposition}[1]{\renewcommand{\@supervisorposition}{#1}}
\newcommand{\@supervisorposition}{}

% Company information
\newcommand{\company}[1]{\renewcommand{\@company}{#1}}
\newcommand{\@company}{}

\newcommand{\companydepartment}[1]{\renewcommand{\@companydepartment}{#1}}
\newcommand{\@companydepartment}{}

\newcommand{\companytutor}[1]{\renewcommand{\@companytutor}{#1}}
\newcommand{\@companytutor}{}

\newcommand{\tutorposition}[1]{\renewcommand{\@tutorposition}{#1}}
\newcommand{\@tutorposition}{}

\newcommand{\defensedate}[1]{\renewcommand{\@defensedate}{#1}}
\newcommand{\@defensedate}{}

% =====================================================
% CUSTOM COMMANDS (English equivalents of SGC commands)
% =====================================================

% Company and technology highlighting
\newcommand{\companyname}[1]{\textcolor{primarycolor}{\textbf{#1}}}
\newcommand{\technology}[1]{\texttt{\color{accentcolor}#1}}
\newcommand{\framework}[1]{\textbf{\color{secondarycolor}#1}}
\newcommand{\database}[1]{\textsc{\color{primarycolor}#1}}

% Emphasis commands
\newcommand{\important}[1]{\textcolor{primarycolor}{\textbf{#1}}}
\newcommand{\keyword}[1]{\textcolor{secondarycolor}{\textbf{#1}}}
\newcommand{\concept}[1]{\textcolor{graycolor}{\textit{#1}}}
\newcommand{\highlight}[1]{\textcolor{primarycolor}{\textbf{#1}}}

% Metrics and results
\newcommand{\metric}[1]{\textcolor{primarycolor}{\textbf{#1}}}
\newcommand{\gain}[1]{\textcolor{successcolor}{\textbf{#1}}}
\newcommand{\improvement}[1]{\textcolor{primarycolor}{\textbf{#1}}}

% Project management
\newcommand{\milestone}[1]{\textbf{\color{primarycolor}#1}}
\newcommand{\deliverable}[1]{\textit{\color{secondarycolor}#1}}
\newcommand{\sprint}[1]{\textbf{\color{accentcolor}#1}}

% =====================================================
% HEADER AND FOOTER STYLE (Word-like, inspired )
% =====================================================

\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\textcolor{graycolor}{\footnotesize\MakeUppercase{\@reporttitle}}}
\fancyfoot[R]{\textcolor{graycolor}{\footnotesize{\leftmark} \quad \small{\textbf{\textcolor{graycolor}{\textbar}}} \quad \footnotesize{\textbf{\thepage}}}}

\renewcommand{\footrulewidth}{0.5pt}
\renewcommand{\footrule}{\color{graycolor}\hrule width\headwidth height\footrulewidth}

% Plain style for chapter pages
\fancypagestyle{plain}{%
    \fancyhf{}
    \fancyfoot[C]{\textcolor{textcolor}{\thepage}}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
}

% =====================================================
% TITLE FORMATTING
% =====================================================

\titleformat{\chapter}[display]
    {\normalfont\huge\bfseries\color{primarycolor}}
    {\chaptertitlename\ \thechapter}{20pt}{\Huge\MakeUppercase}

\titleformat{\section}
    {\normalfont\Large\bfseries\color{secondarycolor}}
    {\thesection}{1em}{}

\titleformat{\subsection}
    {\normalfont\large\bfseries\color{graycolor}}
    {\thesubsection}{1em}{}

\titleformat{\subsubsection}
    {\normalfont\normalsize\bfseries\color{mediumgray}}
    {\thesubsubsection}{1em}{}

% =====================================================
% LIST FORMATTING (Word-like)
% =====================================================

\setlist[itemize,1]{
    labelindent=0pt,
    leftmargin=25pt,
    itemsep=3pt,
    parsep=0pt,
    label=\textcolor{secondarycolor}{\textbullet}
}

\setlist[itemize,2]{
    labelindent=0pt,
    leftmargin=40pt,
    itemsep=2pt,
    parsep=0pt,
    label=\textcolor{graycolor}{--}
}

\setlist[enumerate]{
    labelindent=0pt,
    leftmargin=25pt,
    itemsep=3pt,
    parsep=0pt
}

% =====================================================
% TABLE FORMATTING (Word-like)
% =====================================================

\arrayrulecolor{graycolor}
\renewcommand{\arraystretch}{1.2}

% Table commands
\newcommand{\tableheadercell}[1]{\cellcolor{tableheader}\textbf{\color{textcolor}#1}}
\newcommand{\alternaterow}{\rowcolor{tablealternate}}

% =====================================================
% CAPTION FORMATTING
% =====================================================

\captionsetup{
    font={small,color=textcolor},
    labelfont={bf,color=primarycolor},
    margin=1cm,
    skip=8pt
}

% =====================================================
% CODE LISTING STYLE
% =====================================================

\lstset{
    backgroundcolor=\color{lightgray},
    basicstyle=\footnotesize\ttfamily\color{textcolor},
    keywordstyle=\color{codekeyword}\bfseries,
    commentstyle=\color{codecomment}\itshape,
    stringstyle=\color{codestring},
    numberstyle=\tiny\color{graycolor},
    numbers=left,
    numbersep=8pt,
    frame=single,
    rulecolor=\color{graycolor},
    breaklines=true,
    tabsize=2,
    xleftmargin=1.5em,
    showstringspaces=false
}

% =====================================================
% SPACING AND TYPOGRAPHY
% =====================================================

\setlength{\parskip}{6pt}
\setlength{\parindent}{15pt}
\onehalfspacing

% =====================================================
% HYPERLINK FORMATTING
% =====================================================

\hypersetup{
    colorlinks=true,
    linkcolor=primarycolor,
    urlcolor=accentcolor,
    citecolor=graycolor,
    pdfborder={0 0 0},
    pdftitle={\@reporttitle},
    pdfauthor={\@reportauthor},
    pdfsubject={Internship Report},
    pdfkeywords={internship, report, academic, professional}
}

% =====================================================
% TOC CUSTOMIZATION
% =====================================================

\renewcommand{\cftchappresnum}{\chaptername~}
\renewcommand{\cftchapaftersnum}{ :\hspace{0.05em}}
\renewcommand{\cftchapnumwidth}{5.5em}

% =====================================================
% CUSTOM ENVIRONMENTS
% =====================================================

% Information box (simple, Word-like)
% \newenvironment{infobox}[1][]
% {
%     \begin{center}
%     \begin{minipage}{0.95\textwidth}
%     \begin{quote}
%     \ifx&#1&\else\textbf{\color{primarycolor}#1}\par\noindent\textcolor{graycolor}{\rule{\textwidth}{0.5pt}}\vspace{5pt}\fi
% }
% {
%     \vspace{5pt}
%     \par\noindent\textcolor{graycolor}{\rule{\textwidth}{0.5pt}}
%     \end{quote}
%     \end{minipage}
%     \end{center}
% }

% Objectives environment
\newenvironment{objectives}
{
    \par\vspace{10pt}
    \noindent\textbf{\color{primarycolor}Objectifs~:}
    \par\vspace{5pt}
}
{
    \par\vspace{5pt}
}

% Constraints environment
\newenvironment{constraints}
{
    \par\vspace{10pt}
    \noindent\textbf{\color{primarycolor}Contraintes~:}
    \par\vspace{5pt}
}
{
    \par\vspace{5pt}
}

% Definition environment
\newenvironment{definition}[1]
{
    \par\vspace{10pt}
    \noindent\textbf{\color{primarycolor}Définition --- #1~:}
    \par\vspace{5pt}
    \begin{quote}
}
{
    \end{quote}
    \par\vspace{5pt}
}

% Results/Metrics environment
\newenvironment{results}
{
    \par\vspace{10pt}
    \noindent\textbf{\color{successcolor}Résultats~:}
    \par\vspace{5pt}
}
{
    \par\vspace{5pt}
}

% Key findings environment
\newenvironment{keyfindings}
{
    \par\vspace{10pt}
    \noindent\textbf{\color{primarycolor}Constats principaux~:}
    \par\vspace{5pt}
}
{
    \par\vspace{5pt}
}

% Methodology environment
\newenvironment{methodology}
{
    \par\vspace{10pt}
    \noindent\textbf{\color{accentcolor}Démarche~:}
    \par\vspace{5pt}
}
{
    \par\vspace{5pt}
}

% User story environment
\newcommand{\userstory}[3]{
    \begin{tcolorbox}[colback=lightgray,colframe=accentcolor,title=\textcolor{white}{\textbf{User Story}},width=\textwidth]
        \textbf{As a} #1\\
        \textbf{I want} #2\\
        \textbf{So that} #3
    \end{tcolorbox}
}

% Advanced boxes with tcolorbox
\tcbset{
    every box/.style={
        enhanced,
        colback=white,
        colframe=graycolor,
        boxrule=0.5pt,
        arc=0mm,
        outer arc=0mm,
        left=1em,
        right=1em,
        top=0.5em,
        bottom=0.5em,
        before skip=1em,
        after skip=1em
    }
}

% % Warning box
% \newtcolorbox{warningbox}{
%     colback=yellow!10,
%     colframe=orange,
%     title=\textcolor{white}{\textbf{Warning}},
%     fonttitle=\bfseries
% }

% % Success box
% \newtcolorbox{successbox}{
%     colback=green!10,
%     colframe=successcolor,
%     title=\textcolor{white}{\textbf{Success}},
%     fonttitle=\bfseries
% }

% Technical box
\newtcolorbox{techbox}{
    colback=blue!5,
    colframe=accentcolor,
    title=\textcolor{white}{\textbf{Technical Note}},
    fonttitle=\bfseries
}

% =====================================================
% TITLE PAGE COMMAND
% =====================================================

\newcommand{\makereportpage}{
\begin{titlepage}
\newgeometry{top=1.27cm,bottom=1.27cm,left=1.27cm,right=1.27cm}
\begin{center}

% University and company logos space
\vspace{1cm}
{\Large \textcolor{graycolor}{[UNIVERSITY LOGO]} \hfill \textcolor{graycolor}{[COMPANY LOGO]}}



\vspace{3cm}

% Report type
{\Large \textbf{\textcolor{primarycolor}{\@reporttype}}}

\vspace{1.5cm}

% Main title
{\LARGE \textbf{\textcolor{textcolor}{\@reporttitle}}}

\vspace{0.8cm}

% Subtitle
\ifx\@reportsubtitle\empty\else
{\large \textbf{\textcolor{graycolor}{\@reportsubtitle}}}
\vspace{1cm}
\fi

% Student information
\textcolor{textcolor}{\textbf{Presented by: \@reportauthor}}\\
\ifx\@studentid\empty\else\textcolor{graycolor}{Student ID: \@studentid}\\\fi
\textcolor{textcolor}{\textbf{Program:} \@program}\\
\textcolor{textcolor}{\textbf{Academic Year:} \@academicyear}

\vspace{2cm}

% Supervisors
\begin{minipage}[t]{0.45\textwidth}
\raggedright
\textcolor{textcolor}{\textbf{Academic Supervisor:}}\\
\textcolor{graycolor}{\@academicsupervisor}\\
\ifx\@supervisorposition\empty\else\textcolor{graycolor}{\@supervisorposition}\\\fi
\textcolor{primarycolor}{\textbf{\@university}}
\end{minipage}
\hfill
\begin{minipage}[t]{0.45\textwidth}
\raggedleft
\textcolor{textcolor}{\textbf{Company Supervisor:}}\\
\textcolor{graycolor}{\@companytutor}\\
\ifx\@tutorposition\empty\else\textcolor{graycolor}{\@tutorposition}\\\fi
\textcolor{primarycolor}{\textbf{\@company}}
\end{minipage}

\vfill

% Internship period
\textcolor{textcolor}{\textbf{Internship Period: \@internshipperiod}}

% Defense date (optional)
\ifx\@defensedate\empty\else
\vspace{0.5cm}
\textcolor{graycolor}{Defense Date: \@defensedate}
\fi

\end{center}
\restoregeometry
\end{titlepage}
}

% =====================================================
% BIBLIOGRAPHY SETUP
% =====================================================

\addbibresource{content/backmatter/bibliography.bib}

% =====================================================
% ADDITIONAL SETTINGS
% =====================================================

% Header height
\setlength{\headheight}{14.5pt}

% Float placement
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.8}
\setcounter{topnumber}{2}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}
\setcounter{dbltopnumber}{2}
\renewcommand{\dbltopfraction}{0.9}
\renewcommand{\textfraction}{0.07}
\renewcommand{\floatpagefraction}{0.7}
\renewcommand{\dblfloatpagefraction}{0.7}

% =====================================================
% END OF CLASS
% =====================================================