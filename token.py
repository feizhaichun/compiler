# -*- coding:utf-8 -*-


class Token(object):
	def __init__(self):
		super(Token, self).__init__()


class NumToken(Token):
	def __init__(self, val):
		super(NumToken, self).__init__()
		self.val = val

	def __str__(self):
		return 'NumToken val : ' + str(self.val)
