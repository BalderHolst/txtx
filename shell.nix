{ pkgs ? import <nixpkgs> }:
pkgs.mkShell {
    buildInputs = with pkgs; [
        nodejs_22
        tree-sitter
        (python3.withPackages (python-pkgs: with python-pkgs; [
            build
        ]))
    ];

    # Use git hooks
    shellHook = ''
        git config core.hooksPath .hooks
    '';
}
