from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, List, TypeVar, Union

# -------------
# General
# -------------

class MiniC_Error(Exception):
    pass

# -------------
# Lexer
# -------------

class TokenType(Enum):
    NUM     = auto()
    STR     = auto()
    # BOOL    = auto()
    OP_NOT  = auto() # !
    OP_OR   = auto() # ||
    OP_AND  = auto() # &&
    OP_ADD  = auto() # +
    OP_SUB  = auto() # -
    OP_MUL  = auto() # *
    OP_DIV  = auto() # /
    OP_EQ   = auto() # ==
    OP_NEQ  = auto() # !=
    OP_GT   = auto() # >
    OP_LT   = auto() # <
    OP_GTE  = auto() # >=
    OP_LTE  = auto() # <=
    ID      = auto()
    ASSIGN  = auto() # =
    WSPC    = auto()
    K_FN    = auto()
    K_RET   = auto()
    K_IF    = auto()
    K_FOR   = auto()
    K_ELSE  = auto()
    K_WHILE = auto()
    K_COMMA = auto() # ,
    O_PAREN = auto() # (  
    C_PAREN = auto() # )
    # O_BRACK = auto() # [ 
    # C_BRACK = auto() # ]
    O_BRACE = auto() # {
    C_BRACE = auto() # }
    DELIM   = auto() # ;


T = TypeVar('T')
@dataclass
class Token(Generic[T]):
    token_type : TokenType
    value : T
    strlen : int

    def __str__(self) -> str:
        return f'{self.token_type.name}=[{self.value}] len={self.strlen}'
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Token):
            return False
        
        return self.token_type == value.token_type and \
               self.value      == value.value and \
               self.strlen     == value.strlen

# -------------
# Parser
# -------------

# --- Utils

def _FormatIndented(indent : int, line : str):
    return f'{" " * indent}{line}\n'

# --- Base Class

class Node(ABC):
    def Pretty(self, indent=0) -> str:
        raise NotImplementedError()
    
class SymbolTrait(ABC):
    def Symbol(self) -> str:
        raise NotImplementedError()

# -- Expression Nodes

class ExpressionNode(Node):
    pass

@dataclass
class FnCallExpressionNode(ExpressionNode):
    Symbol : ExpressionNode
    Args : List[ExpressionNode]
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += 'CALL: ' + self.Symbol.Pretty(indent + 1)
        for i, arg in enumerate(self.Args):
            s += '{i}: ' + arg.Pretty(indent + 1)
        return s

@dataclass
class AssignExpressionNode(ExpressionNode):
    Left : SymbolTrait # Assignable node
    Right : ExpressionNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent + 1, f'ASSIGN "{self.Left}"')
        s += self.Right.Pretty(indent + 1)
        return s

@dataclass
class UnaryExpressionNode(ExpressionNode):
    Child : ExpressionNode
    Op : TokenType
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent + 1, self.Op.name)
        s += self.Child.Pretty(indent + 1)
        return s

@dataclass 
class BinaryExpressionNode(ExpressionNode):
    Left : ExpressionNode
    Op : TokenType #TODO: Change to custom operator type ?
    Right : ExpressionNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += self.Left.Pretty(indent + 1)
        s += _FormatIndented(indent + 1, self.Op.name)
        s += self.Right.Pretty(indent + 1)
        return s
    
@dataclass
class IdentifierExpressionNode(ExpressionNode, SymbolTrait):
    Value : str
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent, f'# {self.Value}')
        return s
    def Symbol(self) -> str:
        return self.Value
    
@dataclass
class NumberExpressionNode(ExpressionNode):
    Value : float
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent, f'# {self.Value}')
        return s
    
@dataclass
class StringExpressionNode(ExpressionNode):
    Value : str
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent, f'# {self.Value}')
        return s
    
# class NoOpExpressionNode(ExpressionNode):
#     def Pretty(self, indent=0) -> str:
#         return _FormatIndented(indent, self.__class__.__name__)

# -- Statement Nodes

class StatementNode(Node):
    pass

@dataclass
class ExprStmtNode(StatementNode):
    Expression : ExpressionNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += self.Expression.Pretty(indent + 1)
        return s
    
@dataclass
class IfStatementNode(StatementNode):
    Condition : ExpressionNode
    BlockIf : StatementNode
    BlockElse : StatementNode | None
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += 'IF: ' + self.Condition.Pretty(indent + 1)
        s += 'THEN: ' + self.BlockIf.Pretty(indent + 1)
        if self.BlockElse:
            s += 'ELSE: ' + self.BlockIf.Pretty(indent + 1)
        else:
            s += _FormatIndented(indent + 1, 'ELSE: None')
        return s
    
@dataclass
class ForStatementNode(StatementNode):
    Initial : ExpressionNode | None
    EndCondition : ExpressionNode | None
    NextAction : ExpressionNode | None
    Block : StatementNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += 'FOR: ' + self.Initial.Pretty(indent + 1) if self.Initial else "<NOOP>"
        s += ';    ' + self.EndCondition.Pretty(indent + 1) if self.EndCondition else "<NOOP>"
        s += ';    ' + self.NextAction.Pretty(indent + 1) if self.NextAction else "<NOOP>"
        s += 'THEN: ' + self.Block.Pretty(indent + 1)
        return s
    
@dataclass
class WhileStatementNode(StatementNode):
    Condition : ExpressionNode
    Block : StatementNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += 'WHILE: ' + self.Condition.Pretty(indent + 1)
        s += 'THEN: ' + self.Block.Pretty(indent + 1)
        return s
    
@dataclass
class BlockStatementNode(StatementNode):
    Statements : List[StatementNode]
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        for stmt in self.Statements:
            s += stmt.Pretty(indent + 1)
        return s

@dataclass
class FnDefinitionStatementNode(StatementNode):
    Symbol : ExpressionNode
    Params : List[SymbolTrait]
    Block : StatementNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += 'DEF: ' + self.Symbol.Pretty(indent + 1)
        for i, param in enumerate(self.Params):
            s += '{i}: ' + param.Pretty(indent + 1) # type: ignore
        s += 'BLOCK: ' + self.Block.Pretty(indent + 1)
        return s

# -- Program/Start Node

@dataclass
class ProgramNode(Node):
    FnDefinitions : List[FnDefinitionStatementNode]
    Statements : List[StatementNode]
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        for defn in self.FnDefinitions:
            s += defn.Pretty(indent + 1)
        for stmt in self.Statements:
            s += stmt.Pretty(indent + 1)
        return s