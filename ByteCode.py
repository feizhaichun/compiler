# -*- coding:utf-8 -*-
# from environment import NestedEnvironment
from objects import Func, Method, InstanceInfo, ClassInfo
from environment import FunEnvironment, ClassEnvironment
from util import type_check

ByCodeInfo = {
	"LOAD_CONST": {
		"lenth": 1,
	},

	"STORE_NESTED": {
		"lenth": 1,
	},

	"LOAD_NESTED": {
		"lenth": 1,
	},

	"NEGTIVE": {
		"lenth": 0,
	},

	"BINARY_OP": {
		"lenth": 1,
	},

	"JUMP_IF_FALSE": {
		"lenth": 1,
	},

	"JUMP_FRONT": {
		"lenth": 1,
	},

	"MAKE_FUNCTION": {
		"lenth": 1,
	},

	"CALL_FUNCTION": {
		"lenth": 1,
	},

	"LOAD_LOCAL": {
		"lenth": 2,
	},

	"STORE_LOCAL": {
		"lenth": 2
	},

	"MAKE_CLASS": {
		"lenth": 1
	},

	"STORE_ATTR": {
		"lenth": 1
	},

	"LOAD_ATTR": {
		"lenth": 1,
	},

	"MAKE_ARRAY": {
		"lenth": 1,
	},

	"GET_ARRAY_ITEM": {
		"lenth": 0,
	},

	"SET_ARRAY_ITEM": {
		"lenth": 0,
	}
}

BinaryOpIndex = {
	'<': 0,
	'>': 1,
	'==': 2,
	'+': 3,
	'-': 4,
	'*': 5,
}


def get_binay_op_index(op):
	return BinaryOpIndex[op]

Index2BinarayOp = {}
for k, v in BinaryOpIndex.items():
	Index2BinarayOp[v] = k


class ByteCode(object):
	def __init__(self, opcodes, consts):
		self.opcodes = opcodes
		self.consts = consts

	def eval(self, env):
		sp = 0
		stk = []

		while sp < len(self.opcodes):

			op = self.opcodes[sp]
			op_lenth = ByCodeInfo[op]["lenth"]
			op_args = self.opcodes[sp + 1: sp + 1 + op_lenth]
			sp += op_lenth + 1

			if op == "LOAD_CONST":
				stk.append(self.consts[op_args[0]])
				continue

			if op == "STORE_NESTED":
				name = self.consts[op_args[0]]
				val = stk.pop()

				env.set_val(name, val)
				stk.append(val)
				continue

			if op == "LOAD_NESTED":
				name = self.consts[op_args[0]]
				val = env.get_val(name)

				if val is None:
					print '%s is not assign' % name
				stk.append(val)
				continue

			if op == "BINARY_OP":
				kind = Index2BinarayOp[op_args[0]]
				u = stk.pop()
				v = stk.pop()

				if kind == '<':
					stk.append(u < v)
				elif kind == '>':
					stk.append(u > v)
				elif kind == '==':
					stk.append(u == v)
				elif kind == '+':
					stk.append(u + v)
				elif kind == '-':
					stk.append(u - v)
				elif kind == '*':
					stk.append(u * v)
				continue

			if op == "JUMP_IF_FALSE":
				u = stk.pop()
				if not u:
					sp += op_args[0]
				continue

			if op == "JUMP_FRONT":
				sp += op_args[0]
				continue

			if op == "NEGTIVE":
				u = stk.pop()
				stk.append(-u)
				continue

			if op == "MAKE_FUNCTION":
				code = stk.pop()
				fun_name = stk.pop()
				local_size = op_args[0]
				stk.append(Func(fun_name, code, env, local_size))
				continue

			if op == "CALL_FUNCTION":
				arg_size = op_args[0]
				args = []

				for _ in xrange(arg_size):
					args.append(stk.pop())
				args = args[::-1]
				fun_ob = stk.pop()

				if isinstance(fun_ob, (Func, Method)):				# 函数调用

					# 内部空间
					if isinstance(fun_ob, Method):
						instance_info = fun_ob.this
						fun_ob = fun_ob.func
						local_env = FunEnvironment(fun_ob.env, fun_ob.local_size, instance_info)

						# 参数
						for index, val in enumerate(args):
							local_env.set_local(index + 1, 0, val)		# 第0位是this
					else:
						local_env = FunEnvironment(fun_ob.env, fun_ob.local_size, None)

						# 参数
						for index, val in enumerate(args):
							local_env.set_local(index, 0, val)
					local_env.set_consts(fun_ob.bytecode.consts)

					# 执行函数
					stk.append(fun_ob.bytecode.eval(local_env))
				else:											# 构造函数调用
					class_info = fun_ob

					# 创建对象
					instance_info = InstanceInfo(class_info.name, ClassEnvironment(class_info.local_env))

					# 执行初始化函数,暂时不支持带参的构造函数
					try:
						constructor = class_info.local_env.get_val(class_info.name)
						type_check(constructor, Func)
						local_env = FunEnvironment(constructor.env, constructor.local_size, instance_info)
						constructor.bytecode.eval(local_env)
					except NameError:
						pass

					stk.append(instance_info)
				continue

			if op == "LOAD_LOCAL":
				stk.append(env.get_local(op_args[0], op_args[1]))
				continue

			if op == "STORE_LOCAL":
				val = stk.pop()
				env.set_local(op_args[0], op_args[1], val)
				continue

			if op == "MAKE_CLASS":
				class_opcodes = self.consts[op_args[0]]
				father_class = stk.pop()
				if not father_class:
					class_env = ClassEnvironment(None)
				else:
					raise NotImplementedError()

				class_name = stk.pop()

				class_opcodes.eval(class_env)
				stk.append(ClassInfo(class_name, class_env))
				continue

			if op == "STORE_ATTR":
				class_info = stk.pop()
				val = stk.pop()
				stk.append(class_info.set_val(self.consts[op_args[0]], val))
				continue

			if op == "LOAD_ATTR":
				class_info = stk.pop()
				val = class_info.get_val(self.consts[op_args[0]])
				stk.append(val)
				continue

			if op == "MAKE_ARRAY":
				array = []
				for _ in xrange(op_args[0]):
					array.append(stk.pop())
				array = array[::-1]
				stk.append(array)
				continue

			if op == "GET_ARRAY_ITEM":
				index = stk.pop()
				array = stk.pop()
				stk.append(array[index])
				continue

			if op == "SET_ARRAY_ITEM":
				index = stk.pop()
				array = stk.pop()
				val = stk.pop()

				array[index] = val
				stk.append(val)
				continue

			assert False, "%s has not implement" % op

		# TODO:把不用的东西退栈
		return stk[-1] if len(stk) else None
