{
    description = "txtx project flake";

    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/24.05";
        flake-utils.url = "github:numtide/flake-utils";
        task-gen = {
            url = "github:BalderHolst/task-gen.nix";
            inputs = {
                flake-utils.follows = "flake-utils";
                nixpkgs.follows = "nixpkgs";
            };
        };
    };

    outputs = { nixpkgs, flake-utils, task-gen, ... }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                task-lib = task-gen.lib.${system};
                pkgs = nixpkgs.legacyPackages.${system};
                tasks = import ./tasks.nix { inherit task-lib; };
            in
            rec {
                packages = rec {
                    default = txtx;
                    txtx = pkgs.callPackage ./. {};
                };
                overlays = {
                    default = final: prev: {
                        txtx = packages.txtx;
                    };
                };
                apps = rec {
                    default = txtx;
                    txtx = flake-utils.lib.mkApp { drv = packages.txtx; };
                    gen-scripts = with task-lib; mkGenScriptsApp {
                        "Makefile" = mkMakefile [tasks.gen-readme];
                        ".hooks/pre-push" = mkScript (mkSeq "pre-push" [
                            tasks.gen-readme
                            tasks.pre-push-check
                        ]);
                    };
                };
                devShell = pkgs.mkShell {
                    buildInputs = with pkgs; [
                        nodejs_22
                            tree-sitter
                            (python3.withPackages (python-pkgs: with python-pkgs; [
                                                   build
                            ]))
                    ] ++ (task-lib.mkScripts tasks);

                    shellHook = ''
                        # Use git hooks
                        git config core.hooksPath .hooks
                    '' + task-lib.mkShellHook tasks;
                };
            }
    );
}
