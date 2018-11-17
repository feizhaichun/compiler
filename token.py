# -*- coding:utf-8 -*-


# 得到token在env中对应的值
def get_true_value(token, env):
	if isinstance(token, IdToken):
		return env.get_val(token.val)
	elif isinstance(token, StrToken) or isinstance(token, NumToken):
		return token.val
	elif isinstance(token, int) or isinstance(token, basestring):
		return token
	else:
		raise Exception('cannot get true value : %s, env : %s' % (token, str(env)))


class Token(object):
	def __init__(self, val):
		super(Token, self).__init__()
		self.val = val

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
		return 'IdToken val : ' + str(self.val)


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
