# -*- coding:utf-8 -*-
from token import Token, IdToken
from environment import NestedEnvironment, ClassEnvironment, FunEnvironment
from objects import ArrayInfo, Func, Method, ClassInfo, InstanceInfo
from util import type_check


class ASTNode(object):
	def __init__(self):
		super(ASTNode, self).__init__()

	def eval(self, env):
		raise Exception('%s has not implement eval' % type(self))

	def __repr__(self):
		return self.__str__()

	def lookup(self, env):
		pass


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
	def __init__(self, astnode_list):
		super(ASTList, self).__init__()
		self.astnode_list = astnode_list

	def __str__(self):
		ret = ['(']
		for element in self.astnode_list:
			if isinstance(element, Token):
				ret.append(str(element.val))
			else:
				ret.append(str(element))
		ret.append(')')
		return ' '.join(ret)

	def eval(self, env):
		ret = None
		for token in self.astnode_list:
			ret = token.eval(env)
		return ret

	def lookup(self, env):
		ret = None
		for token in self.astnode_list:
			if isinstance(token, ASTNode):
				ret = token.lookup(env)

		return ret


# 双目操作符
class BinaryExpr(ASTList):
	def __init__(self, astnode_list):
		super(BinaryExpr, self).__init__(astnode_list)

		if len(astnode_list) != 3:
			raise Exception("len(astnode_list) in BinaryExpr must be 3 : %s", astnode_list)

		self.left, self.op, self.right = self.astnode_list

		type_check(self.op, OpExpr)

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

	def lookup(self, env):
		op = self.op.eval(env)

		if op == '=' and isinstance(self.left, (IdExpr, DotExpr)) and isinstance(env, FunEnvironment):
			self.left.assign_indexs(env)
		else:
			self.left.lookup(env)
		self.right.lookup(env)


# 空语句
class NullExpr(ASTLeaf):
	def __init__(self, token):
		super(NullExpr, self).__init__(token)

	def eval(self, env):
		return None


# 函数定义
class DefExpr(ASTList):
	def __init__(self, astnode_list):
		super(DefExpr, self).__init__(astnode_list)
		assert(len(astnode_list) == 3)

		self.fun_name = astnode_list[0]
		self.param_list = astnode_list[1]
		self.block = astnode_list[2]
		self.local_size = 0

		type_check(self.fun_name, IdExpr)
		type_check(self.param_list, list)
		type_check(self.block, BlockExpr)
		assert(all(isinstance(val, IdExpr) for val in self.param_list))

	def eval(self, env):
		return self.fun_name.set_val(Func(self.fun_name.get_name(), self.param_list, self.block, env, self.local_size), env)

	def lookup(self, env):
		# 函数名称
		if isinstance(env, FunEnvironment):
			self.fun_name.assign_indexs(env)

		local_env = FunEnvironment(env)

		# 对象的方法，需要分配一个this空间
		if isinstance(env, ClassEnvironment):
			local_env.set_new_val('this')

		for expr in self.param_list:
			expr.assign_indexs(local_env)
			assert expr.index != -1

		self.block.lookup(local_env)

		self.local_size = local_env.get_local_size()


# 函数调用
class FunCallExpr(ASTList):
	def __init__(self, token):
		super(FunCallExpr, self).__init__(token)

		self.args = token

	def eval(self, env, instance_info=None):
		raise NotImplementedError()


# 数组定义
class ArrayDefExpr(ASTList):
	def __init__(self, astnode_list):
		super(ArrayDefExpr, self).__init__(astnode_list)
		self.elements = astnode_list

	def eval(self, env):
		elements = [element.eval(env) for element in self.elements]
		return ArrayInfo(elements)


# 数组取值
class ArrayGetItemExpr(ASTList):
	def __init__(self, token):
		super(ArrayGetItemExpr, self).__init__([token])


# 类的定义表达式
class ClassDefExpr(ASTList):
	def __init__(self, astnode_list):
		super(ClassDefExpr, self).__init__(astnode_list)
		assert len(astnode_list) == 3, astnode_list

		type_check(astnode_list[0], IdExpr)

		self.name = astnode_list[0]
		self.father_name = astnode_list[1]
		self.members = astnode_list[2]

	def eval(self, env):
		father_env = None
		if self.father_name is not None:
			father_class = env.get_val(self.father_name)
			assert father_class is not None, 'class : %s cannot find his father : %s' % (self.name, self.father_name)
			father_env = father_class.local_env

		local_env = ClassEnvironment(father_env)

		self.members.eval(local_env)

		return self.name.set_val(ClassInfo(self.name.get_name(), local_env), env)

	def lookup(self, env):
		father_env = None
		if self.father_name is not None:
			father_class = env.get_val(self.father_name)
			assert father_class is not None, 'class : %s cannot find his father : %s' % (self.name, self.father_name)
			father_env = father_class.local_env

		local_env = ClassEnvironment(father_env)

		self.members.lookup(local_env)


