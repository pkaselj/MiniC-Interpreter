from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Union

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
    OP      = auto()
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

class Operator(Enum):
    ADD = auto() # +
    SUB = auto() # -
    MUL = auto() # *
    DIV = auto() # /
    EQ  = auto() # ==
    NEQ = auto() # !=
    GT  = auto() # >
    LT  = auto() # <
    GTE = auto() # >=
    LTE = auto() # <=

@dataclass
class Token:
    token_type : TokenType
    value : Union[None, float, str, Operator]
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

# --- Base Class

class Node(ABC):
    def Pretty(self, indent=0) -> str:
        raise NotImplementedError()

# -- Expression Nodes

class ExpressionNode(Node):
    pass

@dataclass
class IdentifierExprNode(ExpressionNode):
    Value : str
    def Pretty(self, indent=0) -> str:
        pad = ' ' * indent
        s = f'{pad}{self.__class__.__name__}\n'
        s += f'{pad}# {self.Value}\n'
        return s

# -- Statement Nodes

class StatementNode(Node):
    pass

@dataclass
class ExprStmtNode(StatementNode):
    Expression : ExpressionNode
    def Pretty(self, indent=0) -> str:
        pad = ' ' * indent
        s = f'{pad}{self.__class__.__name__}\n'
        s += self.Expression.Pretty(indent + 1)
        return s

# -- Program/Start Node

@dataclass
class ProgramNode(Node):
    Statements : List[StatementNode]
    def Pretty(self, indent=0) -> str:
        pad = ' ' * indent
        s = f'{pad}{self.__class__.__name__}\n'
        for stmt in self.Statements:
            s += stmt.Pretty(indent + 1)
        return s