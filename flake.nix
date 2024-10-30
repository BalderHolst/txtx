{
    description = "txtx project flake";

    inputs.flake-utils.url = "github:numtide/flake-utils";

    outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = nixpkgs.legacyPackages.${system};
            in
            {
                packages = rec {
                    default = txtx;
                    txtx = pkgs.callPackage ./. {};
                };
                apps = rec {
                    default = txtx;
                    txtx = flake-utils.lib.mkApp { drv = self.packages.${system}.txtx; };
                };
                devShell = import ./shell.nix { inherit pkgs; };
            }
        );
}
