# -*- coding:utf-8 -*-
import collections
import re
from token import NumToken


NUMPAT = '(\d+)'


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
				matchobj = re.match(NUMPAT, line)
				if not matchobj:
					raise Exception('invalid token')

				word = matchobj.group(1)
				self.queue.append(NumToken(int(word)))

				line = line[len(word):]
				line = line.strip()

		return True


if __name__ == "__main__":
	with open('test.txt') as f:
		lexer = Lexer(f)

		print lexer.peek(0)
		print lexer.read()

		print lexer.peek(0)
