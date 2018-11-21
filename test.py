# -*- coding:utf-8 -*-
from lexer import Lexer
from token import NumToken, IdToken, StrToken, EOFToken, EOLToken
from exp_parser import Parser
from environment import NestedEnvironment
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


class TestEval(object):
	def __init__(self, lexer, env):
		self.lexer = lexer
		self.env = env

	def eval(self):
		ret = None

		while self.lexer.peek(0) != EOFToken():
			ret = Parser(self.lexer).program().eval(self.env)

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
			["i % 2 == 0"],
			"( ( i % 2 ) == 0 )",
		],
		[
			["0 == i % 2"],
			"( 0 == ( i % 2 ) )",
		],
		[
			["1 + 2 * 3;", ],
			"( 1 + ( 2 * 3 ) )",
		],
		[
			["1 * 2 + 3;", ],
			"( ( 1 * 2 ) + 3 )",
		],

		[
			["(1 + 2) / 3", ],
			"( ( 1 + 2 ) / 3 )",
		],

		[
			['''
			def test(i, j, k) {
				i = i + 1
				j = j + 1
				k += 2
			}
			''', ],
			"( test [i, j, k] ( ( i = ( i + 1 ) ) ( j = ( j + 1 ) ) ( k += 2 ) ) )"
		],

		[
			['''
			func(1, 2, 3)
			}
			''', ],
			"( func [1, 2, 3] )"
		],

		[
			['''
			def ttt(i) {
				if i == 0 {
					i
				}
				ttt(i - 1)
			}
			''', ],
			"( ttt [i] ( ( ( i == 0 ) ( i ) ) ( ttt [( i - 1 )] ) ) )"
		],

		[
			['''
			if x < 10 {
				y = 15; y = a + b
				z = a + b
			} else {
				t = a + b
				a = b = c = x + y
			}
			''', ],
			"( ( x < 10 ) ( ( y = 15 ) ( y = ( a + b ) ) ( z = ( a + b ) ) ) ( ( t = ( a + b ) ) ( a = ( b = ( c = ( x + y ) ) ) ) ) )"
		],
		[
			['''
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
			'''],
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

	test_cases = [
		[
			['''
				a = 2
				b = c = a
			''', ],
			[
				"None", "a : 2, b : 2, c : 2,"
			],
		],
		[
			['''
				a = 2
				if a < 3 {
					b = -4
				} else {
					b = 6
				}

				if a < 1 {
					c = 3
				} else {
					c = 8
				}
			''', ],
			[
				"None", 'a : 2, b : -4, c : 8,',
			],
		],
		[
			['''
				a = 3
				b = 1
				c = 2
				while a > 0 {
					b = b + 1
					c = c + 1
					a = a - 1
				}
			''', ],
			[
				"None", 'a : 0, b : 4, c : 5,',
			],
		],
		[
			['''
				a = 2 * (1 + 3)
				b = 2 - -3;;
			''', ],
			[
				"None", 'a : 8, b : 5,',
			],
		],

		[
			['''
			def ttt(i) {
				if i == 0 {
					i
				}
				ttt(i - 1)
			}
			''', ],
			[
				'None', "ttt : (Func : ttt),"
			]
		],
		[
			['''
			def ttt(i) {
				if i > 0 {
					ttt(i - 1)
				}
				i
			}
			j = ttt(10)
			''', ],
			[
				'None', 'j : 10, ttt : (Func : ttt),'
			]
		],
		[
			['''
			def fabi(i) {
				if i < 2 {
					i
				} else {
					fabi(i - 2) + fabi(i - 1)
				}
			}
			j = fabi(10)
			''', ],
			[
				'None', 'fabi : (Func : fabi), j : 55,'
			]
		],
		[
			['''
			j = "abc" + "def"
			''', ],
			[
				'None', 'j : abcdef,'
			]
		],

	]

	success, failed = 0, 0
	for case, expect in test_cases:
		env = NestedEnvironment(None)
		ret = TestEval(Lexer(TestReader(case)), env).eval()
		if str(ret) != expect[0] or str(env) != expect[1]:
			print "input\t:\t%s" % case
			print "ret\t\t:\t%s\nexpect\t:\t%s" % (ret, expect[0])
			print "env\t\t:\t%s\nexpect\t:\t%s\n" % (env, expect[1])
			failed += 1
		else:
			success += 1

	test_case_result("eval", success, failed)
