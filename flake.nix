{
  description = "lintrans, the linear transformation visualizer";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ {
    self,
    flake-parts,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux"];
      perSystem = {pkgs, ...}: let
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
          # p.pytest-custom-exit-code
          p.pytest-xvfb
          p.pyqt5-stubs
          p.toml
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
        };

        packages = rec {
          default = native-python-package;

          native-python-package = pkgs.python311.pkgs.buildPythonPackage {
            name = "lintrans-native-python-package";
            src = self;
            format = "pyproject";

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

                propagatedBuildInputs = [
                  lintransPython
                  native-python-package
                ];

                dontUnpack = true;

                installPhase = let
                  bin = pkgs.writeShellScriptBin "lintrans" ''
                    ${lintransPython}/bin/python -m lintrans
                  '';
                in
                  # bash
                  ''
                    runHook preInstall

                    mkdir -p $out/bin
                    cp ${bin}/bin/lintrans $out/bin/lintrans

                    runHook postInstall
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
      };
    };
}
