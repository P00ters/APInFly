"""Module containing logic to represent an API context/model.

Attributes:
	API_REL_CHAR (str): Character to separate relations in API naming scheme.
"""

import copy
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
		self.reqs = []
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
		self.reqs.append([])
		for f in self.tables[0].children:
			self.model[f.fq_name] = f.clone()
			self.model[f.fq_name].sql_name = tid + '.' + self.model[f.fq_name].name
			f.sql_name = tid + '.' + self.model[f.fq_name].name
			self.reqs[0].append(f.name)
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
		self.reqs.append([])
		
		for f in parent_table.children:
			g = f.clone()
			
			parent[f.fq_name] = g
			parent[f.fq_name].sql_name = tid + '.' + parent[f.fq_name].name
			new = api_name_p1 + f.name
			parent[f.fq_name].api_name.name = new
			
			self.reqs[len(self.tables) - 1].append(parent[f.fq_name].api_name.name)

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
		
	
	def flat_fields (self):
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
		
	def post_sql_parts (self, packed):
		"""Method to generate first pieces of sql queries for insertions.
		
		Args:
			packed (dict): Values packed into and paralleling the model dict.
		
		Returns:
			(list of list of str, list of DatabaseField): A list of insertion statements to be appended onto with values.
		"""
		sql = []
		
		s = 'INSERT INTO ' + self.tables[0].fq_name + '\nVALUES\n('
		for key in packed:
			if '_branch' not in key:
				if key + '_branch' in packed:
					if 'varchar' in self.model[key].typ:
						s += "'" + str(packed[key]) + "',"
					else:
						s += str(packed[key]) + ','
					self.__post_sql_parts_rec(packed[key + '_branch'], self.model[key + '_branch'], self.model[key].relation, sql)
				else:
					if 'varchar' in self.model[key].typ:
						s += "'" + str(packed[key]) + "',"
					else:
						s += str(packed[key]) + ','
		s = s[:len(s) - 1]
		s += ');'
		sql.append(s)
		
		return sql
		
	def __post_sql_parts_rec (self, pack_node, model_node, reld, sql):
		pt = reld.parent
		s = 'INSERT INTO ' + pt.fq_name + '\nVALUES\n('
		for key in pack_node:
			if '_branch' not in key:
				if key + '_branch' in pack_node:
					if 'varchar' in model_node[key].typ:
						s += "'" + pack_node[key] + "',"
					else:
						s += str(pack_node[key]) + ','
					self.__post_sql_parts_rec(pack_node[key + '_branch'], model_node[key + '_branch'], sql)
				else:
					if 'varchar' in model_node[key].typ:
						s += "'" + pack_node[key] + "',"
					else:
						s += str(pack_node[key]) + ','
		s = s[:len(s) - 1]
		s += ');'
		sql.append(s)
		
	def del_sql_parts (self, packed):
		sql = []
		s = 'DELETE FROM ' + self.tables[0].fq_name + ' WHERE '
		for key in packed:
			if '_branch' not in key:
				if 'PRI' in self.model[key].key:
					if 'char' in self.model[key].typ:
						s += self.model[key].name + "='" + str(packed[key]) + "'"
					else:
						s += self.model[key].name + '=' + str(packed[key])
				if key + '_branch' in packed:
					rel_t = self.model[key].relation.parent
					self.__del_sql_parts_rec(packed[key + '_branch'], self.model[key + '_branch'], rel_t, sql)
		
		s += ';'
		sql.append(s)
		return sql
		
	def __del_sql_parts_rec (self, pack_node, model_node, rel_t, sql):
		s = 'DELETE FROM ' + rel_t.fq_name + ' WHERE '
		for key in pack_node:
			if '_branch' not in key:
				if 'PRI' in model_node[key].key:
					if 'char' in model_node[key].typ:
						s += model_node[key].name + "='" + str(pack_node[key]) + "'"
					else:
						s += model_node[key].name + '=' + str(pack_node[key])
				if key + '_branch' in pack_node:
					rel_t = model_node[key].relation.parent
					self.__del_sql_parts_rec(pack_node[key + '_branch'], model_node[key + '_branch'], rel_t, sql)
					
		s += ';'
		sql.append(s)
		
	def to_model_pack (self, pack):
		model_pack = {}
		for key in self.model:
			if '_branch' not in key:
				if key + '_branch' in self.model:
					model_pack[key] = self.model[key].relation.api_name.name
					model_pack[key + '_branch'] = {}
					model_pack[key] = self.__to_model_pack_rec(model_pack[key + '_branch'], pack[self.model[key].api_name.name], self.model[key + '_branch'], model_pack[key])
				else:
					model_pack[key] = pack[self.model[key].api_name.name]
		return model_pack
		
	def __to_model_pack_rec (self, hook, val_node, model_node, rel_f):
		
		retval = None
		
		for key in model_node:
			if model_node[key].name == rel_f:
				retval = val_node[model_node[key].api_name.name]
			if '_branch' not in key:
				if key + '_branch' in model_node:
					hook[key] = model_node[key].relation.api_name.name
					hook[key + '_branch'] = {}
					hook[key] = self.__to_model_pack_rec(hook[key + '_branch'], val_node[model_node[key].api_name.name], model_node[key + '_branch'], hook[key])
				else:
					hook[key] = val_node[model_node[key].api_name.name]
		return retval
	
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
	
	def pack_api (self, packed):
		"""Repacks model packed dict into dict with valid api key names.
		"""
		pack_api = {}
		for key in packed:
			if '_branch' not in key:
				if key + '_branch' in packed:
					api_n = self.model[key].api_name.name
					pack_api[api_n] = {}
					self.__pack_api_rec(pack_api[api_n], packed[key + '_branch'], self.model[key + '_branch'])
				else:
					api_n = self.model[key].api_name.name
					pack_api[api_n] = packed[key]
					
		return pack_api
	
	def __pack_api_rec (self, new_node, val_node, model_node):
		for key in val_node:
			if '_branch' not in key:
				if key + '_branch' in val_node:
					api_n = model_node[key].api_name.name
					new_node[api_n] = {}
					self.__pack_api_rec(new_node[api_n], val_node[key + '_branch'], model_node[key + '_branch'])
				else:
					api_n = model_node[key].api_name.name
					new_node[api_n] = val_node[key]
	
	def pack_single (self, d):
		"""Packs values for a single instance of this context into a dict.
		
		Args:
			d (dict): A flat dict of context values.
			
		Raiases:
			AttributeError: If d is missing a required value. 
		"""
		model = copy.deepcopy(self.model)
		for key in model:
			if '_branch' not in key:
				this_field = model[key]
				if this_field.api_name.name not in d:
					if key + '_branch' in model:
						new_id = this_field.relation.parent.gen_id()
						rel_field = model[key]
						model[key] = new_id
						self.__pack_single_rec(model[key + '_branch'], rel_field, new_id, d)
					else:
						if 'PRI' in this_field.key:
							new_id = self.tables[0].gen_id()
							model[key] = new_id
						else:
							print("Missing key '" + key + "'")
							raise AttributeError("Missing key '" + key + "'")
				else:
					model[key] = d[this_field.api_name.name]
		
		return model
	
	def __pack_single_rec (self, node, rel_field, new_id, d):
		for key in node:
			if '_branch' not in key:
				this_field = node[key]
				if this_field.api_name.name not in d:
					if key + '_branch' in node:
						n_id = this_field.relation.parent.gen_id()
						rel_f = node[key]
						node[key] = n_id
						self.__pack_single_rec(node[key + '_branch'], rel_f, n_id, d)
					else:
						if 'PRI' in this_field.key:
							n_id = this_field.parent.gen_id()
							node[key] = n_id
						else:
							raise AttributeError("Missing key '" + key + "'")
				else:
					node[key] = d[this_field.api_name.name]
					
		for key in node:
			if key == rel_field.relation.fq_name:
				node[key] = new_id
				
				
		