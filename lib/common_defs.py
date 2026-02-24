from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

class MiniC_Error(Exception):
    pass

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
