"""
Generic class to store a collection of data items.

Each data item within a collection has a unique key, and each 
attribute within a data item has a unique key.  An attribute of an 
item of a collection can be accessed like this:
data_collection[item_id][attribute_id]

Methods for loading and saving a data collection from a tab delimited file
are included here as well.

@author Norman MacDonald
@date 2010-02-16
"""

from __future__ import print_function
import sys

def error(*objs):
	print("ERROR: ", *objs, file=sys.stderr)
	
class DataItem:
	"""A keyed collection of attributes."""
	def __init__(self,identifier,dicFields):
		"""Initialize the id and dictionary of attributes."""
		self.dicFields = dicFields
		self.id = identifier
	def __getitem__(self,attribute):
		"""Return the attribute."""
		return self.dicFields[attribute]
	def __setitem__(self,attribute,value):
		"""Set the attribute."""
		self.dicFields[attribute] = value
		
	#python dictionaries are (key,value) based equality
	def __eq__(self,other):
		"""Return True if and only if all fields are the same (including the id)."""
		return self.dicFields == other.dicFields
		
	def keys(self):
		"""Return a list of attributes."""
		return self.dicFields.keys()
	def has_key(self,key):
		"""Return True if and only if the attribute is defined."""
		return self.dicFields.has_key(key)
		
	def get(self,key,default):
		"""Return the attribute value or default if it is not defined."""
		return self.dicFields.get(key,default)
	
		
class DataCollection:
	"""A collection of DataItems."""
	def __init__(self):
		"""Initialize an empty list of DataItems."""
		self._dicDataItems = {}
		self.lstNamedHeaders = []
	def add_data_item(self,dataitem):
		"""Add the data item to the collection."""
		self._dicDataItems[dataitem.id] = dataitem
	def __getitem__(self,instance):
		"""Return the data item with the given id."""
		return self._dicDataItems[instance]
	def __setitem__(self,key,value):
		"""Set the data item with the given id."""
		self._dicDataItems[key] = value
	def get(self,key,default):
		"""Get the data item with the given id."""
		return self._dicDataItems.get(key,default)
	def __iter__(self):
		"""Return a dictionary iterator of data items."""
		return self._dicDataItems.__iter__()
	def get_key_list(self):
		"""Get a list of all attributes defined of any data item in the collection.
		
		Note that each data item is searched for attributes before returning, and the list
		of ordered headers is updated with any new attributes.
		"""
		key_list = self.lstNamedHeaders[:]
		for i in self._dicDataItems.keys():
			for k in self._dicDataItems[i].keys():
				if k not in key_list:
					key_list.append(k)
		return key_list
		
	def has_key(self,key):
		"""Return True if and only if a data item exists with the given key."""
		return self._dicDataItems.has_key(key)
	def keys(self):
		"""Return a a list of data item ids.
		
		Note that this is different from get_key_list() which returns all data item attributes.
		"""
		return self._dicDataItems.keys()

	def get_category_counts(self):
		"""Return a dictionary with every attribute/value combination counted."""
		counts = {}
		keys = self.get_key_list()[1:]
		for item in self._dicDataItems.keys():
			for key in keys:
				value = self[item].get(key,"NULL")
				if not counts.has_key(key):
					counts[key] = {}
				if not counts[key].has_key(value):
					counts[key][value] = 0
				counts[key][value] += 1
		return counts
	
	def load_data_collection(self, filename):
		"""Load the tab delimited file into a data collection."""
		#datacollection.lstNamedHeaders = lstNamedHeaders
		f = open(filename)
		data = f.readlines()
		f.close()
		if len(data) > 1:
			keys = [x.strip() for x in data[0].split("\t")]
			idindex = -1
			#if len(lstNamedHeaders)>0:
			#	idindex = keys.index(datacollection.lstNamedHeaders[0])
			if idindex <0:
				idindex = 0
			for head in keys:
				if not head.strip() in self.lstNamedHeaders:
					self.lstNamedHeaders.append(head)
			for line in data[1:]:
				if len(line.strip()) > 0:
					dic = {}
					fields = [ x.strip() for x in line.split("\t") if len(x.strip())>0]
					for i in range(len(fields)):
						if keys[i] in self.lstNamedHeaders:
							dic[keys[i]]= fields[i]
					dataitem = DataItem(fields[idindex],dic)
					self.add_data_item(dataitem)
				else:
					pass #skip empty row
		else:
			error("File %r does not seem to contain any data (the first line is interpreted as metadata)." % filename)
			exit(1)
		
		return self # return an instance of DataCollection
		
	# RVF. test.py required class file, part of work-around.
	def null_data_collection(self, filename, targetclass):
		"""Create a NULL data collection."""
		with open(filename, 'r') as f:
			data = f.readlines()
		
		if len(data) > 0:
			if not targetclass in self.lstNamedHeaders:
				self.lstNamedHeaders.append(targetclass)
			for line in data:
				if len(line.strip()) > 0:
					dic = {}
					fields = []
					fields.append(line.split('\t')[0].strip())
					fields.append("NULL")
					dic[targetclass] = fields
					dataitem = DataItem(fields[0],dic)
					self.add_data_item(dataitem)
				else:
					pass #skip empty row
		else:
			error("File %r does not seem to contain any data." % filename)
			exit(1)
		
		return self # return an instance of DataCollection
		