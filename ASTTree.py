# -*- coding:utf-8 -*-
from token import IdToken, get_true_value


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
		super(ASTLeaf, self).__init__()
		self.token = token

	def __str__(self):
		return str(self.token.val)

	def eval(self, env):
		return self.token


# 非叶子节点，代表非终结符
class ASTList(ASTNode):
	def __init__(self, token_list):
		super(ASTList, self).__init__()
		self.token_list = token_list

	def __str__(self):
		ret = ['(']
		for element in self.token_list:
			if isinstance(element, ASTNode):
				ret.append(str(element))
			else:
				ret.append(str(element.val))
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

	def eval(self, env):
		left = self.left.eval(env)
		right = self.right.eval(env)
		op = self.op.val

		# if为赋值操作，需要单独处理
		if op == '=':
			assert isinstance(left, IdToken)
			env.set_val(left.val, get_true_value(right, env))
			return env.get_val(left.val)

		left = get_true_value(left, env)
		right = get_true_value(right, env)
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
		if get_true_value(self.condition.eval(env), env):
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
		while get_true_value(self.condition.eval(env), env):
			ret = self.block.eval(env)
		return ret


# -
class NegExpr(ASTLeaf):
	def __init__(self, token_list):
		super(NegExpr, self).__init__(token_list)

	def eval(self, env):
		val = get_true_value(self.token.eval(env), env)
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
		super(IdExpr, self).__init__(token)


# num
class NumExpr(ASTLeaf):
	def __init__(self, token):
		super(NumExpr, self).__init__(token)


# str
class StrExpr(ASTLeaf):
		def __init__(self, token):
			super(StrExpr, self).__init__(token)
