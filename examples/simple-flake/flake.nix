{
    inputs = {
        txtx.url = "github:BalderHolst/txtx";
        nixpkgs-stable.url = "github:NixOS/nixpkgs/24.05";
    };

    outputs = { nixpkgs, txtx, ... }:
    let
        system = "x86_64-linux";
        pkgs = import nixpkgs { inherit system; };
    in
    {
        # ...

        devShells.${system}.default = pkgs.mkShell {
            nativeBuildInputs = [ txtx.packages.${system}.txtx ];
        };
    };
}


