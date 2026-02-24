from .common_defs import Operator, Token, TokenType, MiniC_Error
from typing import Generator, List, Tuple
import re

class Lexer:
    def PerformLexing(self, input_stream : str) -> List[Token]:
        i = 0
        tokens = []
        while i < len(input_stream):
            s = input_stream[i:]

            if t := self._ParseWhitespace(s):
                i += t.strlen
                continue

            # TODO: Comments

            if t := self._ParseString(s):
                i += t.strlen + 2 # Strlen returns size without quotes
                tokens.append(t)
                continue

            if t := self._ParseOperator(s):
                i += t.strlen
                tokens.append(t)
                continue

            if t := self._ParseNumber(s):
                i += t.strlen
                tokens.append(t)
                continue

            if t := self._ParseIdentifierOrKeyword(s):
                i += t.strlen
                tokens.append(t)
                continue

            if t := self._ParsePunctuation(s):
                i += t.strlen
                tokens.append(t)
                continue

            raise MiniC_Error(f"Invalid token '{input_stream[i]}' index '{i}'")

        return tokens

    def _ParseNumber(self, s : str) -> Token | None:
        if not s[0].isnumeric():
            return None
        
        if (match := re.match(r'\d+(\.\d+)?(e(\+|\-)?\d+)?', s)) is None:
            return None
        
        return Token(
            token_type=TokenType.NUM,
            value = float(match.group(0)),
            strlen = len(match.group(0))
        )
    
    def _ParseWhitespace(self, s : str) -> Token | None:
        if not s[0].isspace():
            return None
        
        i = 0
        while i < len(s):
            if s[i].isspace():
                i += 1
                continue
            else:
                break

        return Token(
            TokenType.WSPC,
            None,
            i
        )
    
    def _ParseOperator(self, s : str) -> Token | None:
        t = Token(
            TokenType.OP,
            None,
            1
        )

        if len(s) > 1:
            match s[0:2]:
                case '==':
                    t.value = Operator.EQ
                    t.strlen = 2
                    return t
                case '!=':
                    t.value = Operator.NEQ
                    t.strlen = 2
                    return t
                case '>=':
                    t.value = Operator.GTE
                    t.strlen = 2
                    return t
                case '<=':
                    t.value = Operator.LTE
                    t.strlen = 2
                    return t

        match s[0]:
            case '=':
                t.token_type = TokenType.ASSIGN
            case '+':
                t.value = Operator.ADD
            case '-':
                t.value = Operator.SUB
            case '*':
                t.value = Operator.MUL
            case '/':
                t.value = Operator.DIV
            case '>':
                t.value = Operator.GT
            case '<':
                t.value = Operator.LT
            case _:
                return None

        return t    

    def _ParseString(self, s : str) -> Token | None:
        if s[0] != '"':
            return None    
        elif len(s) < 2:
            return None
        
        i = 1
        for i in range(1, len(s)):
            if s[i] == '"':
                return Token(
                    TokenType.STR,
                    s[1:i],
                    i-1 # Size witout quotes
                )
            
        return None
    
    _id_kwd_map = {
        'function' : TokenType.K_FN,
        'return'   : TokenType.K_RET,
        'if'       : TokenType.K_IF,
        'else'     : TokenType.K_ELSE,
        'while'    : TokenType.K_WHILE,
        'for'      : TokenType.K_FOR,
    }

    def _ParseIdentifierOrKeyword(self, s : str) -> Token | None:
        if not s[0].isascii():
            return None
        
        if (m := re.match(r'(\w|_)[\w\d_]*', s)) is None:
            return None
        
        v = m.group(0)

        if v not in self._id_kwd_map:
            return Token(
                TokenType.ID,
                v,
                len(v)
            )

        return Token (
            token_type = self._id_kwd_map[v],
            value = v,
            strlen = len(v)
        )
    

    _punc_map = {
        '(' : TokenType.O_PAREN,
        ')' : TokenType.C_PAREN,
        # '[' : TokenType.O_BRACK,
        # ']' : TokenType.C_BRACK,
        '{' : TokenType.O_BRACE,
        '}' : TokenType.C_BRACE,
        ';' : TokenType.DELIM
    }

    def _ParsePunctuation(self, s : str) -> Token | None:
        if s[0] in self._punc_map:
            return Token(
                self._punc_map[s[0]],
                None,
                1
            )
        
        return None
        


