# -*- coding:utf-8 -*-
import collections
import re
from token import NumToken, IdToken, StrToken

# TODO:++，+的区分是否需要词法结合语法分析才可以做到？
NUMPAT = r'(\d+)'
IDPAT = r'([_\w][_\w\d]*|\|\||&&|!|==|<=|>=|<|>)'
STRPAT = r'("(\\\"|\\\\|\\n|[^"])*")'
PAT = '|'.join([NUMPAT, IDPAT, STRPAT])


class Lexer(object):
	def __init__(self, reader):
		super(Lexer, self).__init__()
		self.queue = collections.deque()
		self.has_more = True
		self.reader = reader

	def read(self):
		if self.fill_queue(1):
			return self.queue.popleft()
		return None

	def peek(self, pos):
		if self.fill_queue(pos + 1):
			return self.queue[pos]
		return None

	def fill_queue(self, lenth):
		while len(self.queue) < lenth and self.has_more:
			line = self.reader.readline()

			if not line:
				self.has_more = False
				return False

			line = line.strip()
			while line:
				matchobj = re.match(PAT, line)
				if not matchobj:
					raise Exception('invalid token %s' % line)

				if matchobj.group(1):
					word = matchobj.group(1)
					self.queue.append(NumToken(int(word)))
				elif matchobj.group(2):
					word = matchobj.group(2)
					self.queue.append(IdToken(word))
				elif matchobj.group(3):
					word = matchobj.group(3)
					self.queue.append(StrToken(word[1:-1]))

				line = line[len(word):]
				line = line.strip()

		return len(self.queue) >= lenth


if __name__ == "__main__":
	class TestReader(object):
		def __init__(self, lines):
			self.lines = lines
			self.lino = 0

		def readline(self):
			if self.lino >= len(self.lines):
				return ""

			ret = self.lines[self.lino]
			self.lino += 1
			return ret

	test_cases = [
		[
			["123 234"],
			[
				["peek", 0, NumToken(123)],
				["read", 0, NumToken(123)],
				["read", 0, NumToken(234)],
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
