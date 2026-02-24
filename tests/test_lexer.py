# type: ignore

import unittest

from lib.lexer import Lexer
from lib.common_defs import Token, TokenType, Operator, MiniC_Error

# Used for testing only
class X: # Don't care about value
    name = "<Don't care>"
    value = "<Don't care>"
    strlen = "<Don't care>"

def unittest_token_eq(self, value) -> bool:
    if not isinstance(value, Token):
        return False
    
    return (isinstance(value.token_type, X) or self.token_type == value.token_type) and \
           (isinstance(value.value,      X) or self.value      == value.value) and \
           (isinstance(value.strlen,     X) or self.strlen     == value.strlen)

class TestMiniCLexer(unittest.TestCase):
    def setUp(self) -> None:
        self.lexer = Lexer()
        Token.__eq__ = unittest_token_eq

    # ------------------
    # Empty
    # ------------------
    def test_empty(self):
        tokens = self.lexer.PerformLexing('')
        self.assertEqual(tokens, [])

    # ------------------
    # Whitespace
    # ------------------
    def test_whitespace(self):
        tokens = self.lexer.PerformLexing('         \t\n     \r    ')
        self.assertEqual(tokens, [])

    # ------------------
    # Numbers
    # ------------------
    def test_num_int(self):
        t = self.lexer.PerformLexing('123')
        self.assertTrue(t[0].token_type == TokenType.NUM)
        self.assertTrue(t[0].value == 123)

    def test_num_frac(self):
        t = self.lexer.PerformLexing('123.456')
        self.assertTrue(t[0].token_type == TokenType.NUM)
        self.assertTrue(t[0].value == 123.456)

    def test_num_sci(self):
        t = self.lexer.PerformLexing('123.456e-3')
        self.assertTrue(t[0].token_type == TokenType.NUM)
        self.assertTrue(t[0].value == 123.456e-3)

    # ------------------
    # Operators
    # ------------------
    def test_op_singlechar(self):
        t = self.lexer.PerformLexing('+ - / * > <')
        tt = [x.token_type == TokenType.OP for x in t]
        self.assertTrue(all(tt))

        tv = [x.value for x in t]
        self.assertEqual(tv,
            [
                Operator.ADD,
                Operator.SUB,
                Operator.DIV,
                Operator.MUL,
                Operator.GT,
                Operator.LT,
            ]
        )
    
    def test_op_assign(self):
        t = self.lexer.PerformLexing('=')
        self.assertTrue(t[0].token_type == TokenType.ASSIGN)
    
    def test_op_multichar(self):
        t = self.lexer.PerformLexing('== != >= <=')
        tt = [x.token_type == TokenType.OP for x in t]
        self.assertTrue(all(tt))

        tv = [x.value for x in t]
        self.assertEqual(tv,
            [
                Operator.EQ,
                Operator.NEQ,
                Operator.GTE,
                Operator.LTE,
            ]
        )

    # ------------------
    # Punctuation
    # ------------------
    def test_punctuation(self):
        t = self.lexer.PerformLexing('(){};')
        tt = [x.token_type for x in t]
        self.assertEqual(tt,
            [
                TokenType.O_PAREN,
                TokenType.C_PAREN,
                TokenType.O_BRACE,
                TokenType.C_BRACE,
                TokenType.DELIM
            ]
        )

    # ------------------
    # Identifiers
    # ------------------
    def test_ident(self):
        t = self.lexer.PerformLexing('hello world n1c3 t0 m33t you')
        tt = [x.token_type == TokenType.ID for x in t]
        self.assertTrue(all(tt))
        tv = [x.value for x in t]
        self.assertEqual(
            tv,
            ['hello', 'world', 'n1c3', 't0', 'm33t', 'you']
        )

    def test_kwd(self):
        t = self.lexer.PerformLexing('function return if else while for')
        tt = [x.token_type for x in t]
        self.assertEqual(tt,
           [
                TokenType.K_FN,
                TokenType.K_RET,
                TokenType.K_IF,
                TokenType.K_ELSE,
                TokenType.K_WHILE,
                TokenType.K_FOR
           ]
        )

    # ------------------
    # Errors
    # ------------------
    def test_invalid_char(self):
        with self.assertRaises(MiniC_Error):
            self.lexer.PerformLexing('`')

    # ------------------
    # Mixed expressions
    # ------------------
    def test_expr_1(self):
        t = self.lexer.PerformLexing('x = yz + 3;')
        self.assertEqual(t,
            [
                Token(TokenType.ID, 'x', 1),
                Token(TokenType.ASSIGN, X(), 1),
                Token(TokenType.ID, 'yz', 2),
                Token(TokenType.OP, Operator.ADD, 1),
                Token(TokenType.NUM, 3, 1),
                Token(TokenType.DELIM, X(), 1),
            ]
        )

    def test_expr_2(self):
        t = self.lexer.PerformLexing('if(x == 3) { return x / 2.3; }')
        self.assertEqual(t,
            [
                Token(TokenType.K_IF, X(), 2),
                Token(TokenType.O_PAREN, X(), 1),
                Token(TokenType.ID, 'x', 1),
                Token(TokenType.OP, Operator.EQ, 2),
                Token(TokenType.NUM, 3, 1),
                Token(TokenType.C_PAREN, X(), 1),
                Token(TokenType.O_BRACE, X(), 1),
                Token(TokenType.K_RET, X(), 6),
                Token(TokenType.ID, 'x', 1),
                Token(TokenType.OP, Operator.DIV, 1),
                Token(TokenType.NUM, 2.3, 3),
                Token(TokenType.DELIM, X(), 1),
                Token(TokenType.C_BRACE, X(), 1),
            ]
        )

    def test_expr_3(self):
        t = self.lexer.PerformLexing('while(i!=   1){  name = "sample_string"; }')
        self.assertEqual(t,
            [
                Token(TokenType.K_WHILE, X(), 5),
                Token(TokenType.O_PAREN, X(), 1),
                Token(TokenType.ID, 'i', 1),
                Token(TokenType.OP, Operator.NEQ, 2),
                Token(TokenType.NUM, 1, 1),
                Token(TokenType.C_PAREN, X(), 1),
                Token(TokenType.O_BRACE, X(), 1),
                Token(TokenType.ID, 'name', 4),
                Token(TokenType.ASSIGN, X(), 1),
                Token(TokenType.STR, 'sample_string', 13),
                Token(TokenType.DELIM, X(), 1),
                Token(TokenType.C_BRACE, X(), 1),
            ]
        )


