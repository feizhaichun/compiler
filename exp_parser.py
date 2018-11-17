# -*- coding:utf-8 -*-
from ASTTree import BinaryExpr, IfExpr, WhileExpr, BlockExpr, NullExpr, NegExpr, NumExpr, IdExpr, StrExpr
from token import EOLToken, NumToken, IdToken, StrToken

'''
primary		: "(" expr ")" | NUMBER | IDENTIFIER | STRING | EOL
factor		: "-" primary | primary
expr 		: factor {OP factor}
block		: "{" [statement] {(";" | EOL) [statement] } "}"
simple		: expr
statement	: "if" expr block {"else" block}
			| "while" expr block
			| simple
program		: [ statement ] (";" | EOL)
'''
# TODO NEXT 实现EOF， 实现Parser对上述代码的分析
# TODO 使用算符优先算法来实现算符优先级

OP = {
	'+': -1,			# 左结合
	'-': -1,			# 左结合
	'*': -1,			# 左结合
	'/': -1,			# 左结合
	'>': -1,			# 左结合
	'<': -1,			# 左结合
	'==': -1,			# 左结合
	'%': -1,			# 左结合
	'+=': -1,			# 左结合

	'=': 1,			# 右结合
}


class Parser(object):
	def __init__(self, lexer):
		super(Parser, self).__init__()
		self.lexer = lexer

	def program(self):
		if self.isToken(EOLToken()) or self.isToken(IdToken(';')):
			return NullExpr([self.lexer.read()])

		ret = self.statement()
		if not self.isToken(EOLToken()) and not self.isToken(IdToken(';')):
			raise Exception('expected: EOL or ;, instead : （%s） at line %d ' % (self.lexer.peek(0), self.lexer.get_line()))
		self.lexer.read()
		return ret

	def statement(self):
		if self.isToken(IdToken('if')):
			exprs = []
			self.lexer.read()
			exprs.append(self.expr())
			exprs.append(self.block())
			if self.isToken(IdToken('else')):
				self.lexer.read()
				exprs.append(self.block())
			return IfExpr(exprs)
		elif self.isToken(IdToken('while')):
			exprs = []
			self.lexer.read()
			exprs.append(self.expr())
			exprs.append(self.block())
			return WhileExpr(exprs)
		else:
			return self.simple()

	def simple(self):
		return self.expr()

	def block(self):
		if not self.isToken(IdToken('{')):
			raise Exception('missing { at %s, instead is : %s' % (self.lexer.get_line(), self.lexer.peek(0)))
		self.lexer.read()
		expr = []
		while not self.isToken(IdToken('}')):
			if not self.isToken(IdToken(';')) and not self.isToken(EOLToken()):
				raise Exception('missing ; or EOL at %s, instead is : %s' % (self.lexer.get_line(), self.lexer.peek(0)))
			self.lexer.read()

			if not self.isToken(IdToken('}')):
				expr.append(self.statement())
		self.lexer.read()
		return BlockExpr(expr)

	def expr(self):
		stk = [self.factor()]

		while self.isNextOp():
			op = self.lexer.read()
			if self.is_op_left_combination(op):
				prev = stk.pop()
				stk.append(BinaryExpr([prev, op, self.factor()]))
			else:
				stk.append(op)
				stk.append(self.factor())

		while len(stk) > 1:
			right = stk.pop()
			op = stk.pop()
			left = stk.pop()
			stk.append(BinaryExpr([left, op, right]))

		return stk[0]

	def factor(self):
		if self.isToken(IdToken('-')):
			self.lexer.read()
			return NegExpr(self.primary())
		return self.primary()

	def primary(self):
		if self.isToken(IdToken('(')):
			self.lexer.read()
			ret = self.expr()
			if not self.isToken(IdToken(')')):
				raise Exception('missing ) at %s' % self.lexer.get_line())
			self.lexer.read()
			return ret

		token = self.lexer.read()
		if isinstance(token, NumToken):
			return NumExpr(token)
		elif isinstance(token, IdToken):
			return IdExpr(token)
		elif isinstance(token, StrToken):
			return StrExpr(token)
		else:
			raise Exception('cannot find type of token : %s' % token)

	def isToken(self, val):
		return self.lexer.peek(0) == val

	def isNextOp(self):
		next_token = self.lexer.peek(0)
		return any(next_token == IdToken(op) for op in OP)

	def is_op_left_combination(self, op):
		return OP[op.val] == -1
