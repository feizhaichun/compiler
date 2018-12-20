# -*- coding:utf-8 -*-
from ASTTree import BinaryExpr, IfExpr, WhileExpr, BlockExpr, NullExpr, NegExpr, NumExpr, IdExpr, StrExpr, DefExpr, FunCallExpr, ClassDefExpr, DotExpr, OpExpr
from ASTTree import ArrayGetItemExpr, ArrayDefExpr
from token import EOLToken, NumToken, IdToken, StrToken

'''
param		: IDENTIFIER
member		: def | simple
class_body	: "{" [member] {(";") | EOL) [member]} "}"
defclass	: "class" IDENTIFIER ["extends" IDENTIFIER] class_body
params		: param {"," param}
param_list	: "(" [params] ")"
args		: expr {"," expr}
postfix		: "(" [args] ")" | "." IDENTIFIER | "[" expr "]"
primary		: ("(" expr ")" | "[" args "]" | NUMBER | IDENTIFIER | STRING ) {postfix}
def     	: "def" IDENTIFIER param_list block
factor		: "-" primary | primary
expr 		: factor {OP factor}
block		: "{" [statement] {(";" | EOL) [statement] } "}"
simple		: expr
statement	: "if" expr block {"else" block}
			| "while" expr block
			| simple
			| def
program		: [def | statement | defclass] (";" | EOL)
'''


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
			"priority": 4
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
			return NullExpr(self.lexer.read())

		if self.isToken(IdToken('def')):
			ret = self.defs()
		elif self.isToken(IdToken('class')):
			ret = self.classdef()
		else:
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
		elif self.isToken(IdToken('def')):
			return self.defs()
		else:
			return self.simple()

	def simple(self):
		return self.expr()

	def block(self):
		self.absorb_or_assert(IdToken('{'))

		expr = []
		while not self.isToken(IdToken('}')):
			self.absorb_or_assert(IdToken(';'), EOLToken())

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
				factors.append(BinaryExpr([f1, OpExpr(ops.pop()), f2]))

			ops.append(op)
			factors.append(factor)

		while len(ops):
			f2 = factors.pop()
			f1 = factors.pop()
			op = ops.pop()
			factors.append(BinaryExpr([f1, OpExpr(op), f2]))

		assert(len(factors) == 1)
		assert(len(ops) == 0)
		return factors[0]

	def args(self):
		if self.isToken(IdToken(')')):
			return []

		ret = [self.expr()]

		while self.isToken(IdToken(',')):
			self.lexer.read()
			ret.append(self.expr())

		return ret

	def postfix(self):
		if self.isToken(IdToken('(')):
			self.absorb_or_assert(IdToken('('))
			ret = self.args()
			self.absorb_or_assert(IdToken(')'))
			return ret
		elif self.isToken(IdToken('[')):
			self.absorb_or_assert(IdToken('['))
			ret = ArrayGetItemExpr(self.expr())
			self.absorb_or_assert(IdToken(']'))
			return ret
		else:
			self.absorb_or_assert(IdToken('.'))
			return IdExpr(self.lexer.read())

	def factor(self):
		if self.isToken(IdToken('-')):
			self.lexer.read()
			return NegExpr([self.primary()])
		return self.primary()

	def primary(self):
		exprs = []

		if self.isToken(IdToken('(')):
			self.absorb_or_assert(IdToken('('))
			exprs.append(self.expr())
			self.absorb_or_assert(IdToken(')'))
		elif self.isToken(IdToken('[')):
			self.absorb_or_assert(IdToken('['))
			exprs.append(ArrayDefExpr(self.args()))
			self.absorb_or_assert(IdToken(']'))
		else:
			token = self.lexer.read()
			if isinstance(token, NumToken):
				exprs.append(NumExpr(token))
			elif isinstance(token, IdToken):
				assert(token != EOLToken())
				exprs.append(IdExpr(token))
			elif isinstance(token, StrToken):
				exprs.append(StrExpr(token))
			else:
				raise Exception('cannot find type of token : %s' % token)

		while self.isToken(IdToken('('), IdToken('.'), IdToken('[')):
			if self.isToken(IdToken('(')):
				exprs.append(FunCallExpr(self.postfix()))
			else:
				exprs.append(self.postfix())

		return DotExpr(exprs)

	def defs(self):
		self.lexer.read()
		assert(isinstance(self.lexer.peek(0), IdToken))
		fun_name = IdExpr(self.lexer.read())
		param_list = self.param_list()
		block = self.block()

		return DefExpr([fun_name, param_list, block])

	def param_list(self):
		self.absorb_or_assert(IdToken('('))

		ret = self.params()

		self.absorb_or_assert(IdToken(')'))

		return ret

	def params(self):
		if self.isToken(IdToken(')')):
			return []

		tokens = [self.param()]

		while self.isToken(IdToken(',')):
			self.lexer.read()
			tokens.append(self.param())

		return tokens

	def param(self):
		token = self.lexer.read()
		assert(isinstance(token, IdToken))
		return token

	def member(self):
		if self.isToken(IdToken('def')):
			return self.defs()
		return self.simple()

	def class_body(self):
		self.absorb_or_assert(IdToken('{'))
		members = []

		while not self.isToken(IdToken('}')):
			self.absorb_or_assert(IdToken(';'), EOLToken())

			if not self.isToken(IdToken('}')):
				members.append(self.member())

		self.absorb_or_assert(IdToken('}'))
		return members

	def classdef(self):
		self.absorb_or_assert(IdToken('class'))

		assert isinstance(self.lexer.peek(0), IdToken), (type(self.lexer.peek(0)), self.lexer.peek(0))
		class_name = IdExpr(self.lexer.read())

		father_class_name = None
		if self.isToken('extends'):
			self.absorb_or_assert(IdToken('extends'))
			father_class_name = self.lexer.read()
			assert isinstance(father_class_name), IdToken

		class_body = self.class_body()

		return ClassDefExpr([class_name, father_class_name, class_body])

	def isToken(self, *val):
		return self.lexer.peek(0) in val

	def isNextOp(self):
		next_token = self.lexer.peek(0)
		return isinstance(next_token, IdToken) and OP.is_op(next_token.val)

	def absorb_or_assert(self, *tokens):
		next_token = self.lexer.peek(0)

		assert next_token in tokens, "expect : %s, actually : %s at line : %d" % (tokens, next_token, self.lexer.get_line())

		if next_token in tokens:
			self.lexer.read()
			return True
