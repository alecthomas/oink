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

from oink import Compiler
from nose.tools import assert_equal


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
