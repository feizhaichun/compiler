# -*- coding:utf-8 -*-
from token import Token, IdToken
from environment import NestedEnvironment, ClassEnvironment
from util import type_check


class ASTNode(object):
	def __init__(self):
		super(ASTNode, self).__init__()

	def eval(self, env):
		raise Exception('%s has not implement eval' % type(self))

	def __repr__(self):
		return self.__str__()


# 叶子节点，代表终结符
class ASTLeaf(ASTNode):
	def __init__(self, token):
		type_check(token, Token)

		super(ASTLeaf, self).__init__()
		self.token = token

	def __str__(self):
		return str(self.token.val)

	def eval(self, env):
		return self.token.val


# 非叶子节点，代表非终结符
class ASTList(ASTNode):
	def __init__(self, token_list):
		super(ASTList, self).__init__()
		self.token_list = token_list

	def __str__(self):
		ret = ['(']
		for element in self.token_list:
			if isinstance(element, Token):
				ret.append(str(element.val))
			else:
				ret.append(str(element))
		ret.append(')')
		return ' '.join(ret)

	def eval(self, env):
		ret = None
		for token in self.token_list:
			ret = token.eval(env)
		return ret


# 双目操作符
class BinaryExpr(ASTList):
	def __init__(self, token_list):
		super(BinaryExpr, self).__init__(token_list)

		if len(token_list) != 3:
			raise Exception("len(token_list) in BinaryExpr must be 3 : %s", token_list)

		self.left, self.op, self.right = self.token_list

		type_check(self.op, OpExpr)
		type_check(self.right, (ASTNode))

	def eval(self, env):
		op = self.op.eval(env)
		# if为赋值操作，需要单独处理
		if op == '=':
			type_check(self.left, (IdExpr, DotExpr))
			ret = self.left.set_val(self.right.eval(env), env)
			return ret

		left = self.left.eval(env)
		right = self.right.eval(env)
		if op == '<':
			return left < right
		elif op == '>':
			return left > right
		elif op == '==':
			return left == right
		elif op == '+':
			return left + right
		elif op == '-':
			return left - right
		elif op == '*':
			return left * right
		else:
			raise Exception('has not implement op : %s' % op)


# 空语句
class NullExpr(ASTLeaf):
	def __init__(self, token):
		super(NullExpr, self).__init__(token)

	def eval(self, env):
		return None


class Func(object):
	def __init__(self, name, arglist, block, env):
		super(Func, self).__init__()
		self.name = name
		self.arglist = arglist
		self.block = block
		self.env = env
		assert(all(isinstance(val, IdToken) for val in self.arglist))

	def __str__(self):
		return "(Func : %s)" % self.name

	def __repr__(self):
		return self.__str__()

	def eval(self, argvals, instance_info=None):
		assert(len(self.arglist) == len(argvals))
		local_env = NestedEnvironment(self.env)

		# 如果instance_info不为None，说明是方法，需要一个指向对象的this指针
		if instance_info is not None:
			local_env.set_new_val('this', instance_info)

		for name, val in zip(self.arglist, argvals):
			local_env.set_new_val(name.val, val)
		return self.block.eval(local_env)


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

	def eval(self, argvals):
		return self.func.eval(argvals, self.this)


# 函数定义
class DefExpr(ASTList):
	def __init__(self, token_list):
		super(DefExpr, self).__init__(token_list)
		assert(len(token_list) == 3)
		assert(all(isinstance(val, IdToken) for val in token_list[1]))

		self.fun_name = token_list[0]
		self.param_list = token_list[1]
		self.block = token_list[2]

		type_check(self.fun_name, IdExpr)

	def eval(self, env):
		return env.set_val(self.fun_name.get_name(), Func(self.fun_name, self.param_list, self.block, env))


# 函数调用
class FunCallExpr(ASTList):
	def __init__(self, token):
		super(FunCallExpr, self).__init__(token)

		self.args = token

	def eval(self, env, instance_info=None):
		raise NotImplementedError()

	def calc_params(self, env):
		return [val.eval(env) for val in self.args]


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
	def __init__(self, class_info, env):
		super(InstanceInfo, self).__init__()
		self.name = class_info.name
		self.local_env = ClassEnvironment(class_info.local_env)

		# 寻找初始化函数
		constructor = self.local_env.get_val(self.name)
		type_check(constructor, (Func, type(None)))
		if constructor is not None:
			constructor.eval([], self)		# 暂时不支持多参数构造函数

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


