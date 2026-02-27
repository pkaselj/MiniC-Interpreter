import os

from lib.interpreter import Interpreter
from lib.lexer import Lexer
from lib.parser import Parser
from lib.common_defs import MiniC_Error

import argparse

def interpret_repl():
    input_string = ''
    interpreter = Interpreter()
    while True:
        input_string = input('> ')
        try:
            # print('==========================')
            tokens = Lexer().PerformLexing(input_string)
            # for token in tokens:
            #     print(token)
            # print('==========================')
            ast = Parser().PerformParsing(tokens)
            # print(ast.Pretty())
            # print('==========================')
            value = interpreter.Interpret(ast)
        except MiniC_Error as ex:
            print(f'Error: {ex}')

def interpret_file(file : str):
    if not os.path.exists(file):
        print(f'Could not find a file: {file}')
        return
    
    code = ''
    with open(file, 'r') as fp:
        code = fp.read()

    try:
        tokens = Lexer().PerformLexing(code)
        ast = Parser().PerformParsing(tokens)
        _ = Interpreter().Interpret(ast)
    except MiniC_Error as ex:
        print(f'Error: {ex}')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Mini-C language interpreter."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive mode (REPL)."
    )
    group.add_argument(
        "-f", "--file",
        type=str,
        metavar="FILENAME",
        help="Run the program from a file."
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.interactive:
        print("Starting interactive REPL...")
        interpret_repl()
    elif args.file:
        print(f"Running file: {args.file}")
        interpret_file(args.file)



