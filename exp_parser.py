# -*- coding:utf-8 -*-
from ASTTree import BinaryExpr

'''
factor  	: NUMBER | "(" expression ")"
term 		: factor { ("*" | "/" factor)}
expression	: term { ("+" | "-") term}
'''


class Parser(object):
	def __init__(self, lexer):
		super(Parser, self).__init__()
		self.lexer = lexer

	def expression(self):
		left = self.term()
		while self.isToken('+') or self.isToken('-'):
			mid = self.lexer.read()
			right = self.term()
			left = BinaryExpr([left, mid, right])
		return left

	def term(self):
		left = self.factor()
		while self.isToken('*') or self.isToken('/'):
			mid = self.lexer.read()
			right = self.factor()
			left = BinaryExpr([left, mid, right])
		return left

	def factor(self):
		if self.isToken('('):
			self.lexer.read()
			ret = self.expression()
			self.lexer.read()
			return ret
		else:
			return self.lexer.read()

	def isToken(self, val):
		next_val = self.lexer.peek(0)
		return next_val is not None and next_val.val == val
