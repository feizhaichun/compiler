# -*- coding:utf-8 -*-


class Environment(object):
	def __init__(self):
		super(Environment, self).__init__()
		self.is_nested_instance = False


class NestedEnvironment(Environment):
	def __init__(self, outer=None):
		super(NestedEnvironment, self).__init__()
		self.names = {}
		self.outer = outer

		if self.outer is not None:
			self.is_nested_instance = self.outer.is_nested_instance

	def get_val(self, name):
		if name in self.names:
			return self.names[name]
		if self.outer:
			return self.outer.get_val(name)
		raise NameError('could not find %s in %s' % (name, self))

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

	# 找到name对应的index
	def lookup(self, name):
		return -1


# 类/对象空间，必然有一个指向自身的this指针
class ClassEnvironment(NestedEnvironment):
	def __init__(self, outer=None):
		super(ClassEnvironment, self).__init__(outer)
		self.names['this'] = self

		self.is_nested_instance = True

	def set_new_val(self, name, val):
		assert name != 'this', 'ClassEnvironment cannot assign this'
		return super(ClassEnvironment, self).set_new_val(name, val)


# 函数对象空间，所有的局部变量访问都通过index
class FunEnvironment(NestedEnvironment):
	def __init__(self, outer=None, size=0, instance_info=None):
		super(FunEnvironment, self).__init__(outer)
		self.name2index = {}
		self.names = [None] * size

		if instance_info is not None:
			self.name2index['this'] = 0
			self.names[0] = instance_info

	def lookup(self, name):
		if name in self.name2index:
			return self.name2index[name], 0
		elif isinstance(self.outer, FunEnvironment):
			pos, nested_level = self.outer.lookup(name)
			return pos, nested_level + 1
		return -1, 0

	def set_new_val(self, name, val=None):
		# assert name != 'this'
		if name not in self.name2index:
			self.name2index[name] = len(self.names)
			self.names.append(val)
		return self.name2index[name], 0

	def get_local_size(self):
		return len(self.names)

	def __str__(self):
		return str(self.name2index) + " " + str(self.names)

	# 如果调用通用的set/get_val方法，默认从嵌套空间获取
	def set_val(self, name, val):
		self.outer.set_val(name, val)

	def get_val(self, name):
		return self.outer.get_val(name)

	def set_local(self, index, nested_level, val):
		if nested_level == 0:
			self.names[index] = val
			return val
		return self.outer.set_local(index, nested_level - 1, val)

	def get_local(self, index, nested_level):
		if nested_level == 0:
			return self.names[index]
		return self.outer.get_local(index, nested_level - 1)
