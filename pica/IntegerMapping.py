"""This module generates maps between user-friendly strings and performance-minded integers"""


class IntegerMapping():
	def __init__(self):
		self.dic = {}
		self.arr = []
		self.max = -1
	
	def calculate_new_integer_map_for_list(self,list_X):
		xdic = {}
		xarr = []
		cval = -1
		
		for x in list_X:
			if not xdic.has_key(x):
				cval+=1
				xdic[x] = cval
				xarr.append(x)
		v_X = [xdic[x] for x in list_X]
		self.dic = xdic
		self.arr = xarr
		self.max = cval
		return v_X
	
	def int_to_str(self,i):
		return self.arr[i]
	
	def str_to_int(self,s):
		return self.dic[s]
	
	