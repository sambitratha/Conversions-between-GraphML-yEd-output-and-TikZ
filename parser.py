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


#how to write grammar for node_draw (conflict issues)

calc_grammar = """
    start: LBRACE (instruction SEMICOLON)+ RBRACE

    instruction: NODE for_each* node_prop             -> node_ins
                |DRAW node_draw (edge_details? node_draw)*    -> draw_ins

    node_draw:    position? NODE node_prop              -> typenode
                | LPARAN STR_CONST RPARAN                 -> lookup



    edge_details: EDGE attrs?

    for_each: FOREACH variable IN LBRACE range RBRACE

    variable: STR_CONST


    range: INT_CONST COMMA DOT DOT DOT COMMA INT_CONST  -> rangetype1 
            | INT_CONST (COMMA INT_CONST)*              -> rangetype2

    node_prop: pos? attrs? name?

    pos: AT LPARAN expr COMMA expr RPARAN

    position: LPARAN expr COMMA expr RPARAN

    attrs: LBOX attr (COMMA attr)* RBOX
    
    attr: STR_CONST                         -> unnamed_attr
        | STR_CONST EQUALS STR_CONST        -> str_attr
        | STR_CONST EQUALS expr             -> num_attr
    
    name: LBRACE STR_CONST RBRACE

    expr:   expr PLUS expr                  -> add
            | expr SUB expr                 -> sub
            | mul_expr                      -> expr2
            | STR_CONST                     -> lookup

    mul_expr: mul_expr STAR mul_expr        -> mul
            | mul_expr DIVIDE mul_expr      -> div
            | INT_CONST                     -> num
            | STR_CONST                     -> lookup


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
    DOT: "."
   
    NODE: "node"
    DRAW: "draw"
    EDGE: "edge"
    AT: "at"
    IN: "in"
    FOREACH: "foreach"
    %import common.CNAME -> NAME
    %import common.INT -> NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

parser = Lark(calc_grammar)

def run_mult_expr(t, dictionary = None):
    if t.data == 'mul':
        return run_mult_expr(t.children[0], dictionary)*run_mult_expr(t.children[2], dictionary)
    if t.data == 'div':
        numerator = run_mult_expr(t.children[0], dictionary)
        denominator = run_mult_expr(t.children[2], dictionary)
        if denominator == 0:
            raise SyntaxError('Divison by Zero: %s' % t.data)
        return numerator/denominator
    elif t.data == 'num':
        return (float)(t.children[0])
    elif t.data == 'lookup':
        key = str(t.children[0])
        if key not in dictionary:
            raise SyntaxError('key not found: %s' % key)
        else:
            return dictionary[key]
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)

def run_add_expr(t, dictionary = None):
    if t.data == 'add':
        return run_add_expr(t.children[0], dictionary)+run_add_expr(t.children[2], dictionary)
    elif t.data == 'sub':
        return run_add_expr(t.children[0], dictionary)-run_add_expr(t.children[2], dictionary)
    elif t.data == 'expr2':
        return run_mult_expr(t.children[0], dictionary)
    elif t.data == 'lookup':
        key = str(t.children[0])
        if key not in dictionary:
            raise SyntaxError('key not found: %s' % key)
        else:
            return dictionary[key]
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def run_node_loop(t, foreach_list):
    if foreach_list == []:
        return [run_node(t)]
    else:
        nodes = []
        for i in range(1, len(foreach_list[0])):
            variables = [(foreach_list[0][0], foreach_list[0][i])]
            nodes.extend(process_loop(t, foreach_list, 1, variables))
        return nodes

def process_loop(t, foreach_list, loopnumber, variables):
    if loopnumber == len(foreach_list):
        dictionary = {}
        for (x, y) in variables:
            dictionary[x] = y
        return [run_node(t, dictionary)]
    else:
        nodes = []
        for i in range(1, len(foreach_list[loopnumber])):
            variables.append((foreach_list[loopnumber][0], foreach_list[loopnumber][i]))
            nodes.extend(process_loop(t, foreach_list, loopnumber + 1, variables))
        return nodes

def run_node(t, dictionary = None, position = (0,0)):
    pos = position
    attrs = Attributes()
    name = ""
    for child in t.children:
        if child.data == 'pos':
            pos = (run_add_expr(child.children[2], dictionary), run_add_expr(child.children[4], dictionary))
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


def get_range(t):
    if t.data == "rangetype1":
        start = int(t.children[0])
        end   = int(t.children[-1])
        print start, end
        return range(start, end + 1)
    elif t.data == "rangetype2":
        li = []
        for i in range(0, len(t.children), 2):
            li.append(int(t.children[i]))
        return li
    else:
        raise SyntaxError('Unknown rannge type: %s' % t.data)

def run_forloop(t):
    #update this step 
    variable = str(t.children[1].children[0])       
    loop_range = get_range(t.children[4])
    return [variable] + loop_range


def process_node_draw(t):
    if t.data == "typenode":
        position = (0, 0)

        try:
            position = (run_add_expr(t.children[0].children[1]), run_add_expr(t.children[0].children[3]))
        except Exception as e:
            pass
        
        return run_node(t.children[-1], position = position)

    elif t.data == "lookup":
        return node_dictionary[str(t.children[1])]

    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


def run_instruction(t):
    if t.data == "node_ins":

        foreach_list = []

        for i in range(1, len(t.children) - 1):
            foreach_list.append(run_forloop(t.children[i]))
        
        return run_node_loop(t.children[-1], foreach_list)

    elif t.data == "draw_ins":

        nodes = []
        edges = []

        for i in range(1, len(t.children)):
            print t.children[i].data
            if t.children[i].data != "edge_details":
                print "yes"
                nodes.append(process_node_draw(t.children[i]))

        #make changes here for which nodes the edge belongs to

        for i in range(1, len(t.children)):
            if t.children[i].data == "edge_details":
                edges.append(source_node = nodes[i-1], dest_node = nodes[i+1])

        return nodes, edges
        
    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


def run_parser(program):
    instructions = []
    parse_tree = parser.parse(program)
    print (parse_tree.pretty(indent_str='  '))
    for i in range(1,len(parse_tree.children)-1,2):
        instruction = parse_tree.children[i]
        instructions.extend( run_instruction(instruction))
    return instructions

def main():
    instructions = []
    code = input('> ')
    try:
        instructions = run_parser(code)
    except Exception as e:
        print(e)
    return instructions


node_dictionary = {}
instructions = main()
for instruction in instructions:
    instruction.show()
