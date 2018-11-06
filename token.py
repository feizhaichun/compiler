# -*- coding:utf-8 -*-


class Token(object):
	def __init__(self):
		super(Token, self).__init__()

	def __eq__(self, other):
		if type(other) != self.__class__:
			return False
		return self.val == other.val

	def __ne__(self, other):
		return not self.__eq__(other)


class NumToken(Token):
	def __init__(self, val):
		super(NumToken, self).__init__()
		self.val = val

	def __str__(self):
		return 'NumToken val : ' + str(self.val)


class IdToken(Token):
	def __init__(self, val):
		super(IdToken, self).__init__()
		self.val = val

	def __str__(self):
		return 'IdToken val : ' + str(self.val)


class StrToken(Token):
	def __init__(self, val):
		super(StrToken, self).__init__()
		self.val = val

	def __str__(self):
		return 'StrToken val : \'%s\'' % self.val
