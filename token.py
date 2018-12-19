# -*- coding:utf-8 -*-


class Token(object):
	def __init__(self, val):
		super(Token, self).__init__()
		self.val = val

		assert isinstance(self.val, (int, basestring)), 'wrong type : %s' % (type(self.val), )

	def __eq__(self, other):
		if type(other) != self.__class__:
			return False
		return self.val == other.val

	def __ne__(self, other):
		return not self.__eq__(other)


class NumToken(Token):
	def __init__(self, val):
		super(NumToken, self).__init__(val)

	def __str__(self):
		return 'NumToken val : ' + str(self.val)


class IdToken(Token):
	def __init__(self, val):
		super(IdToken, self).__init__(val)

	def __str__(self):
		return str(self.val)

	def __repr__(self):
		return self.__str__()


class StrToken(Token):
	def __init__(self, val):
		super(StrToken, self).__init__(val)

	def __str__(self):
		return 'StrToken val : \'%s\'' % self.val


class EOFToken(Token):
	def __init__(self):
		super(EOFToken, self).__init__(-1)

	def __str__(self):
		return 'EOFToken'


class EOLToken(Token):
	def __init__(self):
		super(EOLToken, self).__init__(-1)

	def __str__(self):
		return 'EOLToken'
