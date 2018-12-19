# -*- coding:utf-8 -*-
import sys
import traceback


def type_check(value, expected_type):
	if not isinstance(value, expected_type):
		raise TypeError('%s should be type [%s], instead is [%s]' % (value, expected_type, type(value)))


# 打印每帧中的局部变量的列表
def print_exc_plus():
	tb = sys.exc_info()[2]
	while tb.tb_next:
		tb = tb.tb_next

	stk = []
	f = tb.tb_frame
	while f:
		stk.append(f)
		f = f.f_back

	stk = stk[::-1]
	msg = traceback.format_exc()
	print msg

	print ('locals by frame, innermost last')
	for f in stk:
		print 'Frame %s in %s at line %s' % (f.f_code.co_name, f.f_code.co_filename, f.f_lineno)

		for k, v in f.f_locals.items():
			print '%20s = ' % k,

			try:
				print(v)
			except:
				print '<ERROR WHILE PRINTING VALUE>'
