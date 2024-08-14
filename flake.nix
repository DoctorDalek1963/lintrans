{
  description = "lintrans, the linear transformation visualizer";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-parts.url = "github:hercules-ci/flake-parts";

    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs @ {
    self,
    flake-parts,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [
        inputs.pre-commit-hooks.flakeModule
      ];

      systems = ["x86_64-linux" "aarch64-linux"];
      perSystem = {
        pkgs,
        config,
        ...
      }: let
        buildPy311Package = {
          pname,
          version,
          hash,
        }:
          pkgs.python311Packages.buildPythonPackage {
            inherit pname version;
            src = pkgs.fetchPypi {
              inherit pname version hash;
            };
          };

        python311-packages = {
          singleton-decorator = buildPy311Package {
            pname = "singleton-decorator";
            version = "1.0.0";
            hash = "sha256-GpCtiopzi+WRycFn/dZ3xdSkPRvGscEoInvhxeA77gc=";
          };

          # pytest-custom-exit-code = buildPy311Package {
          #   pname = "pytest-custom_exit_code";
          #   version = "0.3.0";
          #   hash = "sha256-Uf//DuLB3cwSQuLdsqX9AkgnF+M6IybvMw46pDAkRjU=";
          # };
        };

        python-runtime-libs = p: [
          p.nptyping
          p.numpy
          p.packaging
          p.pip # TODO: Remove pip
          p.pyqt5
          python311-packages.singleton-decorator
        ];

        python-compile-libs = p: [
          p.pillow
          # p.pyinstaller
        ];

        python-dev-libs = p: [
          p.flake8
          p.isort
          p.mypy
          p.pycodestyle
          p.pydocstyle
          p.pytest
          p.pytest-xvfb
          p.pyqt5-stubs
          p.toml
          # python311-packages.pytest-custom-exit-code
        ];

        python-docs-libs = p: [
          p.pylint
          p.sphinx
          p.sphinx-rtd-theme
          # p.sphinxcontrib-email
          # p.sphobjinv
        ];

        buildPython = libFuncs:
          pkgs.python311.withPackages (p:
            if builtins.isList libFuncs
            then pkgs.lib.lists.flatten (builtins.map (f: f p) libFuncs)
            else libFuncs p);
      in rec {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            (buildPython [
              python-runtime-libs
              python-compile-libs
              python-dev-libs
              python-docs-libs
            ])
          ];

          shellHook = ''
            ${config.pre-commit.installationScript}
          '';
        };

        packages = rec {
          default = native-python-application;

          native-python-package = pkgs.python311.pkgs.buildPythonPackage {
            name = "lintrans-native-python-package";
            src = self;
            format = "setuptools";

            nativeBuildInputs = with pkgs.python311Packages; [setuptools wheel];
            propagatedBuildInputs = python-runtime-libs pkgs.python311Packages;
          };

          native-python-application = pkgs.callPackage (
            {stdenvNoCC}: let
              lintransPython = buildPython [
                python-runtime-libs
                (_: [native-python-package])
              ];
            in
              stdenvNoCC.mkDerivation {
                name = "lintrans-native-python-application";

                nativeBuildInputs = [pkgs.qt5.wrapQtAppsHook];

                propagatedBuildInputs = [
                  lintransPython
                  native-python-package
                ];

                dontUnpack = true;

                buildPhase = let
                  bin = pkgs.writeShellScriptBin "lintrans" ''
                    ${lintransPython}/bin/python -m lintrans
                  '';
                in
                  # bash
                  ''
                    runHook preBuild
                    mkdir -p $out/bin
                    cp ${bin}/bin/lintrans $out/bin/
                    runHook postBuild
                  '';

                dontWrapQtApps = true;
                preFixup = ''
                  wrapQtApp "$out/bin/lintrans" --prefix PATH : /path/to/bin
                '';
              }
          ) {};
        };

        apps = rec {
          default = native-python-application;

          native-python-application = {
            type = "app";
            program = "${packages.native-python-application}/bin/lintrans";
          };
        };

        # See https://flake.parts/options/pre-commit-hooks-nix and
        # https://github.com/cachix/git-hooks.nix/blob/master/modules/hooks.nix
        # for all the available hooks and options
        pre-commit = {
          settings.hooks = let
            python = buildPython [
              python-runtime-libs
              python-dev-libs
              (_: [packages.native-python-package])
            ];
          in {
            check-added-large-files.enable = true;
            check-merge-conflicts.enable = true;
            check-toml.enable = true;
            check-vcs-permalinks.enable = true;
            check-yaml.enable = true;
            end-of-file-fixer.enable = true;
            trim-trailing-whitespace.enable = true;

            check-python.enable = true;
            python-debug-statements.enable = true;

            flake8 = {
              enable = true;
              files = ''^(src|tests)/.*\.py$'';
            };
            isort = {
              enable = true;
              files = ''^(src|tests)/.*\.py$'';
            };
            mypy = {
              enable = true;
              files = ''^(src|tests)/.*\.py$'';
            };

            alejandra.enable = true;
            deadnix.enable = true;
            statix.enable = true;

            pytest = {
              enable = true;
              entry = "${python}/bin/python -m pytest";
              files = ''^(src|tests)/.*\.py$'';
              pass_filenames = false;
            };

            # pytest-doctests = {
            #   enable = true;
            #   entry = "${python}/bin/python -m pytest";
            #   args = ["--doctest-modules" "--suppress-no-test-exit-code"];
            #   files = ''^src/.*\.py$'';
            # };

            # - repo: https://github.com/PyCQA/pydocstyle
            #   rev: 6.1.1
            #   hooks:
            #     - id: pydocstyle
            #       files: ^(src|tests)/.*\.py$
            #       additional_dependencies: [toml==0.10.2]
            #
            # - repo: local
            #   hooks:
            #     - id: pycodestyle
            #       name: pycodestyle
            #       entry: pycodestyle
            #       language: system
            #       files: ^(src|tests)/.*\.py$
          };
        };
      };
    };
}
