# yellow!80
# variable get range 
# make changes here for which nodes the edge belongs to
# find a name for rangetype1

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


from class_objects import *

from lark import Lark


#how to write grammar for node_draw (conflict issues)

calc_grammar = """
    start: LBRACE (instruction SEMICOLON)+ RBRACE

    instruction: BACKSLASH NODE for_each* node_prop                     -> node_ins
                |BACKSLASH DRAW node_draw (edge_details? node_draw)*    -> draw_ins

    node_draw:    position? NODE node_prop              -> typenode
                | LPARAN STR_CONST RPARAN               -> lookup



    edge_details: EDGE edge_attrs?

    edge_attrs: LBOX shape RBOX

    shape: LARROW
            | RARROW
            | DASH

    for_each: FOREACH variable IN LBRACE range RBRACE

    variable: BACKSLASH STR_CONST


    range: numvar COMMA DOT DOT DOT COMMA numvar        -> rangetype1 
            | INT_CONST (COMMA INT_CONST)*              -> discrete

    numvar: expr                                        -> number
            | variable                                  -> var

    node_prop: id? pos? attrs? name?

    id: LPARAN STR_CONST RPARAN                        

    pos: AT LPARAN expr COMMA expr RPARAN

    position: LPARAN expr COMMA expr RPARAN

    attrs: LBOX attr (COMMA attr)* RBOX
    
    attr: STR_CONST+                         -> unnamed_attr
        | STR_CONST+ EQUALS STR_CONST+       -> str_attr
        | STR_CONST+ EQUALS expr             -> num_attr
        | STR_CONST+ EQUALS 
    
    name: LBRACE STR_CONST RBRACE

    expr:   expr PLUS expr                  -> add
            | expr SUB expr                 -> sub
            | mul_expr                      -> expr2


    mul_expr: mul_expr STAR mul_expr        -> mul
            | mul_expr DIVIDE mul_expr      -> div
            | INT_CONST                     -> num
            | variable                      -> lookup


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
    BACKSLASH: "$"
    LARROW: "<-"
    RARROW: "->"
    DASH: SUB
   
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

def process_mult_expr(t, dictionary = None):
    if t.data == 'mul':
        return process_mult_expr(t.children[0], dictionary)*process_mult_expr(t.children[2], dictionary)
    if t.data == 'div':
        numerator = process_mult_expr(t.children[0], dictionary)
        denominator = process_mult_expr(t.children[2], dictionary)
        if denominator == 0:
            raise SyntaxError('Divison by Zero: %s' % t.data)
        return numerator/denominator
    elif t.data == 'num':
        return (float)(t.children[0])
    elif t.data == 'lookup':
        var_name = str(t.children[0].children[1])
        if var_name in dictionary:
            return dictionary[var_name]
        else:
            raise SyntaxError('Variable not found: %s' % var_name)
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def process_add_expr(t, dictionary = None):
    if t.data == 'add':
        return process_add_expr(t.children[0], dictionary)+process_add_expr(t.children[2], dictionary)
    elif t.data == 'sub':
        return process_add_expr(t.children[0], dictionary)-process_add_expr(t.children[2], dictionary)
    elif t.data == 'expr2':
        return process_mult_expr(t.children[0], dictionary)
    else:
        raise SyntaxError('Unknown expression: %s' % t.data)


def process_loop(t, foreach_list, loopnumber, dictionary):
    if loopnumber == len(foreach_list):
        return [generate_node(t, dictionary)]
    else:
        print "loopnumber = ", loopnumber, "dictionary = ", dictionary
        nodes = []
        looprange = []

        start_range = foreach_list[loopnumber][1]
        end_range = foreach_list[loopnumber][-1]
        
        if type(start_range) == "str":
            start_range = dictionary[start_range]

        if type(end_range) == "str":
            end_range = dictionary[end_range]

        looprange = range(start, end + 1)

        # print start_range, end_range
        # print looprange

        for i in range(len(looprange)):
            dictionary[foreach_list[loopnumber][0]] = looprange[i]
            nodes.extend(process_loop(t, foreach_list, loopnumber + 1, dictionary))
        
        return nodes


def generate_node(t, dictionary = None, position = (0,0)):
    global node_dictionary

    pos = position
    attrs = Attributes()
    name = ""
    identity = ""
    for child in t.children:
        if child.data == "id":
            identity = str(child.children[1])

        elif child.data == 'pos':
            pos = (process_add_expr(child.children[2], dictionary), process_add_expr(child.children[4], dictionary))
        
        elif child.data == 'name':
            name = str(child.children[1])

        elif child.data == 'attrs':

            for i in range(1, len(child.children)-1,2):
                token = child.children[i]
                if token.data == "unnamed_attr":
                    val = str(' '.join(token.children))
                    attrs.addUnnamedAttribute(val)

                else:

                    key = str(' '.join(token.children[0:token.children.index('=')]))
                    
                    if token.data == 'num_attr':
                        val = token.children[token.children.index('=') + 1]
                        val = process_add_expr(val, dictionary)
                    
                    elif token.data == 'str_attr':
                        val = str(' '.join(token.children[token.children.index('=') + 1:]))
                    
                    if key == "node contents":
                        name = val
                    else:
                        attrs.addNamedAttribute(key, val)
    
    new_node = Node(pos, attrs, name, identity)
    if identity != "":
        node_dictionary[identity] = new_node

    return new_node


def process_foreach(t, foreach_list):
    nodes = []

    first_loop = foreach_list[0]
    loop_var = first_loop[0]

    for i in range(1, len(first_loop)):
        dictionary = {}
        dictionary[loop_var] =  first_loop[i]
        nodes.extend(process_loop(t, foreach_list, 1, dictionary))
    
    return nodes


def get_range(t):
    if t.data == "rangetype1":
        values = []
        # range: numvar COMMA DOT DOT DOT COMMA numvar
        start_range = t.children[0]

        if start_range.data == "var":

            # numvar = variable
            variable = start_range.children[0]

            # variable = BACKSLASH var_name
            values.append(str(variable.children[1]))

        elif start_range.data == "number":
            values.append(run_expr(start_range.children[0]))
        else:
            raise SyntaxError('Unknown rannge type: %s' % start_range.data) 

        end_range = t.children[-1]
        if end_range.data == "var":

            # numvar = variable
            variable = end_range.children[0]

            # variable = BACKSLASH var_name
            values.append(str(variable.children[1]))
        elif end_range.data == "number":
            values.append(run_expr(end_range.children[0]))
        else:
            raise SyntaxError('Unknown rannge type: %s' % end_range.data)

        return values

    elif t.data == "discrete":
        values = []

        # discrete_range = num (COMMA num)*
        for i in range(0, len(t.children), 2):
            values.append(process_add_expr(t.children[i]))

        return values
    else:
        raise SyntaxError('Unknown rannge type: %s' % t.data)    


def process_node_instruction(t):
    foreach_list = []

    # node_ins = NODE foreach* node_props
    for i in range(1, len(t.children) - 1):
        foreach_ins = t.children[i]

        # foreach_ins = FOREACH variable IN LBRACE range RBRACE
        variable = foreach_ins.children[1]
        
        # variable = BACKSLASH var_name
        var_name = str(variable.children[1])

        loop_range = get_range(foreach_ins.children[4])
        
        foreach_list.append([var_name] + loop_range)

    if foreach_list == []:
        return [generate_node(t)]
    else:
        return process_foreach(t.children[-1], foreach_list)


def process_node_draw(t):
    if t.data == "typenode":
        position = (0, 0)

        try:
            position = (process_add_expr(t.children[0].children[1]), process_add_expr(t.children[0].children[3]))
        except Exception as e:
            pass
        
        return process_node(t.children[-1], position = position)

    elif t.data == "lookup":
        return node_dictionary[str(t.children[1])]

    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)



"""
Input : The Subtree of one instruction
Output: -
Action:
    1) Parses which type of instruction it is. 
    2) Updates the list of nodes and edges.
