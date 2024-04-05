{
  description = "The write-up for lintrans";

  inputs = {
    # NOTE: We could pin this to f12a7d932ddf7f4d0c5e0c5664dec08e718e67a8 to
    # get minted 2.6, which doesn't quote pygmentize arguments, but that
    # revision has certain TeXlive packages (like gensymb) completely missing,
    # so it's not usable. See ./tools/process-code-snippets/src/snippet/comment.rs,
    # line 215 for more information.
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-parts.url = "github:hercules-ci/flake-parts";

    tools = {
      url = "path:./tools";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs @ {
    self,
    flake-parts,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux"];
      perSystem = {
        pkgs,
        system,
        ...
      }: let
        # NOTE: A list of all available pkgs.texlive.* packages is available here:
        # https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-23.11/pkgs/tools/typesetting/tex/texlive/tlpdb.nix
        texlive = pkgs.texlive.combine {
          inherit
            (pkgs.texlive)
            scheme-basic
            latexmk
            biber
            biblatex
            cancel
            csquotes
            fontspec
            footmisc
            gensymb
            luacode
            luatexbase
            mathtools
            minted
            pdflscape
            pgf # TikZ
            subfiles
            tkz-euclide
            xpatch
            ;
        };

        buildInputs = [
          inputs.tools.packages.${system}.generate-appendices
          inputs.tools.packages.${system}.process-code-snippets
          texlive
          pkgs.coreutils
          pkgs.fd
          pkgs.hack-font
          pkgs.ncurses # tput
          pkgs.python311Packages.pygments
          pkgs.which
        ];

        lualatex-command =
          # bash
          ''
            lualatex -file-line-error -halt-on-error -interaction=nonstopmode \
              -shell-escape -recorder --jobname="main" "main.tex"
          '';
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = buildInputs ++ (with pkgs; [just sd zip]);
        };

        packages = rec {
          default = lintrans-write-up-zip;

          lintrans-write-up-zip = pkgs.callPackage (
            {stdenvNoCC}:
              stdenvNoCC.mkDerivation rec {
                name = "lintrans-write-up-zip";
                src = self;

                buildInputs = [
                  lintrans-write-up-pdf
                  pkgs.fd
                  pkgs.zip
                ];

                buildPhase = ''
                  runHook preBuild

                  cp ${lintrans-write-up-pdf}/lintrans.pdf ./lintrans.pdf
                  fd -e mp4 . videos/ -X zip lintrans.zip lintrans.pdf

                  runHook postBuild
                '';

                installPhase = ''
                  runHook preInstall

                  mkdir $out
                  mv lintrans.zip $out/lintrans.zip
                  mv lintrans.pdf $out/lintrans.pdf # It's nice to have easy access to the PDF as well

                  runHook postInstall
                '';
              }
          ) {};

          lintrans-write-up-pdf = pkgs.callPackage (
            {stdenvNoCC}:
              stdenvNoCC.mkDerivation rec {
                name = "lintrans-write-up-pdf";
                src = self;

                inherit buildInputs;

                patches = [
                  ./patches/add-pretex.patch
                ];

                preBuild = ''
                  fd . sections/development/ -e tex -E 'processed*' \
                    -X process-code-snippets sections/development.tex sections/evaluation.tex

                  generate-appendices

                  sed -i "s/% BUILT FROM/\\\\hfill Built from \\\\texttt{${self.shortRev or self.dirtyShortRev}}/" main.tex
                '';

                buildPhase = ''
                  runHook preBuild

                  export TEXMFHOME=.cache
                  export TEXMFVAR=.cache/texmf-var
                  export SOURCE_DATE_EPOCH=${toString self.lastModified}
                  export OSFONTDIR=${pkgs.hack-font}/share/fonts

                  mkdir -p .cache/texmf-var
                  mkdir tikz-imgs

                  ${lualatex-command}
                  biber main
                  ${lualatex-command}

                  runHook postBuild
                '';

                installPhase = ''
                  runHook preInstall

                  mkdir $out
                  cp main.pdf $out/lintrans.pdf

                  runHook postInstall
                '';
              }
          ) {};
        };
      };
    };
}
