# -*- coding:utf-8 -*-
from util import type_check


# 数组
class ArrayInfo(object):
	def __init__(self, array):
		super(ArrayInfo, self).__init__()
		self.array = array

	def get_item(self, index):
		type_check(index, (int))

		return self.array[index]

	def set_val(self, index, val):
		type_check(index, (int))

		self.array[index] = val
		return self.array[index]

	def __str__(self):
		return str(self.array)


class Func(object):
	def __init__(self, name, arglist, block, env, local_size):
		super(Func, self).__init__()
		self.name = name
		self.arglist = arglist
		self.block = block
		self.env = env
		self.local_size = local_size

	def __str__(self):
		return "(Func : %s)" % self.name

	def __repr__(self):
		return self.__str__()


# 方法
class Method(object):
	def __init__(self, func, this):
		super(Method, self).__init__()
		self.this = this
		self.func = func

	def __str__(self):
		return "(Method : %s)" % self.name

	def __repr__(self):
		return self.__str__()


# 类型
class ClassInfo(object):
	def __init__(self, name, local_env):
		super(ClassInfo, self).__init__()
		self.local_env = local_env
		self.name = name

	def __str__(self):
		return "(class : %s, local_env : %s)" % (self.name, self.local_env)

	def set_val(self, name, val):
		self.local_env.set_val(name, val)

	def get_val(self, name):
		return self.local_env.get_val(name)


# 对象
class InstanceInfo(object):
	def __init__(self, name, env):
		super(InstanceInfo, self).__init__()
		self.name = name
		self.local_env = env

	def __str__(self):
		return '(%s [class_name : %s, local_env : %s, ])' % ('InstanceInfo', self.name, self.local_env)

	def __repr__(self):
		return self.__str__()

	def set_val(self, name, val):
		self.local_env.set_val(name, val)

	def get_val(self, name):
		ret = self.local_env.get_val(name)

		# 在对象中找到的方法需要与对象绑定
		if isinstance(ret, Func):
			return Method(ret, self)

		return ret
