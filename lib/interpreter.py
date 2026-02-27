from typing import Any, Dict

from lib.common_defs import *

class _StackFrame:
    symbols : Dict[str, Any]
    context : str

    def __init__(self, ctx : str) -> None:
        self.symbols = {}
        self.context = ctx

    def SetValue(self, id : str, value):
        self.symbols[id] = value

    def HasSymbol(self, id : str) -> bool:
        return id in self.symbols.keys()

    def GetValue(self, id : str) -> Any:
        if id not in self.symbols:
            raise MiniC_Error(f'Symbol [{id}] not defined!')
        return self.symbols[id]

class _CallStack:
    _cs : List[_StackFrame] = []

    def __init__(self) -> None:
        self._cs.append(_StackFrame('.global')) # Append global stack frame

    def SetValue(self, id : str, value):
        self._cs[-1].SetValue(id, value)

    def GetValue(self, id : str) -> Any:
        for sf in reversed(self._cs):
            if sf.HasSymbol(id):
                return sf.GetValue(id)
        raise MiniC_Error(f'Symbol [{id}] not defined in any stack frame.')
    
    def _CurrentStackFrame(self):
        return self._cs[-1]

    def InitializeStackFrame(self, fn : '_Function', args : List[Any]):
        self._cs.append(_StackFrame(fn._Id))
        fn.InitializeEnvironment(self._CurrentStackFrame(), args)

    def PopStackFrame(self):
        self._cs.pop()

    def __str__(self) -> str:
        raise NotImplementedError()
    
    
class _Function:
    _Id : str
    _Params : List[str]
    _Block : StatementNode

    def __init__(self, id : str, params : List[str], block : StatementNode) -> None:
        self._Id = id
        self._Params = params
        self._Block = block

    def __hash__(self) -> int:
        return self._Id.__hash__()
    
    def __eq__(self, value: object) -> bool:
        return self.__hash__() == value.__hash__()

    # def GetParamCount(self) -> int:
    #     return len(self._Params)
    
    def InitializeEnvironment(self, env : _StackFrame, args : List[Any]):
        if len(self._Params) != len(args):
            raise MiniC_Error(f'Error when calling function [{self._Id}]. Expected [{len(self._Params)}] arguments, got [{len(args)}]')
        for i, v in enumerate(args):
            local_id = self._Params[i]
            env.SetValue(local_id, v)

    def GetExecBlock(self) -> StatementNode:
        return self._Block

class _FunctionTable:
    _fn_table : Dict[str, _Function]

    def __init__(self) -> None:
        self._fn_table = {}

    # TODO: Function overriding
    def RegisterFunction(self, fn : _Function):
        if fn._Id in self._fn_table:
            raise MiniC_Error(f"Function '{fn._Id}' already defined.")
        self._fn_table[fn._Id] = fn

    def LookupFunction(self, sym : str) -> _Function | None:
        if sym not in self._fn_table:
            return None
        return self._fn_table[sym]

class Interpreter:
    _callstack : _CallStack
    _fn_table : _FunctionTable

    def __init__(self) -> None:
        # Initialize global stack frame
        self._callstack = _CallStack()
        self._fn_table = _FunctionTable()

    def Interpret(self, program : ProgramNode):
        self._InterpretProgram(program)

    def _InterpretProgram(self, program : ProgramNode):
        for fndef in program.FnDefinitions:
            self._InterpretFnDefition(fndef)
        for stmt in program.Statements:
            print(self._InterpretStatement(stmt)) # ?

    def _InterpretFnDefition(self, fndef : FnDefinitionStatementNode):
        id = fndef.Symbol
        if not isinstance(id, SymbolTrait):
            raise MiniC_Error(f'Function definition of [{id}] invalid. Identifier not valid symbol name.')
        params = [x.Symbol() for x in fndef.Params]
        fn = _Function(id.Symbol(), params, fndef.Block)
        self._fn_table.RegisterFunction(fn)
        
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
            return self._callstack.GetValue(expr.Value)
        elif isinstance(expr, AssignExpressionNode):
            if not isinstance(expr.Left, SymbolTrait):
                raise MiniC_Error(f'Left hand side [{expr.Left.__class__}] is not assignable.')
            value = self._InterpretExpression(expr.Right)
            self._callstack.SetValue(expr.Left.Symbol(), value) # type: ignore
            return value
        elif isinstance(expr, FnCallExpressionNode):
            if not isinstance(expr.Symbol, SymbolTrait):
                raise MiniC_Error(f'Cannot call function "{expr.Symbol}" - not a valid symbol name.')
            sym = expr.Symbol.Symbol()
            _fn = self._fn_table.LookupFunction(sym)
            if not _fn:
                raise MiniC_Error(f'Could not call function "{sym}" - function not defined.')
            args = [self._InterpretExpression(x) for x in expr.Args]
            self._callstack.InitializeStackFrame(_fn, args)
            value = self._InterpretStatement(_fn.GetExecBlock())
            self._callstack.PopStackFrame()
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
