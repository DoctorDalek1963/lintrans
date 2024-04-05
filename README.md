# lintrans write-up

![Compile PDF](https://github.com/DoctorDalek1963/lintrans/actions/workflows/compile-pdf.yaml/badge.svg)

This branch contains the write-up of the `lintrans` project for my A Level Computer Science NEA (Non-Exam Assessment).
The actual source code of the project is found in the [`main`](https://github.com/DoctorDalek1963/lintrans/tree/main) branch.

The compiled PDF can be downloaded from [my GitHub pages site](https://doctordalek1963.github.io/lintrans/lintrans.pdf).

## How to build

The only supported way to build the PDF is by install [Nix](https://nixos.org/) (make sure to enable flakes) and run
`nix build`. This will build everything in a fully reproducible way and create `./result/lintrans.{pdf,zip}`. You could
use `nix develop` and run `just build`, and that might work but it's not supported. You may have some font issues.