# 方法访问
class DotExpr(ASTList):
	def __init__(self, astnode_list):
		super(DotExpr, self).__init__(astnode_list)

	def set_val(self, val, env):

		assert not isinstance(self.astnode_list[-1], FunCallExpr), 'cannot assign to a Function call'
		class_info = self._get_val(env, self.astnode_list[:-1])

		type_check(class_info, (ClassInfo, InstanceInfo, NestedEnvironment, ArrayInfo))

		if isinstance(self.astnode_list[-1], IdExpr):
			self.astnode_list[-1].set_val(val, class_info)
		else:
			class_info.set_val(self.astnode_list[-1].eval(env), val)

		return val

	# 获取exprs代表的环境
	def _get_val(self, env, exprs):
		cur_env = env

		for expr in exprs:

			# 如果是函数调用
			if isinstance(expr, FunCallExpr):
				assert isinstance(cur_env, (Func, Method, ClassInfo)), '%s is not callable' % type(expr)

				args = [val.eval(env) for val in expr.args]
				fun_ob = cur_env

				if isinstance(fun_ob, (Func, Method)):				# 函数调用

					# 内部空间
					if isinstance(fun_ob, Method):
						instance_info = fun_ob.this
						fun_ob = fun_ob.func
						local_env = FunEnvironment(fun_ob.env, fun_ob.local_size, instance_info)
					else:
						local_env = FunEnvironment(fun_ob.env, fun_ob.local_size, None)

					# 参数
					for name, val in zip(fun_ob.arglist, args):
						local_env.set_local(name.index, 0, val)

					# 执行函数
					cur_env = fun_ob.block.eval(local_env)
				else:											# 构造函数调用
					class_info = fun_ob

					# 创建对象
					instance_info = InstanceInfo(class_info.name, ClassEnvironment(class_info.local_env))

					# 执行初始化函数,暂时不支持带参的构造函数
					try:
						constructor = class_info.local_env.get_val(class_info.name)
						type_check(constructor, (Func))
						local_env = FunEnvironment(constructor.env, constructor.local_size, instance_info)
						constructor.block.eval(local_env)
					except NameError:
						pass

					cur_env = instance_info

			elif isinstance(expr, ArrayGetItemExpr):
				type_check(cur_env, ArrayInfo)
				index = expr.eval(env)
				cur_env = cur_env.get_item(index)
			else:
				cur_env = expr.eval(cur_env)
		return cur_env

	def eval(self, env):
		return self._get_val(env, self.astnode_list)

	def assign_indexs(self, env):
		type_check(self.astnode_list[0], IdExpr)
		self.astnode_list[0].assign_indexs(env)


# if
class IfExpr(ASTList):
	def __init__(self, astnode_list):
		if len(astnode_list) not in (2, 3):
			raise Exception("len(astnode_list) in if should be 2 or 3 : %s", astnode_list)
		super(IfExpr, self).__init__(astnode_list)

		self.condition = astnode_list[0]
		self.block = astnode_list[1]
		self.elseblock = astnode_list[2] if len(astnode_list) == 3 else None

	def eval(self, env):
		if self.condition.eval(env):
			return self.block.eval(env)
		elif self.elseblock:
			return self.elseblock.eval(env)
		return None


# while
class WhileExpr(ASTList):
	def __init__(self, astnode_list):
		if len(astnode_list) != 2:
			raise Exception("len(astnode_list) in if should be 2 or 3 : %s", astnode_list)
		super(WhileExpr, self).__init__(astnode_list)

		self.condition = astnode_list[0]
		self.block = astnode_list[1]

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
		val = self.astnode_list[0].eval(env)
		if not isinstance(val, int):
			raise Exception("cannot negetive %s" % val)
		return -val


# block
class BlockExpr(ASTList):
	def __init__(self, astnode_list):
		super(BlockExpr, self).__init__(astnode_list)


# id
class IdExpr(ASTLeaf):
	def __init__(self, token):
		type_check(token, IdToken)

		super(IdExpr, self).__init__(token)
		self.index = -1
		self.nested_level = -1

	# 在命名空间中找到变量对应的值
	def eval(self, env):
		if self.index != -1:
			type_check(env, (FunEnvironment))
			return env.get_local(self.index, self.nested_level)
		return env.get_val(self.get_name())

	def set_val(self, val, env):
		if self.index != -1:
			type_check(env, (FunEnvironment))
			return env.set_local(self.index, self.nested_level, val)

		return env.set_val(self.get_name(), val)

	def get_name(self):
		return self.token.val

	def lookup(self, env):
		if not isinstance(env, FunEnvironment):
			return

		assert self.index == -1

		self.index, self.nested_level = env.lookup(self.get_name())

	def assign_indexs(self, env):
		assert isinstance(env, FunEnvironment)

		self.index, self.nested_level = env.set_new_val(self.get_name())


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
