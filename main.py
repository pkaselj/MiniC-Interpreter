from lib.lexer import Lexer
from lib.parser import Parser
from lib.common_defs import MiniC_Error

if __name__ == '__main__':
    input_string = ''
    while input_string != 'x':
        input_string = input('> ')
        try:
            print('==========================')
            tokens = Lexer().PerformLexing(input_string)
            for token in tokens:
                print(token)
            print('==========================')
            ast = Parser().PerformParsing(tokens)
            print(ast.Pretty())
        except MiniC_Error as ex:
            print(f'Error: {ex}')



