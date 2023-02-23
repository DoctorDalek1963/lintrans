"""A simple module containing custom Pygments lexers."""

import re

from pygments.lexer import RegexLexer, bygroups, do_insertions, include, this, using
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)
from pygments.util import ClassNotFound, get_bool_opt


class CommentedTextLexer(RegexLexer):
    """A lexer that adds // or # comments to text files."""

    name = "CommentedText"

    tokens = {
        "root": [
            (r"#.*\n", Comment),
            (r"//.*\n", Comment),
        ]
    }


class BnfHashtagCommentLexer(RegexLexer):
    """This lexer extends pygments' built-in BnfLexer with # comments."""

    name = 'BNF'

    tokens = {
        'root': [
            (r"#.*\n", Comment),

            (r'(<)([ -;=?-~]+)(>)',
             bygroups(Punctuation, Name.Class, Punctuation)),

            # an only operator
            (r'::=', Operator),

            # fallback
            (r'[^<>:]+', Text),  # for performance
            (r'.', Text),
        ],
    }


class SphObjInvTextLexer(RegexLexer):
    """A lexer for my custom language used for the text files that generate Sphinx object inventory files."""

    name = "SphObjInvText"

    tokens = {
        "root": [
            (r"#.*\n", Comment),
            (
                r"^(\S+)(\s+)([^\s:]+)(:)(\S+)(\s+)([0-9]+)(\s+)(\S+)(\s+)(\S+)",
                bygroups(
                    Name.Variable.Global,  # Reference name
                    Whitespace,
                    Name.Namespace,  # Domain
                    Punctuation,
                    Name.Class,  # Role
                    Whitespace,
                    Number,  # Priority
                    Whitespace,
                    Name.Attribute,  # URI
                    Whitespace,
                    Text,  # Display name
                ),
            ),
        ]
    }


