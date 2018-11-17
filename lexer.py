# -*- coding:utf-8 -*-
import collections
import re
from token import NumToken, IdToken, StrToken, EOFToken, EOLToken

# TODO:++，+的区分是否需要词法结合语法分析才可以做到？
NUMPAT = r'(\d+)'
IDPAT = r'([_\w][_\w\d]*|\|\||&&|!|==|<=|>=|<|>|\+=|\+|\*|\(|\)|/|;|if|{|}|==|=|%|while|%|else)'
STRPAT = r'("(\\\"|\\\\|\\n|[^"])*")'
PAT = '|'.join([NUMPAT, IDPAT, STRPAT])


class Lexer(object):
	def __init__(self, reader):
		super(Lexer, self).__init__()
		self.queue = collections.deque()
		self.has_more = True
		self.reader = reader
		self.line_no = 0

	def read(self):
		if self.fill_queue(1):
			return self.queue.popleft()
		return EOFToken()

	def peek(self, pos):
		if self.fill_queue(pos + 1):
			return self.queue[pos]
		return EOFToken()

	def fill_queue(self, lenth):
		while len(self.queue) < lenth and self.has_more:
			line = self.reader.readline()
			self.line_no += 1

			if not line:
				self.has_more = False
				return False

			line = line.strip()
			while line:
				matchobj = re.match(PAT, line)
				if matchobj is None:
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

				line = line[len(word):].lstrip()
			self.queue.append(EOLToken())

		return len(self.queue) >= lenth

	def get_line(self):
		return self.line_no
