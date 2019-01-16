# -*- coding:utf-8 -*-
from token import Token, IdToken
from environment import ClassEnvironment, FunEnvironment
from util import type_check
from ByteCode import ByteCode, get_binay_op_index


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
		opcodes = []
		for token in self.astnode_list:
			opcodes += token.eval(env)
		return opcodes

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
		opcodes = []
		# 赋值操作，需要单独处理
		if op == '=':
			type_check(self.left, (IdExpr, DotExpr))
			opcodes += self.right.eval(env)
			opcodes += self.left.set_val(env)
			return opcodes

		opcodes += self.right.eval(env)
		opcodes += self.left.eval(env)
		opcodes += ['BINARY_OP', get_binay_op_index(op)]
		return opcodes

	def lookup(self, env):
		op = self.op.eval(env)

		if op == '=' and isinstance(self.left, (IdExpr, DotExpr)) and isinstance(env, FunEnvironment):
			self.left.assign_indexs(env)

		self.left.lookup(env)

		self.right.lookup(env)


# 空语句
class NullExpr(ASTLeaf):
	def __init__(self, token):
		super(NullExpr, self).__init__(token)

	def eval(self, env):
		return []


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
		self.fun_name.eval(env)

		local_env = FunEnvironment(env)
		fun_code = self.block.eval(local_env)
		fun = ByteCode(fun_code, local_env.get_consts())
		const_index = env.assign_const(fun)

		opcodes = ["LOAD_CONST", self.fun_name.const_index] + ["LOAD_CONST", const_index] + ["MAKE_FUNCTION", self.local_size]
		if isinstance(env, FunEnvironment):
			return opcodes + ["STORE_LOCAL", self.fun_name.index, self.fun_name.nested_level]
		else:
			return opcodes + ["STORE_NESTED", self.fun_name.const_index]

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
		opcodes = sum([element.eval(env) for element in self.elements], [])
		return opcodes + ["MAKE_ARRAY", len(self.elements)]


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
		self.name.eval(env)
		opcodes = []

		opcodes += ['LOAD_CONST', self.name.const_index]

		if self.father_name is not None:
		else:
			opcodes += ['LOAD_CONST', env.assign_const(None)]

		local_env = ClassEnvironment(None)

		class_opcodes = self.members.eval(local_env)
		class_code = ByteCode(class_opcodes, local_env.get_consts())
		const_index = env.assign_const(class_code)

		opcodes += ["MAKE_CLASS", const_index]

		opcodes += ["STORE_NESTED", self.name.const_index]
		return opcodes

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

	def set_val(self, env):
		opcodes = []
		type_check(self.astnode_list[-1], (IdExpr, ArrayGetItemExpr))
		opcodes += self._get_val(env, self.astnode_list[:-1])

		if len(self.astnode_list) == 1:
			opcodes += self.astnode_list[-1].set_val(env)
		elif isinstance(self.astnode_list[-1], ArrayGetItemExpr):
			opcodes += self.astnode_list[-1].eval(env)
			opcodes += ["SET_ARRAY_ITEM"]
		else:
			self.astnode_list[-1].eval(env)
			opcodes += ["STORE_ATTR", self.astnode_list[-1].const_index]

		return opcodes

	# 获取exprs代表的环境
	def _get_val(self, env, exprs):
		opcodes = []
		for index, expr in enumerate(exprs):

			# 如果是函数调用
			if isinstance(expr, FunCallExpr):

				# 参数压栈
				for val in expr.args:
					opcodes += val.eval(env)

				opcodes += ["CALL_FUNCTION", len(expr.args)]
				continue

			elif isinstance(expr, ArrayGetItemExpr):
				opcodes += expr.eval(env)
				opcodes += ["GET_ARRAY_ITEM"]

			elif index == 0:
				opcodes += expr.eval(env)
			else:
				expr.eval(env)
				opcodes += ["LOAD_ATTR", expr.const_index]

		return opcodes

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
		elif self.elseblock:
			return self.elseblock.eval(env)
		return None
		else:
			else_codes = []

		return self.condition.eval(env) + ["JUMP_IF_FALSE", len(true_codes)] + true_codes + else_codes


# while
class WhileExpr(ASTList):
	def __init__(self, astnode_list):
		if len(astnode_list) != 2:
			raise Exception("len(astnode_list) in if should be 2 or 3 : %s", astnode_list)
		super(WhileExpr, self).__init__(astnode_list)

		self.condition = astnode_list[0]
		self.block = astnode_list[1]

	def eval(self, env):
		condition_codes = self.condition.eval(env)
		block_codes = self.block.eval(env)
		block_codes += ["JUMP_FRONT", -(len(block_codes) + len(condition_codes) + 4)]

		return condition_codes + ["JUMP_IF_FALSE", len(block_codes)] + block_codes


# -
class NegExpr(ASTList):
	def __init__(self, exprs):
		super(NegExpr, self).__init__(exprs)

		assert len(exprs) == 1

	def eval(self, env):
		return self.astnode_list[0].eval(env) + ['NEGTIVE']


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
		self.const_index = -1

	# 在命名空间中找到变量对应的值
	def eval(self, env):
		if self.const_index == -1:
			self.const_index = env.assign_const(self.get_name())

		if self.index != -1:
			type_check(env, (FunEnvironment))
			return ["LOAD_LOCAL", self.index, self.nested_level]
		return ["LOAD_NESTED", self.const_index]

	def set_val(self, env):
		if self.index != -1:
			return ["STORE_LOCAL", self.index, self.nested_level]

		if self.const_index == -1:
			self.const_index = env.assign_const(self.get_name())
		return ["STORE_NESTED", self.const_index]

	def get_name(self):
		return self.token.val

	def lookup(self, env):
		if not isinstance(env, FunEnvironment):
			return
		if self.index != -1:
			return

		self.index, self.nested_level = env.lookup(self.get_name())

	def assign_indexs(self, env):
		assert isinstance(env, FunEnvironment)

		self.index, self.nested_level = env.set_new_val(self.get_name())


# num
class NumExpr(ASTLeaf):
	def __init__(self, token):
		super(NumExpr, self).__init__(token)

	def eval(self, env):
		self.const_index = env.assign_const(self.token.val)
		return ['LOAD_CONST', self.const_index]


# str
class StrExpr(ASTLeaf):
	def __init__(self, token):
		super(StrExpr, self).__init__(token)

	def eval(self, env):
		self.const_index = env.assign_const(self.token.val)
		return ['LOAD_CONST', self.const_index]


# op
class OpExpr(ASTLeaf):
	def __init__(self, token):
		super(OpExpr, self).__init__(token)
