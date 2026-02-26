# MiniC Interpreter
## General
This project implements an interpreter for a simple toy language inspired by C - without external libraries other than Python standard library. The language is dynamically typed LL(1)*-ish* grammar interpreted by a recursive descent parser written in Python (for now).

It is still WIP and it currently implements the following features:
- Arithmetic operations (`+ - * /`) (with proper operator precedence i.e. `2+3*4` parses as `2+(3*4)`)
- Parentheses `3*(2+3)`
- Variables (create on assign)
- Compound assignment (right-associative i.e. `x = y = 1` parses as `x = (y = 1)`)
- Assignment as top-level expression i.e. assignment produces its own value - `x + (y = 4)` parses as `x + 4; y = 4`.
- `;`-delimited statements
- Semantic analysis of left hand side assignability

## Grammar EBNF

Currently implemented grammar EBNF:

```bnf
<S> ::= <stmt>*

<stmt> ::= <assign> ";"
<assign> ::= <id> "=" <assign> | <expr> 
<expr> ::= <term> (("+" | "-") <term>)*
<term> ::= <factor> (("*" | "/") <factor>)*
<factor> ::= <number> | <id> | "(" <expr> ")"
```

## Examples

```
> x;
Error: Symbol [x] not defined!
> x = 3;
3.0
> 2 * x;
6.0
> x;
3.0
> x = 2*x;
6.0
> x;
6.0
> x = y = 5;
5.0
> x; y;
5.0
5.0
> x = 2 * y = 5;
Error: Could not assign to node of type: [<class 'lib.common_defs.BinaryExpressionNode'>]
> x; y = 3 * (2 + x);
5.0
21.0
```
## Extending the Language
Implement in future:
- `NULL` value - remove var from env?
- flow control and loops - `if else while`
- functions