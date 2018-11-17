# -*- coding:utf-8 -*-


class Environment(object):
	def __init__(self):
		super(Environment, self).__init__()


class BaseEnvironment(Environment):
	def __init__(self):
		super(BaseEnvironment, self).__init__()
		self.names = {}

	def get_val(self, name):
		return self.names[name]

	def set_val(self, name, val):
		self.names[name] = val

	def __str__(self):
		return ' '.join('%s : %s,' % (k, self.names[k]) for k in sorted(self.names.keys()))
