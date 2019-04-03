

def processNumber(c, f):
	number = ''
	while True:
		number = number + c
		c = f.read(1)
		if not c or not c.isdigit():
			f.seek(-1,1)
			return (int)(number)

def processString(c, f):
	string = ''
	while True:
		string = string + c
		c = f.read(1)
		if not c or not c.isalpha():
			f.seek(-1,1)
			return string


def run(input_filename):
	tokens = []
	KEYWORDS = ['at','node']
	with open(input_filename) as f:
	  while True:
	    c = f.read(1)
	    if not c:
	      print "Tokenisation complete\n"
	      break
	    if c.isdigit():
	    	val = processNumber(c,f)
	    	tokens.append(('INT_CONST', val))
	    elif c.isalpha():
	    	val = processString(c, f)
	    	if val in KEYWORDS:
	    		tokens.append(('KEYWORD', val))
	    	else:
	    		tokens.append(('STR_CONST', val))
	    elif c == '(':
	    	tokens.append(('LPAREN', c))
	    elif c == ')':
	    	tokens.append(('RPAREN', c))
	    elif c == ':':
	    	tokens.append(('COLON', c))
	    elif c == ';':
	    	tokens.append(('SEMICOLON', c))
	    elif c == ',':
	    	tokens.append(('COMMA', c))
	    elif c == '+':
	    	tokens.append(('PLUS', c))
	    elif c == '-':
	    	tokens.append(('MINUS', c))
	    elif c == '*':
	    	tokens.append(('STAR', c))
	    elif c == '/':
	    	tokens.append(('SLASH', c))
	    elif c == '\\':
	    	tokens.append(('BACKSLASH', c))
	    elif c == '=':
	    	tokens.append(('EQUALS', c))
	    elif c == '{':
	    	tokens.append(('LBRACE', c))
	    elif c == '}':
	    	tokens.append(('RBRACE', c))
	    elif c == '[':
	    	tokens.append(('LBOX', c))
	    elif c == ']':
	    	tokens.append(('RBOX', c))
	    elif c == '.':
	    	tokens.append(('DOT', c))
	    elif c==' ' or c=='\n':
	    	continue
	    else:
	    	print "Unidentified Token", c
	return tokens


input_filename = "sample/sample_1.txt"
tokens = run(input_filename)
print tokens