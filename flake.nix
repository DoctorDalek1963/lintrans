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
          ...
        } @ args:
          pkgs.python311Packages.buildPythonPackage ({
              inherit pname version;

              src = pkgs.fetchPypi {
                inherit pname version hash;
              };
            }
            // args);

        python311-packages = rec {
          singleton-decorator = buildPy311Package {
            pname = "singleton-decorator";
            version = "1.0.0";
            hash = "sha256-GpCtiopzi+WRycFn/dZ3xdSkPRvGscEoInvhxeA77gc=";
          };

          pytest-custom-exit-code = buildPy311Package {
            pname = "pytest-custom_exit_code";
            version = "0.3.0";
            hash = "sha256-Uf//DuLB3cwSQuLdsqX9AkgnF+M6IybvMw46pDAkRjU=";

            dependencies = with pkgs.python311Packages; [pytest];
          };

          pyinstaller = buildPy311Package {
            pname = "pyinstaller";
            version = "5.13.2";
            hash = "sha256-yOXTSJw6fMX4QBwtH0inDliPmWfjkcOwbdrB9oX41dI=";

            # PyInstaller won't install because django needs gdal, and
            # somehow can't find it even though it's provided. Even if I
            # disable checks, the pyinstaller derivation will build just fine,
            # but compile.py complains that it can't find qt5 plugins, even
            # though QT_PLUGINS_PATH is set in the shellHook.
            meta.broken = true;
            # doCheck = false;

            GDAL_LIBRARY_PATH = "${pkgs.gdal}/lib/";

            buildInputs = with pkgs; [zlib gdal];
            dependencies =
              [pyinstaller-hooks-contrib]
              ++ (with pkgs.python311Packages; [
                pyside2
                pyside6
                pyqt5
                pyqt6
                django
                gdal
                psycopg2
                asgiref
                sqlparse
              ]);
          };

          pyinstaller-hooks-contrib = buildPy311Package {
            pname = "pyinstaller-hooks-contrib";
            version = "2021.4";
            hash = "sha256-d1tSIAs54SyVzCT4CesFCpcRD+6BnReOv94hTw9R5fQ=";

            dependencies = with pkgs.python311Packages; [altgraph];
          };

          sphinxcontrib-email = buildPy311Package {
            pname = "sphinxcontrib_email";
            version = "0.3.6";
            hash = "sha256-q8ys4UFQmFu8eh6QRNQn6P89nKr9JVufBmX4t4tmRbg=";

            dependencies = with pkgs.python311Packages; [
              lxml
              setuptools-scm
              sphinx
            ];
          };

          sphobjinv = buildPy311Package {
            pname = "sphobjinv";
            version = "2.3.1.1";
            hash = "sha256-R8YD/v0xUP1ZSzxo/qv6odKPSme3A0lBVMrIp0R6pIM=";

            dependencies =
              (with pkgs.python311Packages; [
                certifi
                jsonschema
                pytest
                sphinx
              ])
              ++ [stdio-mgr];
          };

          stdio-mgr = buildPy311Package {
            pname = "stdio-mgr";
            version = "1.0.1";
            hash = "sha256-eBw7UWMqXgmOytMW4fpklZrlQOHWbY6oqducm3ufQYY=";

            dependencies = with pkgs.python311Packages; [attrs dictdiffer];
          };
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
          # python311-packages.pyinstaller
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
          python311-packages.pytest-custom-exit-code
        ];

        python-docs-libs = p: [
          p.pylint
          p.sphinx
          p.sphinx-rtd-theme
          python311-packages.sphinxcontrib-email
          python311-packages.sphobjinv
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
              (_: packages.native-python-package)
            ])
            pkgs.graphviz
            pkgs.qt5.full
          ];

          shellHook = ''
            ${config.pre-commit.installationScript}
            export QT_PLUGINS_PATH="${pkgs.qt5.full}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/"
            export QT_QPA_PLUGINS_PATH="$QT_PLUGINS_PATH"
          '';
        };

        packages =
          rec {
            default = native-python-application;

            native-python-package = pkgs.python311.pkgs.buildPythonPackage {
              name = "lintrans-native-python-package";
              src = self;
              format = "setuptools";

              nativeBuildInputs = with pkgs.python311Packages; [setuptools wheel];
              propagatedBuildInputs = python-runtime-libs pkgs.python311Packages;
            };

            native-python-application = let
              lintransPython = buildPython [
                python-runtime-libs
                (_: [native-python-package])
              ];
            in
              pkgs.stdenvNoCC.mkDerivation rec {
                name = "lintrans";
                src = self;

                nativeBuildInputs = [pkgs.qt5.wrapQtAppsHook pkgs.copyDesktopItems];

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
                  wrapQtApp "$out/bin/lintrans"
                '';

                postInstall = ''
                  install -Dm0444 $src/src/lintrans/gui/assets/16.xpm $out/share/icons/hicolor/16x16/apps/lintrans.xpm
                  install -Dm0444 $src/src/lintrans/gui/assets/32.xpm $out/share/icons/hicolor/32x32/apps/lintrans.xpm
                  install -Dm0444 $src/src/lintrans/gui/assets/64.xpm $out/share/icons/hicolor/64x64/apps/lintrans.xpm
                  install -Dm0444 $src/src/lintrans/gui/assets/128.xpm $out/share/icons/hicolor/128x128/apps/lintrans.xpm
                '';

                desktopItems = [
                  (pkgs.makeDesktopItem {
                    name = "lintrans";
                    exec = meta.mainProgram;
                    icon = "lintrans";
                    desktopName = "lintrans";
                    comment = meta.description;
                    categories = ["Education"];
                    mimeTypes = ["application/lintrans-session"];
                  })
                ];

                meta = with pkgs.lib; {
                  description = "Linear transformation visualizer";
                  license = licenses.gpl3Only;
                  mainProgram = "lintrans";
                };
              };
          }
          // (let
            build-docs-type = type:
              pkgs.stdenvNoCC.mkDerivation {
                name = "lintrans-docs-${type}";
                src = self;

                nativeBuildInputs = [
                  (buildPython [
                    python-docs-libs
                    (_: [packages.native-python-package])
                  ])
                  pkgs.graphviz
                  pkgs.rsync
                ];

                buildPhase = ''
                  cd docs
                  make precompile
                  make ${type}
                  cd ..
                '';

                installPhase = ''
                  rsync -a --mkpath docs/build/${type}/ $out/share/doc
                '';
              };
          in {
            docs-html = build-docs-type "html";
            docs-dirhtml = build-docs-type "dirhtml";
            docs-singlehtml = build-docs-type "singlehtml";
          });

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
              enable = false;
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

            pytest-doctests = {
              enable = true;
              entry = "${python}/bin/python -m pytest";
              args = ["--doctest-modules" "--suppress-no-test-exit-code"];
              files = ''^src/.*\.py$'';
            };

            pydocstyle = {
              enable = true;
              entry = "${python}/bin/python -m pydocstyle";
              files = ''^(src|tests)/.*\.py$'';
            };

            pycodestyle = {
              enable = true;
              entry = "${python}/bin/python -m pycodestyle";
              files = ''^(src|tests)/.*\.py$'';
            };
          };
        };
      };
    };
}
