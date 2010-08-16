#!/usr/bin/env python

"""Oink is a Python to Javascript compiler.

It differs from Pyjamas in that it tries to be as thin a layer as possible
between Python and Javascript.
"""

import ast
import optparse
import os
from textwrap import dedent
from contextlib import contextmanager


def strmap(show):
    """Hardcode a particular ast Node to string representation 'show'."""
    return lambda self, node=None: show


class Error(Exception):
    """Base Oink exception...boink!"""


class NotImplemented(Error):
    """A feature is not implemented."""


class Scope(object):
    def __init__(self, node, parent=None):
        self._node = node
        self._parent = parent
        self._symbols = set()

    def add_symbol(self, name):
        self._symbols.add(name)

    def __eq__(self, ast):
        return ast is type(self._node)

    def __contains__(self, name):
        return name in self._symbols


class Compiler(ast.NodeVisitor):
    SUPPORTED_META_FUNCTIONS = ('__init__', '__iter__')
    BUILTINS = {'None': 'null', 'True': 'true', 'False': 'false',
                'xrange': 'Oink.range', 'range': 'Oink.range',
                'sum': 'Oink.sum'}

    def __init__(self, *args, **kwargs):
        super(Compiler, self).__init__(*args, **kwargs)
        self.scopes = []
        self.classes = {}

    def compile(self, source, filename=None):
        tree = ast.parse(source, filename or '<undefined>')
        return self.visit(tree)

    def generic_visit(self, node):
        raise NotImplemented(ast.dump(node))

    def visit_Module(self, node):
        with self.scoped(node):
            return ';\n\n'.join(self.visit_list(node.body)) + ';'

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Pow):
            return 'Math.pow(%s, %s)' % (left, right)
        return '%s %s %s' % (left, self.visit(node.op), right)

    def visit_If(self, node):
        if not node.orelse:
            format = """
                if ({test}) {{
                {body}
                }}
            """
        else:
            format = """
                if ({test}) {{
                {body}
                }} else {{
                {orelse}
                }}
            """
        return self.format(format, test=self.visit(node.test),
                           body=self.body(node),
                           orelse=self.body(node, attr='orelse'))

    def visit_Compare(self, node):
        assert len(node.ops) == 1
        op_type = type(node.ops[0])
        lhs = self.visit(node.left)
        rhs = self.visit(node.comparators[0])
        if op_type is ast.In:
            return 'Oink.in_(%s, %s)' % (rhs, lhs)
        if op_type is ast.NotIn:
            return '!Oink.in_(%s, %s)' % (rhs, lhs)
        return '%s %s %s' % (lhs, self.visit(node.ops[0]), rhs)

    def visit_Yield(self, node):
        raise NotImplemented('yield is not supported')

    def visit_ImportFrom(self, node):
        assert node.module == 'oink', 'can only import oink runtime'
        return None

    def visit_FunctionDef(self, node):
        if node.name == 'new':
            return ''
        assert node.name in self.SUPPORTED_META_FUNCTIONS or \
                not node.name.startswith('__'), \
            'meta function %r is not supported' % node.name
        if self.scope == ast.ClassDef:
            prelude = 'var self = this'
            function_format = """
                {name}: function ({args}) {{
                {body}
                }}
            """
        else:
            prelude = ''
            function_format = """
                {comment}function {name}({args}) {{
                {body}
                }}
            """
        with self.scoped(node):
            name = node.name

            args = self.visit(node.args)
            if node.args.vararg:
                prelude += ';\nvar %s = arguments' % node.args.vararg

            comment = ''
            first = node.body[0]
            if isinstance(first, ast.Expr) and \
                    isinstance(first.value, ast.Str):
                comment = '/** %s */\n' % first.value.s.replace('*/', '*\/')
            body = self.body(node, prelude=prelude)

            return self.format(function_format, name=name, body=body,
                               args=args, comment=comment)

    def visit_arguments(self, node):
        assert not node.kwarg, 'keyword arguments not supported'
        assert not node.defaults
        args = self.visit_list(node.args)
        if args and args[0] == 'self' and self.parent_scope == ast.ClassDef:
            args.pop(0)
        return ', '.join(args)

    def visit_For(self, node):
        if isinstance(node.target, ast.Tuple):
            raise NotImplemented('loop iteration unpacking is not supported')
        iter = self.visit(node.iter)
        target = self.visit(node.target)
        body = self.body(node)
        return self.format("""
            Oink.each({iter}, function ({target}) {{
            {body}
            }});
            """, target=target, body=body, iter=iter)

    def visit_While(self, node):
        return self.format("""
            while ({test}) {{
            {body}
            }}
        """, test=self.visit(node.test), body=self.body(node))

    def visit_List(self, node):
        return '[%s]' % ', '.join(self.visit_list(node.elts))

    def visit_Assign(self, node):
        out = []
        assert len(node.targets) == 1, node.targets
        # Assume unpacking assignment. Is this a valid assumption?
        if isinstance(node.targets[0], ast.Tuple):
            for i, target in enumerate(node.targets[0].elts):
                out.append('%s = %s' % (self.visit(target),
                                        self.visit(node.value.elts[i])))
        else:
            lhs = self.visit(node.targets[0])
            # XXX This...is hackish.
            assert not lhs.startswith('Oink.'), \
                    'can not override builtin %r' % lhs
            if '.' not in lhs and lhs not in self.scope:
                prefix = 'var '
                self.scope.add_symbol(lhs)
            else:
                prefix = ''
            out.append('%s%s = %s' % (prefix, lhs, self.visit(node.value)))
        return ';\n'.join(out)

    def visit_AugAssign(self, node):
        lhs = self.visit(node.target)
        assert not lhs.startswith('Oink.'), \
                'can not override builtin %r' % lhs
        if '.' not in lhs and lhs not in self.scope:
            prefix = 'var '
            self.scope.add_symbol(lhs)
        else:
            prefix = ''
        return '%s%s %s= %s' % (prefix, lhs, self.visit(node.op),
                                self.visit(node.value))

    def visit_Tuple(self, node):
        values = ', '.join(self.visit_list(node.elts))
        return '[%s]' % values

    def visit_Dict(self, node):
        keys = self.visit_list(node.keys)
        values = self.visit_list(node.values)
        return '{%s}' % ', '.join('%s: %s' % i for i in zip(keys, values))

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        return '%s.%s' % (value, node.attr)

    def visit_Num(self, node):
        return str(node.n)

    def visit_Str(self, node):
        return '%r' % node.s

    def visit_Return(self, node):
        if node.value:
            return 'return %s' % self.visit(node.value)
        return 'return'

    def visit_BoolOp(self, node):
        op = ' %s ' % self.visit(node.op)
        return op.join(self.visit_list(node.values))

    def visit_UnaryOp(self, node):
        return '%s(%s)' % (self.visit(node.op), self.visit(node.operand))

    def visit_Pass(self, node):
        return ''

    def visit_ClassDef(self, node):
        # FIXME(aat) This is not ideal
        if self.scope == ast.ClassDef:
            class_format = """
                {name}: {super}.extend({{
                {body}
                }})
            """
        else:
            class_format = """
                var {name} = {super}.extend({{
                {body}
                }})
            """

        with self.scoped(node):
            assert len(node.bases) <= 1

            name = node.name

            super = node.bases[0].id if node.bases else 'Oink.Class'
            if super == 'object':
                super = 'Oink.Class'

            body = self.indent(',\n\n'.join(self.visit_list(node.body)))

            return self.format(class_format, name=name, super=super, body=body)

    def visit_Print(self, node):
        text = ' + " " + '.join(self.visit_list(node.values))
        return 'console.log(%s)' % (text or '""')

    def visit_ListComp(self, node):
        assert len(node.generators) == 1
        assert len(node.generators[0].ifs) <= 1
        target = self.visit(node.generators[0].target)
        iter = self.visit(node.generators[0].iter)
        expr = self.visit(node.elt)
        if node.generators[0].ifs:
            test = self.visit(node.generators[0].ifs[0])
            return self.format("""
            Oink.listComprehension({iter}, function ({target}) {{
              return {expr};
            }}, function ({target}) {{
              return {test};
            }})
            """, target=target, iter=iter, expr=expr, test=test)
        else:
            return self.format("""
            Oink.listComprehension({iter}, function ({target}) {{
                return {expr};
            }})
            """, target=target, iter=iter, expr=expr)

    visit_GeneratorExp = visit_ListComp

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str):
            return ''
        return self.visit(node.value)

    def visit_Call(self, node):
        if node.args and node.starargs:
            raise NotImplemented('simultaneous use of *args and normal args '
                                 'not supported')
        name = self.visit(node.func)
        if name == 'super':
            return 'self._super'
        if node.starargs:
            starargs = self.visit(node.starargs)
            # FIXME(aat) "self" is being hardcoded here...this is not good, but
            # the parent name is only available from the caller of visit_Call()
            return '%s.apply(self, %s)' % (name, starargs)
        args = ', '.join(self.visit_list(node.args))
        # XXX Hack to explicitly call constructor if type inference fails
        if name == 'new':
            return '%s %s' % (name, args)
        return '%s(%s)' % (name, args)

    def visit_Subscript(self, node):
        return '%s[%s]' % (self.visit(node.value), self.visit(node.slice))

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Slice(self, node):
        raise NotImplemented('Slicing is not implemented')

    def visit_Name(self, node):
        return self.BUILTINS.get(node.id, node.id)

    def visit_Lambda(self, node):
        args = self.visit(node.args)
        body = self.visit(node.body)
        return self.format("""
            function ({args}) {{ return {body}; }}
            """, args=args, body=body)

    # Internal methods
    def format(self, text, **args):
        return dedent(text).format(**args).strip()

    def visit_list(self, l):
        return filter(None, map(self.visit, l))

    def indent(self, text):
        return '\n'.join('  ' + line for line in text.splitlines())

    def body(self, node, newline='\n', prelude=None, attr='body'):
        body = self.visit_list(getattr(node, attr))
        body = [line if line.endswith('*/') else line + ';'
                for line in body]
        body = newline.join(body)
        text = self.indent((prelude + ';' + newline if prelude else '')
                           + body)
        return text

    @contextmanager
    def scoped(self, scope):
        if self.scopes:
            parent = self.scopes[-1]
        else:
            parent = None
        self.scopes.append(Scope(scope, parent=parent))
        yield
        self.scopes.pop()

    @property
    def scope(self):
        return self.scopes[-1] if self.scopes else None

    @property
    def parent_scope(self):
        return self.scopes[-2] if len(self.scopes) > 1 else None

    # hardcoded these Nodes to return string argument when visited.
    visit_Add = strmap('+')
    visit_Break = strmap('break')
    visit_Continue = strmap('continue')
    visit_Sub = strmap('-')
    visit_Mult = strmap('*')
    visit_Div = strmap('/')
    visit_Mod = strmap('%')
    visit_LShift = strmap('<<')
    visit_RShift = strmap('>>')
    visit_FloorDiv = strmap('//')
    visit_Not = strmap('!')
    visit_And = strmap('&&')
    visit_Or = strmap('||')
    visit_Eq = strmap('==')
    visit_NotEq = strmap('!=')
    visit_Lt = strmap('<')
    visit_LtE = strmap('<=')
    visit_Gt = strmap('>')
    visit_GtE = strmap('>=')
    visit_Is = strmap('===')
    visit_IsNot = strmap('!==')


def run_script(js):
    import PyV8

    class Console(PyV8.JSClass):
        def log(self, text):
            print text

    class Global(PyV8.JSClass):
        console = Console()

    context = PyV8.JSContext(Global())
    context.enter()
    context.eval(js)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='%prog [<flags>] <file>')
    parser.add_option('-I', '--include', default='.',
                      help='path to runtime [%default]')
    parser.add_option('--runtime', default='oink.js',
                      help='files to include in runtime [%default]')

    options, args = parser.parse_args()

    runtime = [os.path.join(options.include, p)
               for p in options.runtime.split(',')]

    if not args:
        parser.error('python source file required')
    filename = args[0]
    source = open(filename).read()

    # Import runtime
    js = ''
    for filename in runtime:
        js += open(filename).read() + '\n\n'
    compiler = Compiler()
    script = compiler.compile(source, filename)
    print script
    js += script
