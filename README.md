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
- Flow control with `if/else`. `else` is associated with the nearest `if`. Condition is `true` if not equal to `0`.
- `while` loop. Condition is `true` if not equal to `0`.
- `if/else` and `while` statements are expressions that return value of last interpreted expression i.e. `if(x) { y = 3; z = 4; }` would return `4` assuming `x` was not equal t o `0` 

## Grammar EBNF

Currently implemented grammar EBNF:

```bnf
<S> ::= <stmt>*

<stmt> ::= <assign> ";" | <if_stmt> | <while_stmt>
<if_stmt> ::= "if" "(" <expr> ")" <block> ( "else" "(" <block> ")" )?
<while_stmt> ::= "while (" <expr> ")" <block>
<block> ::= "{" <stmt>* "}"
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
> if(x) { y  = 4; } else { y = 5; }
4.0
> y;
4.0
> x = 0;
0.0
> if(x) { y  = 4; } else { y = 5; }
5.0
> y;
5.0
> x = 3; y = 20;
3.0
20.0
> while(x) { x = x - 1; y = y + 1; }
23.0
> y;
23.0
> x;
0.0
```
## Extending the Language
Implement in future:
- [ ] `NULL` value - remove var from env?
- [x] Flow control and loops - `if else while`
- [ ] Implement `elseif` keyword
- [ ] Implement comparison operators (`== > < >= <= !=`)
- [ ] Implement booleans
- [ ] Unary `-`
- [ ] Functions

## Unit tests

### Lexer
```
test_empty (tests.test_lexer.TestMiniCLexer.test_empty) ... ok
test_expr_1 (tests.test_lexer.TestMiniCLexer.test_expr_1) ... ok
test_expr_2 (tests.test_lexer.TestMiniCLexer.test_expr_2) ... ok
test_expr_3 (tests.test_lexer.TestMiniCLexer.test_expr_3) ... ok
test_ident (tests.test_lexer.TestMiniCLexer.test_ident) ... ok
test_invalid_char (tests.test_lexer.TestMiniCLexer.test_invalid_char) ... ok
test_kwd (tests.test_lexer.TestMiniCLexer.test_kwd) ... ok
test_num_frac (tests.test_lexer.TestMiniCLexer.test_num_frac) ... ok
test_num_int (tests.test_lexer.TestMiniCLexer.test_num_int) ... ok
test_num_sci (tests.test_lexer.TestMiniCLexer.test_num_sci) ... ok
test_op_assign (tests.test_lexer.TestMiniCLexer.test_op_assign) ... ok
test_op_multichar (tests.test_lexer.TestMiniCLexer.test_op_multichar) ... ok
test_op_singlechar (tests.test_lexer.TestMiniCLexer.test_op_singlechar) ... ok
test_punctuation (tests.test_lexer.TestMiniCLexer.test_punctuation) ... ok
test_whitespace (tests.test_lexer.TestMiniCLexer.test_whitespace) ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.002s

OK
```