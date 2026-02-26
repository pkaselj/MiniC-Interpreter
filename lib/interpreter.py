from lib.common_defs import *

class Interpreter:
    def Interpret(self, program : ProgramNode):
        self._InterpretProgram(program)

    def _InterpretProgram(self, program : ProgramNode):
        for stmt in program.Statements:
            print(self._InterpretStatement(stmt)) # ?
        
    def _InterpretStatement(self, stmt : StatementNode):
        if isinstance(stmt, ExprStmtNode):
            return self._InterpretExpression(stmt.Expression)
        raise MiniC_Error(f"Cannot intepret node [{type(stmt)}]")

    def _InterpretExpression(self, expr : ExpressionNode):
        if isinstance(expr, UnaryExpressionNode):
            return self._InterpretExpression(expr.child)
        elif isinstance(expr, BinaryExpressionNode):
            return self._InterpretBinaryExpression(expr)
        elif isinstance(expr, (StringExpressionNode, NumberExpressionNode, IdentifierExpressionNode)):
            return expr.Value
        raise MiniC_Error(f"Cannot intepret node [{type(expr)}]")
        
    def _InterpretBinaryExpression(self, expr : BinaryExpressionNode):
        left = self._InterpretExpression(expr.left)
        right = self._InterpretExpression(expr.right)
        match expr.op:
            case TokenType.OP_ADD: return (left + right)
            case TokenType.OP_SUB: return (left - right)
            case TokenType.OP_MUL: return (left * right)
            case TokenType.OP_DIV: return (left / right)
        raise MiniC_Error(f'Invalid operator [{expr.op.name}] while interpreting Binary Expression')