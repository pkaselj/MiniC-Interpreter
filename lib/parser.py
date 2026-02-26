from lib.common_defs import *

# TODO: Operator precedence, unary minus



# -------------
# GRAMMAR BNF
# -------------

# <S> ::= <stmt> <S> | E

# <stmt> ::= <assign> ";"
# <assign> ::= <id> "=" <assign> | <expr> 
# <expr> ::= <term> (("+" | "-") <term>)*
# <term> ::= <factor> (("*" | "/") <factor>)*
# <factor> ::= <number> | <id> | "(" <expr> ")"

# -------------

# ---------------- SEMANTIC HELPERS

def _IsAssignable(node : Node) -> bool:
    return isinstance(node, AssignableTrait)

# ---------------- PARSER IMPLEMENTATION

class Parser:
    _pos : int = 0
    _tokens = []

    def _peek(self) -> Token | None:
        if self._pos >= len(self._tokens):
            return None
        return self._tokens[self._pos]
    
    def _advance(self) -> Token | None:
        if self._pos >= len(self._tokens):
            return None
        t = self._tokens[self._pos]
        self._pos += 1
        return t
    
    def _match(self, *t : TokenType) -> Token | None:
         if self._pos >= len(self._tokens):
            return None
         
         tok = self._tokens[self._pos]
         if tok.token_type in t:
            self._advance()
            return tok
         return None
    
    def _expect(self, *t : TokenType) -> Token:
        tok = self._match(*t)
        if not tok:
            raise MiniC_Error(f"Parser: At index '{self._pos}' expected '{", ".join([x.name for x in t])}', got '{self._peek()}'")
        return tok

    def PerformParsing(self, token_stream : List[Token]) -> ProgramNode:
        self._pos = 0
        self._tokens = token_stream
        return self._ParseProgram()

    def _ParseProgram(self) -> ProgramNode:
        statements = []
        while self._peek() is not None:
            statements.append(self._ParseStatement())
        return ProgramNode(statements)
    
    def _ParseStatement(self) -> StatementNode:
        expr = self._ParseAssign()
        self._expect(TokenType.DELIM)
        return ExprStmtNode(expr)
    
    def _ParseAssign(self) -> ExpressionNode:
        node = self._ParseExpression()
        if self._match(TokenType.ASSIGN):
            if not _IsAssignable(node):
                raise MiniC_Error(f'Could not assign to node of type: [{type(node)}]')
            right = self._ParseAssign()
            node = AssignExpressionNode(node, right) # type: ignore
        return node
            
    def _ParseExpression(self) -> ExpressionNode:
        node = self._ParseTerm()
        while op := self._match(TokenType.OP_ADD, TokenType.OP_SUB):
            right = self._ParseTerm()
            node = BinaryExpressionNode(node, op.token_type, right)
        return node
    
    def _ParseTerm(self) -> ExpressionNode:
        node = self._ParseFactor()
        while op := self._match(TokenType.OP_MUL, TokenType.OP_DIV):
            right = self._ParseFactor()
            node = BinaryExpressionNode(node, op.token_type, right)
        return node

    def _ParseFactor(self) -> ExpressionNode:
        id = self._match(TokenType.ID)
        if id:
            return IdentifierExpressionNode(id.value)
        num = self._match(TokenType.NUM)
        if num:
            return NumberExpressionNode(num.value)
        _string = self._match(TokenType.STR)
        if _string:
            return StringExpressionNode(_string.value)
        open_par = self._expect(TokenType.O_PAREN)
        expr = self._ParseExpression()
        close_par = self._expect(TokenType.C_PAREN)
        return expr

    