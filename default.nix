{ pkgs ? import <nixpkgs> {} }:
let
    config = builtins.fromTOML (builtins.readFile ./pyproject.toml);
in
with pkgs.python3Packages;
buildPythonPackage {
    pname = config.project.name;
    version = config.project.version;
    src = ./.;
    doCheck = false;
    pyproject = true;
    build-system = [
        setuptools
        wheel
    ];
}