# This class was adapted from a French language pseudocode parser found here:
# https://github.com/svvac/pygments-lexer-pseudocode/blob/master/pygments_lexer_pseudocode/__init__.py
class OCRPseudocodeLexer(RegexLexer):
    """A lexer for OCR-style pseudocode."""

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
                r"(function|procedure)( )([^(]+)(\()",
                bygroups(Keyword, Whitespace, Name.Function, Punctuation),
            ),
            (
                r"(public|private)( )(function|procedure)( )([^(]+)(\()",
                bygroups(
                    Keyword, Whitespace, Keyword, Whitespace, Name.Function, Punctuation
                ),
            ),
            (
                r"(const)( )(\S+)(:)( )(\S+)( )(=)",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name.Variable.Global,
                    Punctuation,
                    Whitespace,
                    Keyword.Type,
                    Whitespace,
                    Punctuation,
                ),
            ),
            (
                "(class)( )(\\S+)( )(extends)( )(\\S+)",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name.Class,
                    Whitespace,
                    Keyword,
                    Whitespace,
                    Name.Class,
                ),
            ),
            ("(class)( )(\\S+)", bygroups(Keyword, Whitespace, Name.Class)),
            (
                r"(private)( )(\S+)(:)( )(.+)$",
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
                r"(public)( )(\S+)(:)( )(.+)$",
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
                r"\b(import|as|from|endfunction|endprocedure|if|then|else|endif|return|endclass|public|private|new|super|for|next)\s*\b",
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


# See https://github.com/pygments/pygments/blob/2.14.0/pygments/lexers/markup.py#L499-L606
class MarkdownWithCommentsLexer(RegexLexer):
    """A lexer for markdown, taken from the Pygments source code, with comments added."""

    name = "Markdown with comments"
    aliases = ["markdown", "md"]
    flags = re.MULTILINE

    def _handle_codeblock(self, match):
        """match args: 1:backticks, 2:lang_name, 3:newline, 4:code, 5:backticks"""
        from pygments.lexers import get_lexer_by_name

        # section header
        yield match.start(1), String.Backtick, match.group(1)
        yield match.start(2), String.Backtick, match.group(2)
        yield match.start(3), Text, match.group(3)

        # lookup lexer if wanted and existing
        lexer = None
        if self.handlecodeblocks:
            try:
                lexer = get_lexer_by_name(match.group(2).strip())
            except ClassNotFound:
                pass
        code = match.group(4)

        # no lexer for this language. handle it like it was a code block
        if lexer is None:
            yield match.start(4), String, code
        else:
            yield from do_insertions([], lexer.get_tokens_unprocessed(code))

        yield match.start(5), String.Backtick, match.group(5)

    tokens = {
        "root": [
            # NEW: comment in <!-- --> (html-style)
            (r"^<!--.+-->", Comment),
            # heading with '#' prefix (atx-style)
            (r"(^#[^#].+)(\n)", bygroups(Generic.Heading, Text)),
            # subheading with '#' prefix (atx-style)
            (r"(^#{2,6}[^#].+)(\n)", bygroups(Generic.Subheading, Text)),
            # heading with '=' underlines (Setext-style)
            (
                r"^(.+)(\n)(=+)(\n)",
                bygroups(Generic.Heading, Text, Generic.Heading, Text),
            ),
            # subheading with '-' underlines (Setext-style)
            (
                r"^(.+)(\n)(-+)(\n)",
                bygroups(Generic.Subheading, Text, Generic.Subheading, Text),
            ),
            # task list
            (
                r"^(\s*)([*-] )(\[[ xX]\])( .+\n)",
                bygroups(Whitespace, Keyword, Keyword, using(this, state="inline")),
            ),
            # bulleted list
            (
                r"^(\s*)([*-])(\s)(.+\n)",
                bygroups(Whitespace, Keyword, Whitespace, using(this, state="inline")),
            ),
            # numbered list
            (
                r"^(\s*)([0-9]+\.)( .+\n)",
                bygroups(Whitespace, Keyword, using(this, state="inline")),
            ),
            # quote
            (r"^(\s*>\s)(.+\n)", bygroups(Keyword, Generic.Emph)),
            # code block fenced by 3 backticks
            (r"^(\s*```\n[\w\W]*?^\s*```$\n)", String.Backtick),
            # code block with language
            (r"^(\s*```)(\w+)(\n)([\w\W]*?)(^\s*```$\n)", _handle_codeblock),
            include("inline"),
        ],
        "inline": [
            # escape
            (r"\\.", Text),
            # inline code
            (r"([^`]?)(`[^`\n]+`)", bygroups(Text, String.Backtick)),
            # warning: the following rules eat outer tags.
            # eg. **foo _bar_ baz** => foo and baz are not recognized as bold
            # bold fenced by '**'
            (r"([^\*]?)(\*\*[^* \n][^*\n]*\*\*)", bygroups(Text, Generic.Strong)),
            # bold fenced by '__'
            (r"([^_]?)(__[^_ \n][^_\n]*__)", bygroups(Text, Generic.Strong)),
            # italics fenced by '*'
            (r"([^\*]?)(\*[^* \n][^*\n]*\*)", bygroups(Text, Generic.Emph)),
            # italics fenced by '_'
            (r"([^_]?)(_[^_ \n][^_\n]*_)", bygroups(Text, Generic.Emph)),
            # strikethrough
            (r"([^~]?)(~~[^~ \n][^~\n]*~~)", bygroups(Text, Generic.Deleted)),
            # mentions and topics (twitter and github stuff)
            (r"[@#][\w/:]+", Name.Entity),
            # (image?) links eg: ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
            (
                r"(!?\[)([^]]+)(\])(\()([^)]+)(\))",
                bygroups(Text, Name.Tag, Text, Text, Name.Attribute, Text),
            ),
            # reference-style links, e.g.:
            #   [an example][id]
            #   [id]: http://example.com/
            (
                r"(\[)([^]]+)(\])(\[)([^]]*)(\])",
                bygroups(Text, Name.Tag, Text, Text, Name.Label, Text),
            ),
            (
                r"^(\s*\[)([^]]*)(\]:\s*)(.+)",
                bygroups(Text, Name.Label, Text, Name.Attribute),
            ),
            # general text, must come last!
            (r"[^\\\s]+", Text),
            (r".", Text),
        ],
    }

    def __init__(self, **options):
        self.handlecodeblocks = get_bool_opt(options, "handlecodeblocks", True)
        RegexLexer.__init__(self, **options)