"""
def process_instruction(t):
    global graph_nodes

    if t.data == "node_ins":
        graph_nodes.extend(process_node_instruction(t))

    elif t.data == "draw_ins":

        nodes = []
        edges = []

        for i in range(1, len(t.children)):
            print t.children[i].data
            if t.children[i].data != "edge_details":
                print "yes"
                nodes.append(generate_node_draw(t.children[i]))

        

        for i in range(1, len(t.children)):
            if t.children[i].data == "edge_details":
                edges.append(source_node = nodes[i-1], dest_node = nodes[i+1])

        return nodes, edges
        
    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)

"""
Input : The code that has been provided as input by the user
Output: -
Action:
    1) Generates a Parse tree for the input code. 
    2) Executes each instruction and updates the list of nodes and edges.
"""
def run_parser(program):
    parse_tree = parser.parse(program)
    # print (parse_tree.pretty(indent_str='  '))
    # exit()

    # code = LBRACE (instruction SEMICOLON)+ RBRACE
    for i in range(1, len(parse_tree.children)-1, 2):
        instruction = parse_tree.children[i]

        # Removing BackSlash
        instruction.children.pop(0)
        process_instruction(instruction)


"""
Input : -
Output: -
Action:
    1) Takes input from the user
    2) Replaces Backslash with Dollar (Temporary)
    3) Runs the parser
"""
def main():
    # Not able to parse '//' at the moment
    code = input('> ').replace('\\', '$')
    # print code
    try:
        run_parser(code)
    except Exception as e:
        print(e)


node_dictionary = {}
graph_edges = []
graph_nodes = []

if __name__ == '__main__':
    main()
