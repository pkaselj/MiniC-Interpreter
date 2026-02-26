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
        raise MiniC_Error(f"Cannot intepret node [{type(stmt)}]")

    def _InterpretExpression(self, expr : ExpressionNode):
        if isinstance(expr, UnaryExpressionNode):
            return self._InterpretExpression(expr.child)
        elif isinstance(expr, BinaryExpressionNode):
            return self._InterpretBinaryExpression(expr)
        elif isinstance(expr, (StringExpressionNode, NumberExpressionNode)):
            return expr.Value
        elif isinstance(expr, IdentifierExpressionNode):
            return self._env.GetValue(expr.Value)
        elif isinstance(expr, AssignExpressionNode):
            if not isinstance(expr.left, AssignableTrait):
                raise MiniC_Error(f'Left hand side [{expr.left.__class__}] is not assignable.')
            value = self._InterpretExpression(expr.right)
            self._env.SetValue(expr.left.Identifier(), value) # type: ignore
            return value
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