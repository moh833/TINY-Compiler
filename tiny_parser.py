import os
from tiny_scanner import Scanner
from anytree import Node, RenderTree
import copy
import re

class ParsingError(Exception):
    pass

class Parser:

    def __init__(self, scanner):
        self.scanner = scanner
        self.node_names = {}


    def create_node(self, name):
        for node, count in self.node_names.items():
            if node == name:
                new_name = f'{count+1}_{name}'
                created_node = Node(new_name)
                self.node_names[name] += 1
                return created_node
                
        created_node = Node(name)
        self.node_names[name] = 1
        return created_node

    @staticmethod
    def nodeattrfunc(node):
        pattern = re.compile(r'(if\b)|(assign\b)|(read\b)|(write\b)|(repeat\b)')
        is_stmt = bool(re.search(pattern, node.name))
        if is_stmt:
            return "shape=polygon"
        else:
            return "shape=ellipse"

    def match(self, token):
        # print('matching - ', self.scanner.current_token()[0])
        if self.scanner.current_token()[0] == token:
            self.scanner.advance_token()
        else:
            raise ParsingError(f"Can't match ({token})")
 
    def get_syntax_tree(self):
        self.node_names = {}
        return self.stmt_seq()

    def stmt_seq(self):
        # temp = Node(f'{self.node_id()}', data='PROGRAM')
        temp = self.create_node('stmt_seq')
        self.statement().parent = temp
        while(self.scanner.current_token()[0] == 'SEMICOLON'):
            self.match('SEMICOLON')
            self.statement().parent = temp
        
        return temp

    def statement(self):
        if(self.scanner.current_token()[0] == 'IF'):
            return self.if_stmt()
        elif(self.scanner.current_token()[0] == 'REPEAT'):
            return self.repeat_stmt()
        elif(self.scanner.current_token()[0] == 'IDENTIFIER'):
            return self.assign_stmt()
        elif(self.scanner.current_token()[0] == 'READ'):
            return self.read_stmt()
        elif(self.scanner.current_token()[0] == 'WRITE'):
            return self.write_stmt()
        else:
            raise ParsingError(f"Can't assemble a statement")

    def if_stmt(self):
        self.match('IF')
        # temp = Node(f'{self.node_id()}', data='IF')
        temp = self.create_node('if')
        if (self.scanner.current_token()[0] == 'OPENBRACKET'):
            self.match('OPENBRACKET')
            self.exp().parent = temp
            self.match('CLOSEDBRACKET')
        else:
            self.exp().parent = temp
        self.match('THEN')
        self.stmt_seq().parent = temp
        if(self.scanner.current_token()[0] == 'ELSE'):
            self.match('ELSE')
            self.stmt_seq().parent = temp
        self.match('END')

        return temp


    def repeat_stmt(self):
        self.match('REPEAT')
        # temp = Node(f'{self.node_id()}', data='REPEAT')
        temp = self.create_node('repeat')
        self.stmt_seq().parent = temp
        self.match('UNTIL')
        self.exp().parent = temp

        return temp

    def assign_stmt(self):
        # temp = Node(f'{self.node_id()}', data=f'assign ({self.scanner.current_token()[1]})')
        temp = self.create_node(f'assign ({self.scanner.current_token()[1]})')
        self.match('IDENTIFIER')
        self.match('ASSIGN')
        self.exp().parent = temp

        return temp

    def read_stmt(self):
        self.match('READ')
        # temp = Node(f'{self.node_id()}', data=f'READ ({self.scanner.current_token()[1]})')
        temp = self.create_node(f'read ({self.scanner.current_token()[1]})')
        self.match('IDENTIFIER')

        return temp

    def write_stmt(self):
        self.match('WRITE')
        # temp = Node(f'{self.node_id()}', data='WRITE')
        temp = self.create_node('write')
        self.exp().parent = temp

        return temp


    def exp(self):
        temp = self.simple_exp()
        while(self.scanner.current_token()[0] in ['EQUAL', 'LESSTHAN', 'GREATERTHAN']):
            # new_temp = Node(f"{self.node_id()}", data=f'OP ({self.scanner.current_token()[1]})')
            new_temp = self.create_node(f'op ({self.scanner.current_token()[1]})')
            self.match(self.scanner.current_token()[0])

            temp.parent = new_temp
            self.simple_exp().parent = new_temp

            # temp = new_temp
            temp = copy.deepcopy(new_temp)  
        
        return temp

    def simple_exp(self):
        temp = self.term()
        while(self.scanner.current_token()[0] in ['PLUS', 'MINUS']):
            # new_temp = Node(f"{self.node_id()}", data=f'OP ({self.scanner.current_token()[1]})')
            new_temp = self.create_node(f'op ({self.scanner.current_token()[1]})')
            self.match(self.scanner.current_token()[0])

            temp.parent = new_temp
            self.term().parent = new_temp

            # temp = new_temp
            temp = copy.deepcopy(new_temp)  

        return temp

    def term(self):
        temp = self.factor()
        while(self.scanner.current_token()[0] == 'MULT' or self.scanner.current_token()[0] == 'DIV'):
            # new_temp = Node(f"{self.node_id()}", data=f'OP ({self.scanner.current_token()[1]})')
            new_temp = self.create_node(f'op ({self.scanner.current_token()[1]})')
            self.match(self.scanner.current_token()[0])

            temp.parent = new_temp
            self.factor().parent = new_temp

            # temp = new_temp
            temp = copy.deepcopy(new_temp)  

        return temp

    def factor(self):
        temp = None
        if(self.scanner.current_token()[0] == 'OPENBRACKET'):
            self.match('OPENBRACKET')
            temp = self.exp()
            self.match('CLOSEDBRACKET')
        elif(self.scanner.current_token()[0] == 'NUMBER'):
            # temp = Node(f"{self.node_id()}", data=f'const ({self.scanner.current_token()[1]})')
            temp = self.create_node(f'const ({self.scanner.current_token()[1]})')
            self.match('NUMBER')
        elif(self.scanner.current_token()[0] == 'IDENTIFIER'):
            # temp = Node(f"{self.node_id()}", data=f'id ({self.scanner.current_token()[1]})')
            temp = self.create_node(f'id ({self.scanner.current_token()[1]})')
            self.match('IDENTIFIER')
        else:
            raise ParsingError(f"Can't match (IDENTIFIER), (NUMBER) or (OPENBRACKET)")

        return temp


if __name__ == '__main__':
    full_path = os.path.realpath(__file__)
    path = os.path.dirname(full_path)

    file = path + '/test.txt'
    with open(file, 'r') as f:
        text = f.read()

    scanner = Scanner(text)


    from anytree.exporter import DotExporter


    parser = Parser(scanner)


    try:
        syntax_tree = parser.get_syntax_tree()
        DotExporter(syntax_tree, nodeattrfunc=parser.nodeattrfunc).to_picture("final.png")
    except ParsingError as e:
        print(e)
    except FileNotFoundError as e:
        print('Please install graphviz from the following link to visualize the syntax tree: \nhttps://graphviz.org/download/')
    

    # for pre, fill, node in RenderTree(syntax_tree):
    #     print("%s%s" % (pre, node.name))



    # def nodenamefunc(node):
    #     return '%s:%s' % (node.data, node.depth)

    # DotExporter(syntax_tree, nodeattrfunc=lambda node: "fixedsize=true, width=1, height=1, shape=diamond", nodenamefunc=nodenamefunc, edgeattrfunc=lambda parent, child: "style=bold" ).to_picture("dan.png")