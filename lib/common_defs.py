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
    
class AssignableTrait(ABC):
    def Identifier(self) -> str:
        raise NotImplementedError()

# -- Expression Nodes

class ExpressionNode(Node):
    pass

@dataclass
class AssignExpressionNode(ExpressionNode):
    left : AssignableTrait # Assignable node
    right : ExpressionNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent + 1, f'ASSIGN "{self.left}"')
        s += self.right.Pretty(indent + 1)
        return s

@dataclass
class UnaryExpressionNode(ExpressionNode):
    child : ExpressionNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += self.child.Pretty(indent + 1)
        return s

@dataclass 
class BinaryExpressionNode(ExpressionNode):
    left : ExpressionNode
    op : TokenType #TODO: Change to custom operator type ?
    right : ExpressionNode
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += self.left.Pretty(indent + 1)
        s += _FormatIndented(indent + 1, self.op.name)
        s += self.right.Pretty(indent + 1)
        return s
    
@dataclass
class IdentifierExpressionNode(ExpressionNode, AssignableTrait):
    Value : str
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        s += _FormatIndented(indent, f'# {self.Value}')
        return s
    def Identifier(self) -> str:
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

# -- Program/Start Node

@dataclass
class ProgramNode(Node):
    Statements : List[StatementNode]
    def Pretty(self, indent=0) -> str:
        s = _FormatIndented(indent, self.__class__.__name__)
        for stmt in self.Statements:
            s += stmt.Pretty(indent + 1)
        return s