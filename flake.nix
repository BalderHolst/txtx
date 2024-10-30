{
    description = "txtx project flake";

    inputs.flake-utils.url = "github:numtide/flake-utils";

    outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.simpleFlake {
            inherit self nixpkgs;
            name = "txtx";
            overlay = ./overlay.nix;
            shell = ./shell.nix;
        };
}
