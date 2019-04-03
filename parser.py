# Add multi word unnamed attribute
# alias
# node contents as a replacement for name
# yellow!80


try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


from class_objects import *

from lark import Lark

calc_grammar = """
    start: LBRACE (instruction SEMICOLON)+ RBRACE

    instruction: NODE for_each* node_prop             -> node_ins

    for_each: FOREACH variable IN LRACE range RBRACE

    variable: letter (alphanum)*

    letter: [A-Za-z]

    aplhanum: [A-Za-z0-9]


    node_prop: pos? attrs? name?

    pos: AT LPARAN expr COMMA expr RPARAN

    attrs: LBOX attr (COMMA attr)* RBOX
    
    attr: STR_CONST                         -> unnamed_attr
        | STR_CONST EQUALS STR_CONST        -> str_attr
        | STR_CONST EQUALS expr             -> num_attr
    
    name: LBRACE STR_CONST RBRACE

    expr:   expr PLUS expr                  -> add
            | expr SUB expr                 -> sub
            | mul_expr                      -> expr2

    mul_expr: mul_expr STAR mul_expr        -> mul
            | mul_expr DIVIDE mul_expr      -> div
            | INT_CONST                     -> num


    INT_CONST: NUMBER
    STR_CONST: NAME


    PLUS: "+"
    STAR: "*"
    DIVIDE: "/"
    SUB: "-"
    LBRACE: "{"
    RBRACE: "}"
    LPARAN: "("
    RPARAN: ")"
    LBOX: "["
    RBOX: "]"
    EQUALS: "="
    COMMA: ","
    SEMICOLON: ";"
    
    NODE: "node"
    AT: "at"
    IN: 'in'
    FOREACH: 'foreach'

    %import common.CNAME -> NAME
    %import common.INT -> NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

parser = Lark(calc_grammar)

def run_mult_expr(t):
    if t.data == 'mul':
        return run_mult_expr(t.children[0])*run_mult_expr(t.children[2])
    if t.data == 'div':
        numerator = run_mult_expr(t.children[0])
        denominator = run_mult_expr(t.children[2])
        if denominator == 0:
            raise SyntaxError('Divison by Zero: %s' % t.data)
        return numerator/denominator
    elif t.data == 'num':
        return (float)(t.children[0])
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)

def run_add_expr(t):
    if t.data == 'add':
        return run_add_expr(t.children[0])+run_add_expr(t.children[2])
    elif t.data == 'sub':
        return run_add_expr(t.children[0])-run_add_expr(t.children[2])
    elif t.data == 'expr2':
        return run_mult_expr(t.children[0])
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def run_node(t):
    pos = (0,0)
    attrs = Attributes()
    name = ""
    for child in t.children:
        if child.data == 'pos':
            pos = (run_add_expr(child.children[2]), run_add_expr(child.children[4]))
        elif child.data == 'name':
            name = str(child.children[1])
        elif child.data == 'attrs':
            for i in range(1, len(child.children)-1,2):
                token = child.children[i]
                if token.data == "unnamed_attr":
                    val = str(token.children[0])
                    attrs.addUnnamedAttribute(val)
                else:
                    key = str(token.children[0])
                    val = token.children[2]
                    if token.data == 'num_attr':
                        val = run_add_expr(val)
                    elif token.data == 'str_attr':
                        val = str(val)
                    attrs.addNamedAttribute(key, val)
    return Node(pos, attrs, name)


def run_instruction(t):
    if t.data == "node_ins":
        return run_node(t.children[-1])
    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


def run_parser(program):
    instructions = []
    parse_tree = parser.parse(program)
    # print (parse_tree.pretty(indent_str='  '))
    for i in range(1,len(parse_tree.children)-1,2):
        instruction = parse_tree.children[i]
        instructions.append( run_instruction(instruction) )
    return instructions

def main():
    instructions = []
    code = input('> ')
    try:
        instructions = run_parser(code)
    except Exception as e:
        print(e)
    return instructions

instructions = main()
for instruction in instructions:
    # instruction.show()
    instruction.show()