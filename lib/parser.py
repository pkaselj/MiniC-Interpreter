from lib.common_defs import *

# ---------------- SEMANTIC HELPERS

def _IsAssignable(node : Node) -> bool:
    return isinstance(node, SymbolTrait)

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
        fndefs = []
        while (t := self._peek()) and t.token_type == TokenType.K_FN:
            fndefs.append(self._ParseFnDefinition())
        while (t := self._peek()):  
            statements.append(self._ParseStatement())
        return ProgramNode(fndefs, statements)
    
    def _ParseFnDefinition(self) -> StatementNode:
        self._expect(TokenType.K_FN)
        sym = self._expect(TokenType.ID)
        sym = IdentifierExpressionNode(sym.value)
        self._expect(TokenType.O_PAREN)
        params = []
        while (t := self._peek()) and t.token_type != TokenType.C_PAREN:
            param = self._expect(TokenType.ID)
            param = IdentifierExpressionNode(param.value)
            params.append(param)
            self._match(TokenType.K_COMMA)
        self._expect(TokenType.C_PAREN)
        block = self._ParseBlock()
        return FnDefinitionStatementNode(sym, params, block)


    def _ParseStatement(self) -> StatementNode:
        t = self._peek()
        if not t:
            raise MiniC_Error(f'No tokens to parse in _ParseStatement()')
        if t.token_type == TokenType.K_IF: # type: ignore
            return self._ParseIfStatement()
        elif t.token_type == TokenType.K_WHILE:
            return self._ParseWhileStatement()
        elif t.token_type == TokenType.K_FOR:
            return self._ParseForStatement()
        expr = self._ParseExpression()
        self._expect(TokenType.DELIM)
        return ExprStmtNode(expr)
    
    def _ParseIfStatement(self) -> StatementNode:
        self._expect(TokenType.K_IF)
        self._expect(TokenType.O_PAREN)
        cond = self._ParseExpression()
        self._expect(TokenType.C_PAREN)
        block_if = self._ParseBlock()
        block_else = None
        if self._match(TokenType.K_ELSE):
            block_else = self._ParseBlock()
        return IfStatementNode(cond, block_if, block_else)
    
    def _ParseWhileStatement(self) -> StatementNode:
        self._expect(TokenType.K_WHILE)
        self._expect(TokenType.O_PAREN)
        cond = self._ParseExpression()
        self._expect(TokenType.C_PAREN)
        block = self._ParseBlock()
        return WhileStatementNode(cond, block)
    
    def _ParseForStatement(self) -> StatementNode:
        initial = None
        end_cond = None
        next_action = None
        self._expect(TokenType.K_FOR)
        self._expect(TokenType.O_PAREN)
        if (t := self._peek()) and t.token_type != TokenType.DELIM:
            initial = self._ParseExpression()
        self._expect(TokenType.DELIM)
        if (t := self._peek()) and t.token_type != TokenType.DELIM:
            end_cond = self._ParseExpression()
        self._expect(TokenType.DELIM)
        if (t := self._peek()) and t.token_type != TokenType.C_PAREN:
            next_action = self._ParseExpression()
        self._expect(TokenType.C_PAREN)
        block = self._ParseBlock()
        return ForStatementNode(initial, end_cond, next_action, block)
    
    def _ParseBlock(self) -> StatementNode:
        self._expect(TokenType.O_BRACE)
        node = BlockStatementNode([])
        while not self._match(TokenType.C_BRACE):
            node.Statements.append(self._ParseStatement())
        return node
    
    def _ParseExpression(self) -> ExpressionNode:
        node = self._ParseAsignee()
        if self._match(TokenType.ASSIGN):
            if not _IsAssignable(node):
                raise MiniC_Error(f'Could not assign to node of type: [{type(node)}]')
            right = self._ParseExpression()
            node = AssignExpressionNode(node, right) # type: ignore
        return node
    
    def _ParseAsignee(self) -> ExpressionNode:
        return self._ParseLogicalOR()
    
    def _ParseLogicalOR(self) -> ExpressionNode:
        node = self._ParseLogicalAND()
        while (t := self._peek()) and t.token_type == TokenType.OP_OR:
            self._expect(TokenType.OP_OR)
            right = self._ParseLogicalAND()
            node = BinaryExpressionNode(node, TokenType.OP_OR, right)
        return node
    
    def _ParseLogicalAND(self) -> ExpressionNode:
        node = self._ParseComparee()
        while (t := self._peek()) and t.token_type == TokenType.OP_AND:
            self._expect(TokenType.OP_AND)
            right = self._ParseComparee()
            node = BinaryExpressionNode(node, TokenType.OP_AND, right)
        return node
            
    def _ParseComparee(self) -> ExpressionNode:
        node = self._ParseAdditive()
        while op := self._match(
            TokenType.OP_EQ,
            TokenType.OP_NEQ,
            TokenType.OP_GT,
            TokenType.OP_GTE,
            TokenType.OP_LT,
            TokenType.OP_LTE):

            right = self._ParseAdditive()
            node = BinaryExpressionNode(node, op.token_type, right)
        return node
    
    def _ParseAdditive(self) -> ExpressionNode:
        node = self._ParseTerm()
        while op := self._match(TokenType.OP_ADD, TokenType.OP_SUB):
            right = self._ParseTerm()
            node = BinaryExpressionNode(node, op.token_type, right)
        return node
    
    def _ParseTerm(self) -> ExpressionNode:
        node = self._ParseUnary()
        while op := self._match(TokenType.OP_MUL, TokenType.OP_DIV):
            right = self._ParseUnary()
            node = BinaryExpressionNode(node, op.token_type, right)
        return node

    def _ParseUnary(self) -> ExpressionNode:
        if t := self._match(TokenType.OP_ADD, TokenType.OP_SUB, TokenType.OP_NOT):
            base = self._ParseUnary()
            return UnaryExpressionNode(base, t.token_type)
        return self._ParseFnCall()

    def _ParseFnCall(self) -> ExpressionNode:
        node = self._ParsePrimary()
        while (nt := self._peek()) and nt.token_type == TokenType.O_PAREN:
            self._expect(TokenType.O_PAREN)
            params = []
            while (t := self._peek()) and t.token_type != TokenType.C_PAREN:
                param = self._ParseExpression()
                params.append(param)
                self._match(TokenType.K_COMMA)
            self._expect(TokenType.C_PAREN)
            node = FnCallExpressionNode(node, params)
        return node

    def _ParsePrimary(self) -> ExpressionNode:
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

    