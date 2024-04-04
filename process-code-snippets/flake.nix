{
  description = "A simple program to process the code snippets in the lintrans write-up";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-parts.url = "github:hercules-ci/flake-parts";

    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    naersk = {
      url = "github:nix-community/naersk";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux"];
      perSystem = {system, ...}: let
        pkgs = import inputs.nixpkgs {
          inherit system;
          overlays = [(import inputs.rust-overlay)];
        };

        rust-toolchain = pkgs.rust-bin.stable.latest.default;

        naersk = pkgs.callPackage inputs.naersk {
          cargo = rust-toolchain;
          rustc = rust-toolchain;
        };

        lintrans = pkgs.fetchFromGitHub {
          owner = "DoctorDalek1963";
          repo = "lintrans";
          rev = "ce03f8021e60a85fe4c1966dae488b4fb6ee77ba";
          hash = "sha256-tHpXsHWgPDZXK9fgMQE6ze/t+t7gasK6l0gqkcJ9VjM=";
          leaveDotGit = true;
          deepClone = true;
        };

        git-config-bodge = pkgs.stdenvNoCC.mkDerivation {
          name = "git-config-bodge";
          dontUnpack = true;
          installPhase = ''
            mkdir -p $out/.config/git
            echo '[safe]' > $out/.config/git/config
            echo '    directory = "${lintrans}"' >> $out/.config/git/config
          '';
        };
      in rec {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [rust-toolchain];
        };

        packages = rec {
          default = process-code-snippets;

          process-code-snippets = naersk.buildPackage {
            src = ./.;
            postInstall = ''
              wrapProgram $out/bin/process-code-snippets \
                --set LINTRANS_DIR "${lintrans}" \
                --set XDG_CONFIG_HOME "${git-config-bodge}/.config"
            '';
            overrideMain = old: {
              nativeBuildInputs = old.nativeBuildInputs or [] ++ [pkgs.makeWrapper];
            };
          };
        };

        apps = rec {
          default = process-code-snippets;

          process-code-snippets = {
            type = "app";
            program = "${packages.process-code-snippets}/bin/process-code-snippets";
          };
        };
      };
    };
}
