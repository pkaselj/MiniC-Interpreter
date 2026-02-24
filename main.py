from lib.lexer import Lexer

if __name__ == '__main__':
    input_string = ''
    while input_string != 'x':
        input_string = input('> ')
        print('==========================')
        tokens = Lexer().PerformLexing(input_string)
        for token in tokens:
            print(token)
        print('==========================')


