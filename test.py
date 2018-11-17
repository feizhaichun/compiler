# -*- coding:utf-8 -*-
from lexer import Lexer
from token import NumToken, IdToken, StrToken, EOFToken, EOLToken
from exp_parser import Parser
import time


class TestReader(object):
	def __init__(self, lines):
		self.lino = 0
		self.lines = []

		for line in lines:
			for l in line.split('\n'):
				if len(l) > 0:
					self.lines.append(l)

	def readline(self):
		if self.lino >= len(self.lines):
			return ""

		ret = self.lines[self.lino]
		self.lino += 1
		return ret


def test_case_result(kind, success, failed):
	print time.asctime(time.localtime(time.time()))
	print "test case : %s finish" % kind
	print "success : %d" % success
	print "failed : %d" % failed
	print


if __name__ == "__main__":
	# lexer
	success, failed = 0, 0

	test_cases = [
		[
			["123 234"],
			[
				["peek", 0, NumToken(123)],
				["read", 0, NumToken(123)],
				["read", 0, NumToken(234)],
				["read", 0, EOLToken()],
				["read", 0, EOFToken()],
			]
		],
		[
			["abc cde 123"],
			[
				["peek", 0, IdToken("abc")],
				["peek", 1, IdToken("cde")],
				["peek", 2, NumToken(123)],
				["read", 0, IdToken("abc")],
				["read", 0, IdToken("cde")],
			]
		],
		[
			["&&!<=dasda>=<>"],
			[
				["read", 0, IdToken("&&")],
				["read", 0, IdToken("!")],
				["read", 0, IdToken("<=")],
				["read", 0, IdToken("dasda")],
				["read", 0, IdToken(">=")],
				["read", 0, IdToken("<")],
				["read", 0, IdToken(">")],
			]
		],
		[
			[r'"\"Hello" "World"'],
			[
				["read", 0, StrToken(r"\"Hello")],
				["read", 0, StrToken(r"World")],
			],
		],
	]

	for content, cases in test_cases:
		lexer = Lexer(TestReader(content))
		for op, oprand, expect in cases:
			if op == "peek":
				ret = lexer.peek(oprand)
			elif op == 'read':
				ret = lexer.read()
			else:
				raise Exception("unexpected op" + op)

			if ret != expect:
				print "unexpected val, should be [%s], ouput [%s]" % (str(expect), str(ret))
				failed += 1
			else:
				success += 1

	test_case_result("lexer", success, failed)

	# Parser
	success, failed = 0, 0
	test_cases = [
		[
			["1 + 2 * 3;", ],
			"( ( 1 + 2 ) * 3 )",
		],
		[
			["(1 + 2) / 3", ],
			"( ( 1 + 2 ) / 3 )",
		],
		[
			[
			'''
			if x < 10 {
				y = 15; y = a + b
				z = a + b
			} else {
				t = a + b
				a = b = c = x + y
			}
			''',
			],
			"( ( x < 10 ) ( ( y = 15 ) ( y = ( a + b ) ) ( z = ( a + b ) ) ) ( ( t = ( a + b ) ) ( a = ( b = ( c = ( x + y ) ) ) ) ) )"
		],
		[
			[
			'''
			while i < 10 {
				if i == 2 {
					a = i + 2
				} else {
					if i % 2 == 0 {
						i += 3
					} else {
						i += 2
					}
				}
			}
			'''
			],
			"( ( i < 10 ) ( ( ( i == 2 ) ( ( a = ( i + 2 ) ) ) ( ( ( ( i % 2 ) == 0 ) ( ( i += 3 ) ) ( ( i += 2 ) ) ) ) ) ) )",
		],

	]

	for case, expect in test_cases:
		ret = str(Parser(Lexer(TestReader(case))).program())
		if ret != expect:
			print "input\t:\t%s\nret\t\t:\t%s\nexpect\t:\t%s\n\n" % (case, ret, expect)
			failed += 1
		else:
			success += 1

	test_case_result("parser", success, failed)
