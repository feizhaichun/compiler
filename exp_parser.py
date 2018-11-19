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
# TODO 使用算符优先算法来实现算符优先级


class OP(object):
	op_priority = {
		'*': {
			"left_combination": True,
			"priority": 3,
		},
		'/': {
			"left_combination": True,
			"priority": 3,
		},
		'%': {
			"left_combination": True,
			"priority": 3,
		},


		'+': {
			"left_combination": True,
			"priority": 4,
		},
		'-': {
			"left_combination": True,
			"priority": 4,
		},

		'>': {
			"left_combination": True,
			"priority": 6,
		},
		'<': {
			"left_combination": True,
			"priority": 6,
		},

		'==': {
			"left_combination": False,
			"priority": 7,
		},

		'=': {
			"left_combination": False,
			"priority": 14,
		},
		'+=': {
			"left_combination": False,
			"priority": 14,
		},

	}

	def __init__(self):
		super(OP, self).__init__()

	@classmethod
	def is_op(cls, op):
		return op in cls.op_priority

	@classmethod
	def is_priority(cls, op1, op2):
		assert(isinstance(op1, IdToken))
		assert(isinstance(op2, IdToken))

		op1, op2 = op1.val, op2.val

		if not cls.is_op(op1):
			raise Exception("op : %s has not implement" % op1)
		if not cls.is_op(op2):
			raise Exception("op : %s has not implement" % op2)
		if cls.op_priority[op1]["priority"] != cls.op_priority[op2]["priority"]:
			return cls.op_priority[op1]["priority"] < cls.op_priority[op2]["priority"]
		return cls.op_priority[op1]["left_combination"]


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
		ops = []
		factors = [self.factor()]

		while self.isNextOp():
			op = self.lexer.read()
			factor = self.factor()

			while len(ops) and OP.is_priority(ops[-1], op):
				f2 = factors.pop()
				f1 = factors.pop()
				factors.append(BinaryExpr([f1, ops.pop(), f2]))

			ops.append(op)
			factors.append(factor)

		while len(ops):
			f2 = factors.pop()
			f1 = factors.pop()
			op = ops.pop()
			factors.append(BinaryExpr([f1, op, f2]))

		assert(len(factors) == 1)
		assert(len(ops) == 0)
		return factors[0]

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
		return isinstance(next_token, IdToken) and OP.is_op(next_token.val)
