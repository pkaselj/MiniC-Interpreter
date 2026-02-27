from typing import Any, Dict

from lib.common_defs import *

class _Environment:
    symbols : Dict[str, Any]

    def __init__(self) -> None:
        self.symbols = {}

    def SetValue(self, id : str, value):
        self.symbols[id] = value

    def GetValue(self, id : str) -> Any:
        if id not in self.symbols:
            raise MiniC_Error(f'Symbol [{id}] not defined!')
        return self.symbols[id]

class Interpreter:
    _env : _Environment

    def __init__(self) -> None:
        self._env = _Environment()

    def Interpret(self, program : ProgramNode):
        self._InterpretProgram(program)

    def _InterpretProgram(self, program : ProgramNode):
        for stmt in program.Statements:
            print(self._InterpretStatement(stmt)) # ?
        
    def _InterpretStatement(self, stmt : StatementNode):
        if isinstance(stmt, ExprStmtNode):
            return self._InterpretExpression(stmt.Expression)
        elif isinstance(stmt, IfStatementNode):
            return self._InterpretIfStatement(stmt)
        elif isinstance(stmt, WhileStatementNode):
            return self._InterpretWhileStatement(stmt)
        elif isinstance(stmt, ForStatementNode):
            return self._InterpretForStatement(stmt)
        elif isinstance(stmt, BlockStatementNode):
            last_value = None
            for s in stmt.Statements:
                last_value = self._InterpretStatement(s)
            return last_value
        raise MiniC_Error(f"Cannot intepret node [{type(stmt)}]")
    
    def _InterpretIfStatement(self, stmt : IfStatementNode):
        if self._InterpretExpression(stmt.Condition) != 0:
            return self._InterpretStatement(stmt.BlockIf)
        elif stmt.BlockElse is not None:
            return self._InterpretStatement(stmt.BlockElse)

    def _InterpretForStatement(self, stmt : ForStatementNode):
        last_value = None
        if stmt.Initial:
            self._InterpretExpression(stmt.Initial)
        while self._InterpretExpression(stmt.EndCondition) != 0 if stmt.EndCondition else True:
            last_value = self._InterpretStatement(stmt.Block)
            if stmt.NextAction:
                self._InterpretExpression(stmt.NextAction)
        return last_value

    def _InterpretWhileStatement(self, stmt : WhileStatementNode):
        last_value = None
        while self._InterpretExpression(stmt.Condition) != 0:
            last_value = self._InterpretStatement(stmt.Block)
        return last_value

    def _InterpretExpression(self, expr : ExpressionNode):
        if isinstance(expr, UnaryExpressionNode):
            return self._InterpretUnaryExpression(expr)
        elif isinstance(expr, BinaryExpressionNode):
            return self._InterpretBinaryExpression(expr)
        elif isinstance(expr, (StringExpressionNode, NumberExpressionNode)):
            return expr.Value
        elif isinstance(expr, IdentifierExpressionNode):
            return self._env.GetValue(expr.Value)
        elif isinstance(expr, AssignExpressionNode):
            if not isinstance(expr.Left, AssignableTrait):
                raise MiniC_Error(f'Left hand side [{expr.Left.__class__}] is not assignable.')
            value = self._InterpretExpression(expr.Right)
            self._env.SetValue(expr.Left.Identifier(), value) # type: ignore
            return value
        raise MiniC_Error(f"Cannot intepret node [{type(expr)}]")
        
    def _InterpretBinaryExpression(self, expr : BinaryExpressionNode):
        left = self._InterpretExpression(expr.Left)
        right = self._InterpretExpression(expr.Right)
        match expr.Op:
            case TokenType.OP_ADD: return (left + right)
            case TokenType.OP_SUB: return (left - right)
            case TokenType.OP_MUL: return (left * right)
            case TokenType.OP_DIV: return (left / right)
            case TokenType.OP_EQ: return (left == right)
            case TokenType.OP_NEQ: return (left != right)
            case TokenType.OP_GT: return (left > right)
            case TokenType.OP_GTE: return (left >= right)
            case TokenType.OP_LT: return (left < right)
            case TokenType.OP_LTE: return (left <= right)
            case TokenType.OP_AND: return (left and right)
            case TokenType.OP_OR: return (left or right)
        raise MiniC_Error(f'Invalid operator [{expr.Op.name}] while interpreting Binary Expression')
    
    def _InterpretUnaryExpression(self, expr : UnaryExpressionNode):
        value = self._InterpretExpression(expr.Child)
        match expr.Op:
            case TokenType.OP_ADD: return value
            case TokenType.OP_SUB: return -1 * value
            case TokenType.OP_NOT: return not value
        raise MiniC_Error(f'Invalid operator [{expr.Op.name}] while interpreting Unary Expression')
