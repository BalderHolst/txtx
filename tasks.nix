{ task-lib }:
with task-lib; 
let
    check-no-uncommited = msg: mkTask "check-no-uncommited" { script = ''
            git update-index --refresh > /dev/null
            git diff-index --quiet HEAD -- || {
                echo "${msg}"
                exit 1
            }
        '';
    };
in
{
    gen-readme = mkTask "gen-readme" { script = ''
            ./txtx.py README.mdx > README.md
        '';
    };
    pre-push-check = check-no-uncommited "Please commit all changes before pushing";
    gen-scripts = mkGenScriptsTask "gen-scripts";
}
