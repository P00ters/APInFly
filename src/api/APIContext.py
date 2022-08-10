"""Module containing logic to represent an API context/model.

Attributes:
	API_REL_CHAR (str): Character to separate relations in API naming scheme.
"""

from db.Database import Database
from db.DatabaseTable import DatabaseTable
from db.DatabaseField import DatabaseField
from db.ProtectionOption import ProtectionOption
from shared.SharedServices import force_type, is_type

API_REL_CHAR = '_'

class APIContext:
	"""Class representing an API context.
	
	An API context is the model derived from a database schema
	equating to the object represented by a table and its related tables.
	
	Attributes:
		schema (list of Database): The schema for the database as a list of Databases.
		table (DatabaseTable): The table to create the context for.
		model (dict of DatabaseField): The resultant model for this context.
	"""
	def __init__ (self, schema, table):
		caller = 'APIContext.__init__'
		force_type(schema, 'list', caller=caller)
		for d in schema:
			force_type(d, 'db.Database.Database', caller=caller)
		force_type(table, 'db.DatabaseTable.DatabaseTable', caller=caller)
		
		self.name = table.fq_name.replace('.', API_REL_CHAR)
		self.schema = schema
		self.table = table.clone()
		self.tables = []
		self.tables.append(self.table)
		self.joins = []
		
		self.gen_model()
		
	
	def gen_model (self):
		"""Generates the model for the table.
		
		Parses through relations to create a nested object model containing
		the table model. Creates default api names for fields and populates 
		sql naming in the fields.
		"""
		self.model = { }
		
		tid = 't1'
		self.tables[0].db_name = tid
		for f in self.table.children:
			self.model[f.fq_name] = f.clone()
			self.model[f.fq_name].sql_name = tid + '.' + self.model[f.fq_name].name
			if f.relation != None:
				joiner = self.tables[0].db_name + '.' + f.name + ' = t' + str(len(self.tables) + 1) + '.' + f.relation.name
				self.joins.append(joiner)
				self.model[f.fq_name + '_branch'] = {}
				self.branch_rel(self.model[f.fq_name + '_branch'], f)
	
	
	def branch_rel (self, parent, branch_field):
		"""Recursive method to follow branching relations out of the main table context.
		
		Args:
			branch_field (DatabaseField): The field with the relation to branch out on. 
		"""
		api_name_p1 = branch_field.api_name.name + API_REL_CHAR
		parent_table = branch_field.relation.parent
		self.tables.append(parent_table.clone())
		parent_table = self.tables[len(self.tables) - 1]
		tid = 't' + str(len(self.tables))
		self.tables[len(self.tables) - 1].db_name = tid
		
		for f in parent_table.children:
			parent[f.fq_name] = f.clone()
			parent[f.fq_name].sql_name = tid + '.' + parent[f.fq_name].name
			new = api_name_p1 + f.name
			parent[f.fq_name].api_name.name = new
			if f.relation != None:
				joiner = parent_table.db_name + '.' + f.name + ' = t' + str(len(self.tables) + 1) + '.' + f.relation.name
				self.joins.append(joiner)
				parent[f.fq_name + '_branch'] = {}
				self.branch_rel(parent[f.fq_name + '_branch'], parent[f.fq_name])
				
	
	def types_view (self):
		"""Generates the context model with type information.
		
		Returns:
			dict of [str, str]: A dictionary showing all field names and their data type.
		"""
		d = {}
		for key in self.model:
			if '_branch' not in key and key + '_branch' not in self.model:
				field = self.model[key]
				d[field.api_name.name] = field.typ
			else:
				if '_branch' not in key:
					field = self.model[key]
					d[field.api_name.name] = {}
					self.__types_rec(d[field.api_name.name], self.model[key + '_branch'])
				
					
		return d
			
			
	def __types_rec (self, hook, branch):
		"""Recursive method to iterate into child relations in generating the types view.
		"""
		for key in branch:
			if '_branch' not in key and key + '_branch' not in branch:
				field = branch[key]
				hook[field.api_name.name] = field.typ
			else:
				if '_branch' not in key:
					field = branch[key]
					hook[field.api_name.name] = {}
					self.__types_rec(hook[field.api_name.name], branch[key + '_branch'])
		
	
	def flat_fields (self, fields, parent):
		"""Method to retrieve all of the fields in the context flattened into a list.
		
		Returns:
			list of DatabaseField: The fields in one list.
		"""
		fields = []
		for key in self.model:
			if '_branch' not in key and key + '_branch' not in self.model:
				f = self.model[key]
				fields.append(f)
			else:
				if '_branch' in key:
					self.__flat_fields_rec(fields, self.model[key])
		
		return fields
		
		
	def __flat_fields_rec (self, fields, parent):
		for key in parent:
			if '_branch' not in key and key + '_branch' not in parent:
				f = parent[key]
				fields.append(f)
			else:
				if '_branch' in key:
					self.__flat_fields_rec(fields, parent[key])
					
	
	def get_sql_parts (self):
		"""Method to get the sql framework string for this context.
		
		Returns:
			str: The sql framework to use to query this context.
		"""
		sql = "SELECT \n\t"
		flat = self.flat_fields()
		for f in flat:
			sql_name = f.sql_name
			sql += sql_name + ', '
		sql = sql[:-2]
		sql += " \nFROM\n\t"
		for t in self.tables:
			sql += t.fq_name + ' AS ' + t.db_name + ', '
		sql = sql[:-2]
		
		sql += " \nWHERE\n\t"
		for j in self.joins:
			sql += j + ' AND '
		if len(self.joins) > 0:
			sql = sql[:-4]
		
		return sql
		
	
	def unpack_single (self, result):
		"""Unpacks a single instance of this context into a dict.
		
		Args:
			result (tuple): The result of a sql query from this context.
		"""
		fields = self.flat_fields()
		values = []
		for item in result:
			values.append(item)
			
		structure = self.types_view()
		
		for key in structure:
			if not is_type(structure[key], 'dict'):
				ind = -1
				for f in fields:
					if f.api_name.name == key:
						ind = fields.index(f)
				structure[key] = values[ind]
			else:
				self.__unpack_single_rec(fields, values, structure[key])
					
		return structure
		
	
	def __unpack_single_rec (self, fields, values, parent):
		for key in parent:
			if not is_type(parent[key], 'dict'):
				ind = -1
				for f in fields:
					if f.api_name.name == key:
						ind = fields.index(f)
				parent[key] = values[ind]
			else:
				self.__unpack_single_rec(fields, values, parent[key])
					
				
				
				
		