# -*- coding:utf-8 -*-


class Environment(object):
	def __init__(self):
		super(Environment, self).__init__()


class NestedEnvironment(Environment):
	def __init__(self, outer=None):
		super(NestedEnvironment, self).__init__()
		self.names = {}
		self.outer = outer

	def get_val(self, name):
		if name in self.names:
			return self.names[name]
		if self.outer:
			return self.outer.get_val(name)
		return None

	def set_val(self, name, val):
		where = self.where(name)
		if where is None:
			where = self
		return where.set_new_val(name, val)

	def where(self, name):
		if name in self.names:
			return self
		if self.outer:
			return self.outer.where(name)
		return None

	def set_new_val(self, name, val):
		self.names[name] = val

		# assert val == self if name == 'this' else True, 'this must point to env self'
		return val

	def __str__(self):
		return ' '.join('%s : %s,' % (k, self.names[k]) if k != 'this' else 'this : this,' for k in sorted(self.names.keys()))


# 类/对象空间，必然有一个指向自身的this指针
class ClassEnvironment(NestedEnvironment):
	def __init__(self, outer=None):
		super(ClassEnvironment, self).__init__(outer)
		self.names['this'] = self

	def set_new_val(self, name, val):
		assert name != 'this', 'ClassEnvironment cannot assign this'
		return super(ClassEnvironment, self).set_new_val(name, val)
