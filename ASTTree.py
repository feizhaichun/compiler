# -*- coding:utf-8 -*-


class ASTNode(object):
	def __init__(self):
		super(ASTNode, self).__init__()


# 叶子节点，代表终结符
class ASTLeaf(ASTNode):
	def __init__(self, token):
		super(ASTLeaf, self).__init__()
		self.token = token

	def __str__(self):
		return str(self.token.val)


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


# 双目操作符
class BinaryExpr(ASTList):
	def __init__(self, token_list):
		super(BinaryExpr, self).__init__(token_list)


# 空语句
class NullExpr(ASTList):
	def __init__(self, token_list):
		super(BinaryExpr, self).__init__(token_list)


# if
class IfExpr(ASTList):
	def __init__(self, token_list):
		if len(token_list) != 2 and len(token_list) != 3:
			print token_list
			raise Exception("len(token_list) in if should be 2 or 3 : %s", token_list)
		self.token_list = token_list


# while
class WhileExpr(ASTList):
	def __init__(self, token_list):
		if len(token_list) != 2:
			raise Exception("len(token_list) in if should be 2 or 3 : %s", token_list)
		super(WhileExpr, self).__init__(token_list)


# -
class NegExpr(ASTList):
	def __init__(self, token_list):
		if len(token_list) != 2:
			raise Exception("len(token_list) in if should be 2 or 3 : %s", token_list)
		super(NegExpr, self).__init__(token_list)


# block
class BlockExpr(ASTList):
	def __init__(self, token_list):
		super(BlockExpr, self).__init__(token_list)
