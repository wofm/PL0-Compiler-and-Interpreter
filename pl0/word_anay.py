import lex

reserved = {
    'begin': 'BEGIN',
    'end': 'END',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'const': 'CONST',
    'procedure': 'PROCEDURE',
    'var': 'VAR',
    'do': 'DO',
    'while': 'WHILE',
    'call': 'CALL',
    'read': 'READ',
    'write': 'WRITE',
    'repeat': 'REPEAT',
    'until': 'UNTIL',
    'odd': 'ODD'
}  # TODO odd
sorted_reserve = list(reserved.values())
sorted_reserve.sort()
tokens = [
             'NUMBER',
             'ID',
             'PLUS',
             'MINUS',
             'TIMES',
             'DIVIDE',
             'LPAREN',
             'RPAREN',
             'UNEQUAL',
             'LESS',
             'LORE',
             'MORE',
             'MOE',
             'EQUAL',
             'GIVE',
             'DOU',
             'DOT',
             'PAR'
         ] + sorted_reserve

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_UNEQUAL = r'<>'
t_LESS = r'<'
t_LORE = r'<='
t_MORE = r'>'
t_MOE = r'>='
t_EQUAL = r'='
t_GIVE = r':='
t_DOU = r','
t_DOT = r'\.'
t_PAR = r';'


# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# process the reserves
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


# Error handling rule
def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# the class us use
class word_anay:
    def __init__(self, input):
        self.lexer = lex.lex()
        self.lexer.input(input)

    def getsym(self):
        tok = self.lexer.token()
        # print(tok)
        return tok
