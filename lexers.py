import re
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import (
    Comment,
    Error,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)


class SphObjInvTextLexer(RegexLexer):
    name = "SphObjInvText"

    tokens = {
        "root": [
            (r"#.*\n", Comment),
            (r".*\n", Text),
        ]
    }


# This class was adapted from a French language pseudocode parser found here:
# https://github.com/svvac/pygments-lexer-pseudocode/blob/master/pygments_lexer_pseudocode/__init__.py
class OCRPseudocodeLexer(RegexLexer):
    name = "OCRPseudocode"
    flags = re.IGNORECASE

    tokens = {
        "root": [
            (r"(\/\/|#).*\n", Comment),
            include("strings"),
            include("core"),
            (r"[a-z][a-z0-9]*", Name.Variable),
            include("nums"),
            (r"[\s]+", Text),
        ],
        "core": [
            (
                r"(function)( )([^(]+)(\()",
                bygroups(Keyword, Whitespace, Name.Function, Punctuation),
            ),
            (
                r"(procedure)( )([^(]+)(\()",
                bygroups(Keyword, Whitespace, Name.Function, Punctuation),
            ),
            (r"(class)( )(\S+)\n", bygroups(Keyword, Whitespace, Name.Class)),
            (
                r"(private)( )(.+)(:)( )(\S+)$",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name.Variable.Instance,
                    Punctuation,
                    Whitespace,
                    Keyword.Type,
                ),
            ),
            (
                r"(private)( )(.+)(:)( )(\S+)$",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name.Variable.Global,
                    Punctuation,
                    Whitespace,
                    Keyword.Type,
                ),
            ),
            (
                r"(private)( )(\S+)",
                bygroups(Keyword, Whitespace, Name.Variable.Instance),
            ),
            (r"(public)( )(\S+)", bygroups(Keyword, Whitespace, Name.Variable.Global)),
            (r"(raise)( )([^\(]+)", bygroups(Keyword, Whitespace, Error)),
            (
                r"(\S+)( )(=)( )",
                bygroups(Name.Variable, Whitespace, Operator, Whitespace),
            ),
            (
                r"\b(import|as|from|endfunction|endprocedure|if|then|else|endif|return|endclass|public|private|new)\s*\b",
                Keyword,
            ),
            (r"\b(int|float|bool|string|MatrixType)\s*\b", Keyword.Type),
            (r"\b(true|false|null)\s*\b", Name.Constant),
            (r"(<=|>=|\!=|<-|\^|\*|\+|-|\/|<|>|=|\\\\|MOD|DIV|OR|AND)", Operator),
            (r"(\(|\)|\,|\;|:)", Punctuation),
            (r"\b(sqrt|pow|cos|sin|tan|exp|ln|log)\s*\b", Name.Builtin),
        ],
        "strings": [
            (r'"([^"])*"', String.Double),
            (r"'([^'])*'", String.Single),
        ],
        "nums": [
            (r"\d+(?![.Ee])", Number.Integer),
            (r"[+-]?\d*\.\d+([eE][-+]?\d+)?", Number.Float),
            (r"[+-]?\d+\.\d*([eE][-+]?\d+)?", Number.Float),
        ],
    }
