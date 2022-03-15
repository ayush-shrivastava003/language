# language
A simple interpreter built in Python. Just a fun little project to learn how to build interpreters, nothing super crazy. Once I've figured out the essentials, I'll remake it in a faster and stricter language (likely Rust or Java).

Inspired by:

https://craftinginterpreters.com/

https://github.com/tsj845/Custom-Language-Interpreter

https://ruslanspivak.com/lsbasi-part1/

# syntax

* supported operators: `+, -, *, /, ()`

* statement separation: `statement; statement_2;`

* variable declarations: `type name = value;`

* supported types:
    * `num`

* comments: `? content to be ignored ?`

* functions: 
```
fn fn_name(arg: type):

    statement_1;
    statement_2;

end;

```