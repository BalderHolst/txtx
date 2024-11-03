# txtx
A simple script to generate READMEs and other text files by embedding shell and other scripts.

- [Example Use Case](#example-use-case)
- [Setup](#setup)
- [Nix](#nix)
- [Running a Template](#running-a-template)
- [Configuration](#configuration)

### Example Use Case
Say you want to show the file structure of your project in your README. Instead of manually writing out the structure, or running a command like `tree` and copying in the output, we can simply *embed* the `tree` command into the with the following syntax:
```
!{tree}
```

When compiling your README, the `tree` command will be executed and the output will be inserted in place of the `!{tree}` command, resulting in the following.

```
.
├── default.nix
├── examples
│   ├── python.mdx
│   ├── simple-flake
│   │   ├── flake.lock
│   │   └── flake.nix
│   ├── stderr.mdx
│   ├── time.mdx
│   └── txtx-source.mdx
├── flake.lock
├── flake.nix
├── LICENSE
├── Makefile
├── pyproject.toml
├── README.md
├── README.mdx
├── tasks.nix
└── txtx.py

3 directories, 16 files
```

This has the benefit of keeping your README up to date with your project structure, without having to manually update it.

This is just one use case, but your could also use it to include a file with the `cat` command, run a script to generate a table of contents, or embed do documentation extracted from doc-comments in your code. You could even download content from the web to be embedded.

For a concrete example, check out the [README.mdx](./README.mdx) which is used to generate this README or any of the other [examples](./examples/).

You can also use the following syntax to embed another language like python into your text file.
```
!(python){
    print("Hello from python!")
}
```

Or use it to execute multiple commands and embed the output.

```
!(bash){
    echo "Hello from bash!"
    echo "This computer is called $(hostname)"
    echo "The current time is $(date)"
    echo "Goodbye!"
}
```

Commands can be escaped by repeating the prefix (default: `!`) character.

## Setup
txtx is designed to be easy to setup. You can simply copy the `txtx.py` script into your project and start using it. It is now yours! Do whatever you want with it. It does not require any external dependencies.

### Nix
If you are using Nix, you can use the provided flake to add `txtx` to your project. Simply add the following to your `flake.nix` file.
```nix
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
```

### Running a Template
Simply run the `txtx.py` script with the file you want to generate as the first argument. The script will execute the file and emit the result to stdout.

```bash
python3 txtx.py input-file.txtx > README.txt
```

### Configuration
You can configure the txtx syntax using the cli arguments. Run `txtx.py --help` to see the available options.

```
usage: python3 ./txtx.py [OPTIONS] <template-file>

Options:
  --help, -h             Display this help message.
  --prefix <char>        Set the prefix character. Default is '!'
  --exe-parens <str>     Set the executable parentheses. Default is '()'
  --script-parens <str>  Set the script parentheses. Default is '{}'
```
