from lib.lexer import Lexer
from lib.parser import Parser

if __name__ == '__main__':
    input_string = ''
    while input_string != 'x':
        input_string = input('> ')
        print('==========================')
        tokens = Lexer().PerformLexing(input_string)
        for token in tokens:
            print(token)
        print('==========================')
        ast = Parser().PerformParsing(tokens)
        print(ast.Pretty())