# 类的定义表达式
class ClassDefExpr(ASTList):
	def __init__(self, token_list):
		super(ClassDefExpr, self).__init__(token_list)
		assert len(token_list) == 3, token_list

		type_check(token_list[0], IdExpr)
		self.name = token_list[0].get_name()

		self.father_name = token_list[1]
		self.members = token_list[2]

	def eval(self, env):
		father_env = None
		if self.father_name is not None:
			father_class = env.get_val(self.father_name)
			assert father_class is not None, 'class : %s cannot find his father : %s' % (self.name, self.father_name)
			father_env = father_class.local_env

		local_env = ClassEnvironment(father_env)

		for member in self.members:
			if isinstance(member, DefExpr):
				member.eval(local_env)
			else:
				member.eval(local_env)

		env.set_new_val(self.name, ClassInfo(self.name, local_env))


# 方法访问
class DotExpr(ASTList):
	def __init__(self, token_list):
		super(DotExpr, self).__init__(token_list)

	def set_val(self, val, env):

		assert not isinstance(self.token_list[-1], FunCallExpr), 'cannot assign to a Function call'
		class_info = self._get_val(env, self.token_list[:-1])

		type_check(class_info, (ClassInfo, InstanceInfo, NestedEnvironment))
		class_info.set_val(self.token_list[-1].get_name(), val)
		return val

	def _get_val(self, env, exprs):
		cur_env = env

		for expr in exprs:

			# 如果是函数调用
			if isinstance(expr, FunCallExpr):
				args = expr.calc_params(env)
				fun_ob = cur_env

				if isinstance(fun_ob, (Func, Method)):
					cur_env = fun_ob.eval(args)
				else:
					cur_env = InstanceInfo(fun_ob, env)
			else:
				cur_env = expr.eval(cur_env)
		return cur_env

	def eval(self, env):
		return self._get_val(env, self.token_list)


# if
class IfExpr(ASTList):
	def __init__(self, token_list):
		if len(token_list) != 2 and len(token_list) != 3:
			raise Exception("len(token_list) in if should be 2 or 3 : %s", token_list)
		super(IfExpr, self).__init__(token_list)

		self.condition = token_list[0]
		self.block = token_list[1]
		self.elseblock = token_list[2] if len(token_list) == 3 else None

	def eval(self, env):
		if self.condition.eval(env):
			return self.block.eval(env)
		elif self.elseblock:
			return self.elseblock.eval(env)
		return None


# while
class WhileExpr(ASTList):
	def __init__(self, token_list):
		if len(token_list) != 2:
			raise Exception("len(token_list) in if should be 2 or 3 : %s", token_list)
		super(WhileExpr, self).__init__(token_list)

		self.condition = token_list[0]
		self.block = token_list[1]

	def eval(self, env):
		while self.condition.eval(env):
			ret = self.block.eval(env)
		return ret


# -
class NegExpr(ASTList):
	def __init__(self, exprs):
		super(NegExpr, self).__init__(exprs)

		assert len(exprs) == 1

	def eval(self, env):
		val = self.token_list[0].eval(env)
		if not isinstance(val, int):
			raise Exception("cannot negetive %s" % val)
		return -val


# block
class BlockExpr(ASTList):
	def __init__(self, token_list):
		super(BlockExpr, self).__init__(token_list)


# id
class IdExpr(ASTLeaf):
	def __init__(self, token):
		type_check(token, IdToken)

		super(IdExpr, self).__init__(token)

	def eval(self, env):
		return env.get_val(self.token.val)

	def set_val(self, val, env):
		return env.set_val(self.token.val, val)

	def get_name(self):
		return self.token.val


# num
class NumExpr(ASTLeaf):
	def __init__(self, token):
		super(NumExpr, self).__init__(token)


# str
class StrExpr(ASTLeaf):
	def __init__(self, token):
		super(StrExpr, self).__init__(token)


# op
class OpExpr(ASTLeaf):
	def __init__(self, token):
		super(OpExpr, self).__init__(token)
