# encoding: utf-8
#
# Copyright (C) 2010 Alec Thomas <alec@swapoff.org>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Alec Thomas <alec@swapoff.org>

import re

from oink import Compiler, NotImplemented
from nose.tools import assert_equal, assert_raises


def assert_compile(py, js):
    output = Compiler().compile(py)
    output = re.sub(r'[ \t]+', ' ', output, re.M | re.S)
    assert_equal(output, js)


def test_list_construction():
    assert_compile('[1, 2, 3]', '[1, 2, 3];')


def test_list_iteration():
    assert_compile('for i in [1, 2, 3]: pass',
                    'Oink.each([1, 2, 3], function (i) {\n\n});;')


def test_lambda():
    assert_compile('lambda: 1',
                    'function () { return 1; };')


def test_list_comprehension():
    assert_compile('[i for i in [1, 2]]',
                   'Oink.listComprehension('
                   '[1, 2], '
                   'function (i) {\n return i;\n});')


def test_list_comprehension_if_condition():
    assert_compile('[i for i in [1, 2] if i > 1]',
                   'Oink.listComprehension('
                   '[1, 2], '
                   'function (i) {\n return i;\n}, '
                   'function (i) {\n return i > 1;\n});')


def test_print():
    assert_compile('print "hello"', 'console.log(\'hello\');')


def test_while():
    assert_compile('while 1: pass', 'while (1) {\n\n};')


def test_old_style_class():
    assert_compile('class A: pass', 'var A = Oink.Class.extend({\n\n});')


def test_new_style_class():
    assert_compile('class A(object): pass',
                   'var A = Oink.Class.extend({\n\n});')


def test_method():
    assert_compile('class A(object):\n'
                   '  def method(self):\n'
                   '    pass',
                   'var A = Oink.Class.extend({\n'
                   ' method: function () {\n'
                   ' var self = this;\n'
                   ' }\n'
                   '});')


def test_access_instance_attribute():
    assert_compile('class A(object):\n'
                   '  def method(self):\n'
                   '    self.a = 10',
                   'var A = Oink.Class.extend({\n'
                   ' method: function () {\n'
                   ' var self = this;\n'
                   ' self.a = 10;\n'
                   ' }\n'
                   '});')


def test_method_arguments():
    assert_compile('class A(object):\n'
                   '  def method(self, a):\n'
                   '    self.a = a',
                   'var A = Oink.Class.extend({\n'
                   ' method: function (a) {\n'
                   ' var self = this;\n'
                   ' self.a = a;\n'
                   ' }\n'
                   '});')


def test_positional_args_declaration():
    assert_compile('def a(*args): pass',
                   'function a() {\n ;\n var args = arguments;\n};')


def test_positional_args_call():
    assert_compile('a(*args)', 'a.apply(self, args);')


def test_keyword_args_declaration_not_supported():
    assert_raises(NotImplemented, Compiler().compile, 'def a(**args): pass')


def test_keyword_args_call_not_supported():
    assert_raises(NotImplemented, Compiler().compile, 'a(**args)')


def test_str():
    assert_compile('str(1)', 'Oink.str(1);')


def test_repr():
    assert_compile('repr(1)', 'Oink.repr(1);')
