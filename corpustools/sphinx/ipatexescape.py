# encoding: utf-8
import sphinx.util.texescape as te

replacements = r'''
    ɔ \textipa{O}
    ɪ \textipa{I}
    ʊ \textipa{U}
    ʃ \textipa{S}
    ː \textipa{:}
    ʒ \textipa{Z}
    ɚ \textipa{\textrhookschwa}
    ɑ \textipa{A}
    ŋ \textipa{N}
    æ \textipa{\ae}
    ə \textipa{@}
    ɹ \textipa{\*r}
    ɡ \textipa{g}
     ∅ $\varnothing$
    ɛ \textipa{E}
    ā \textipa{\=a}
'''

def setup(app):
    replacement_list = [
        tuple(line.strip().split())
        for line in replacements.strip().splitlines()
    ]

    te.tex_replacements += replacement_list
    te.init()
