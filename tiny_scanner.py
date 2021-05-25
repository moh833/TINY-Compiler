import re
import collections
import os

class Scanner():

    WHITESPACE = r'(?P<WHITESPACE>\s+)'
    COMMENT = r'(?P<COMMENT>{[^}]*})'
    SEMICOLON = r'(?P<SEMICOLON>;)'
    IF = r'(?P<IF>\bif\b)'
    THEN = r'(?P<THEN>\bthen\b)'
    ELSE = r'(?P<ELSE>\belse\b)'
    END = r'(?P<END>\bend\b)'
    REPEAT = r'(?P<REPEAT>\brepeat\b)'
    UNTIL = r'(?P<UNTIL>\buntil\b)'
    IDENTIFIER = r'(?P<IDENTIFIER>[a-zA-Z]+[a-zA-Z0-9_]*)'
    ASSIGN = r'(?P<ASSIGN>:=)'
    READ = r'(?P<READ>\bread\b)'
    WRITE = r'(?P<WRITE>\bwrite\b)'
    LESSTHAN = r'(?P<LESSTHAN><)'
    GREATERTHAN = r'(?P<GREATERTHAN>>)'
    EQUAL = r'(?P<EQUAL>=)'
    PLUS = r'(?P<PLUS>\+)'
    MINUS = r'(?P<MINUS>-)'
    MULT = r'(?P<MULT>\*)'
    DIV = r'(?P<DIV>/)'
    OPENBRACKET = r'(?P<OPENBRACKET>\()'
    CLOSEDBRACKET = r'(?P<CLOSEDBRACKET>\))'
    NUMBER = r'(?P<NUMBER>\d+(\.\d+)?)'

    ALL_TOKENS = [WHITESPACE, COMMENT, SEMICOLON, IF, THEN, END, REPEAT, UNTIL, 
                READ, WRITE, ASSIGN, LESSTHAN, GREATERTHAN, EQUAL, PLUS, MINUS, MULT, DIV, OPENBRACKET, CLOSEDBRACKET, NUMBER, IDENTIFIER]

    pattern = re.compile( '|'.join(ALL_TOKENS) )

    def __init__(self, text):
        self.text = text
        self.tokens, self.errors = self.get_tokens()
        self.num_tokens = len(self.tokens)
        if self.num_tokens > 0:
            self.current_i = 0
            self.finished = False
        else:
            self.finished = True
    
    def get_tokens(self):
        tokens = []
        errors = []
        matches = Scanner.pattern.finditer(self.text)
        last_end = 0
        for match in matches:
            start, end = match.span()
            if start != last_end:
                # error_text = self.text[last_end:start]
                # tokens.append(('ERROR', error_text))
                errors.append((last_end, start))
            if match.lastgroup not in ['WHITESPACE', 'COMMENT']:
                tokens.append((match.lastgroup, match.group()))
            last_end = end
        return tokens, errors
    
    def advance_token(self):
        if self.current_i < (self.num_tokens - 1):
            self.current_i += 1
        else:
            self.finished = True

    def current_token(self):
        if self.finished:
            return ('FINISHED', '')
        else:
            return self.tokens[self.current_i]



if __name__ == '__main__':
    full_path = os.path.realpath(__file__)
    path = os.path.dirname(full_path)

    file = path + '/test.txt'
    with open(file, 'r') as f:
        text = f.read()
    scanner = Scanner(text)
    tokens, errors = scanner.get_tokens()

    # with open('output.txt', 'w') as f:
    #     for t in tokens:
    #         f.write(f'{t[0]} - {t[1]}\n')
    for i in range(scanner.num_tokens):
        print(scanner.current_token())
        scanner.advance_token()


