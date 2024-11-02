#!/usr/bin/env python3

from dataclasses import dataclass
import os
import sys
import subprocess
from enum import Enum

TMP_DIR = "/tmp"

PREFIX = "!"
L_BRACKET = "["
R_BRACKET = "]"
L_CURLY = "{"
R_CURLY = "}"

def usage():
    print(f"usage: python3 {sys.argv[0]} <template-file>");

def error(error):
    print(error + "\n", file=sys.stderr)
    usage()
    exit(1)

def eprint(s, color=None, **kwargs):
    if color is not None: print(f"\033[{color.value}m", end="", file=sys.stderr)
    print(s, file=sys.stderr, **kwargs)
    if color is not None: print("\033[0m", end="", file=sys.stderr)

def put(s):
    print(s, end="");

class Color(Enum):
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36


@dataclass
class Run:
    shell: str
    exit_code: int
    stdout: str
    stderr: str
    line: int


class RunnerState(Enum):
    DEFAULT       = 0,
    FOUND_START   = 1,
    IN_SHELL      = 2,
    IN_EXE        = 3,
    IN_SCRIPT     = 4,

class Runner:
    def __init__(self, path):
        self.line = 1
        self.path = path
        self.start = None
        self.cmd_start = None
        self.exe_start = None
        self.exe = None
        self.state = RunnerState.DEFAULT
        self.curly_count = 0
        self.runs = []
        if not os.path.isfile(path):
            error(f"'{path}' is not a file.")
        with open(path) as f:
            self.contents = f.read()

    def evaluate_cmd(self, cmd):
        sys.stdout.flush()
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.runs.append(Run(cmd, proc.returncode, proc.stdout, proc.stderr, self.line))
        put(proc.stdout.rstrip())

    def evaluate_script(self, exe, script):

        # Write script to a temporary file
        dir = f"{TMP_DIR}/txtx"
        os.makedirs(dir, exist_ok=True)
        script_path = f"{dir}/{exe}"
        with open(script_path, "w") as f:
            f.write(script)
        proc = subprocess.run([exe, script_path], capture_output=True, text=True)
        self.runs.append(Run(f"{exe} {script_path}", proc.returncode, proc.stdout, proc.stderr, self.line))
        put(proc.stdout.rstrip())

    def evaluate(self):
        i = 0
        while i < len(self.contents):
            c = self.contents[i]

            if c == "\n": self.line += 1

            if self.state == RunnerState.DEFAULT:
                if c == PREFIX:
                    self.state = RunnerState.FOUND_START
                    self.start = i
                else:
                    put(c)

            elif self.state == RunnerState.FOUND_START:
                if c == L_CURLY:
                    self.state = RunnerState.IN_SHELL
                    self.cmd_start = i+1
                    self.curly_count = 1
                elif c == L_BRACKET:
                    self.state = RunnerState.IN_EXE
                    self.exe_start = i+1
                # If we find double prefix, we the command is escaped
                elif c == PREFIX:
                    self.state = RunnerState.DEFAULT
                    put(c)
                    self.start = None
                else:
                    self.state = RunnerState.DEFAULT
                    put(self.contents[self.start:i+1])
                    self.start = None

            elif self.state == RunnerState.IN_SHELL:
                if c == L_CURLY:  self.curly_count += 1
                if c == R_CURLY: self.curly_count -= 1
                if self.curly_count == 0:
                    cmd = self.contents[self.cmd_start:i]
                    self.evaluate_cmd(cmd)
                    self.start = None
                    self.state = RunnerState.DEFAULT

            elif self.state == RunnerState.IN_EXE:
                if c == R_BRACKET:

                    self.exe = self.contents[self.exe_start:i]
                    self.exe_start = None

                    i += 1
                    if i >= len(self.contents): error(f"{self.path}:{self.line} Unexpected end of file.")
                    while self.contents[i].isspace(): i += 1

                    if self.contents[i] != L_CURLY:
                        error(f"{self.path}:{self.line} Expected '{L_CURLY}' after executable name.")
                    self.curly_count = 1
                    self.state = RunnerState.IN_SCRIPT
                    self.cmd_start = i+1
                elif c.isspace():
                    error(f"{self.path}:{self.line} Unexpected space in executable name.")

            elif self.state == RunnerState.IN_SCRIPT:
                if c == L_CURLY:  self.curly_count += 1
                if c == R_CURLY: self.curly_count -= 1

                if self.curly_count == 0:
                    self.state = RunnerState.DEFAULT
                    script = self.contents[self.cmd_start:i].rstrip()
                    self.evaluate_script(self.exe, script)

            # Increment cursor
            i += 1


    def check_errors(self):

        errored = False
        printed = False

        for run in self.runs:
            if run.exit_code == 0 and run.stderr.strip() != "":
                if not printed:
                    print("");
                    printed = True
                eprint(f"{self.path}:{run.line} [{run.shell}] produced output on stderr:")
                eprint(run.stderr.rstrip())

        for run in self.runs:
            if run.exit_code != 0:
                if not printed:
                    print("");
                    printed = True
                errored = True
                eprint(f"{self.path}:{run.line} [{run.shell}] failed with exit code {run.exit_code}:",
                       color=Color.RED)
                eprint(run.stderr.rstrip(), color=Color.RED)

        if errored: exit(1)


def main():
    [_, *args] = sys.argv

    if len(args) == 0: error("Please provide a file.")

    [path, *args] = args

    runner = Runner(path)
    runner.evaluate()
    runner.check_errors()

if __name__ == "__main__":
    main()
