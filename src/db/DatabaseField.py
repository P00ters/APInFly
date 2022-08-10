# -*- coding: utf-8 -*-
"""Module containing logic and functions to model a database field.

Allows for a database field to be stored and interacted with. Allows for renaming of 
the field and retrieval of relational information.
"""

from shared.SharedServices import force_type
from db.AliasName import AliasName
from db.ProtectionOption import ProtectionOption

class DatabaseField:
	"""Class containing logic and functions to model a database field.

	Allows for a database field to be stored and interacted with. Allows for renaming of 
	the field and retrieval of relational information. Used in generating schema.
	
	Attributes:
		name (str): The name of the field.
		fq_name (str): The fully qualified name of the field. 
		db_name (str): The name of this field in the context of sql.
		api_name (str): The names of this field in the context of api calls.
		parent (DatabaseTable): The table this field belongs to.
		grandparent (Database): The database this field's parent table belongs to.
		typ (str): The data type of the field.
		nullable (bool): Whether the field can be set to null.
		key (str): If the field is a key and what type of key it is.
		default (bool): If the field has a defualt value set.
		protection (ProtectionOption, optional): API protections to apply to field. Defaults to None.
		relation (DatabaseField, optional): If this is a foreign key, what field this relates to.
	"""
	def __init__ (self, name, parent, grandparent, typ, nullable, key, default, **kwargs):
		caller = 'DatabaseField.__init__'
		force_type(name, 'str', caller=caller)
		force_type(parent, 'db.DatabaseTable.DatabaseTable', caller=caller)
		force_type(grandparent, 'db.Database.Database', caller=caller)
		force_type(typ, 'str', caller=caller)
		force_type(nullable, 'bool', caller=caller)
		force_type(key, 'str', caller=caller)
		force_type(default, 'bool', caller=caller)
		
		self.name = name
		self.fq_name = grandparent.name + '.' + parent.name + '.' + name
		self.api_name = AliasName(self.name)
		self.sql_name = None
		self.parent = parent
		self.grandparent = grandparent
		self.typ = typ
		self.nullable = nullable
		self.key = key 
		self.default = default
		
		if 'protection' in kwargs:
			force_type(kwargs.get('protection'), 'db.ProtectionOption.ProtectionOption', caller=caller)
			self.protection = kwargs.get('protection')
		else:
			self.protection = ProtectionOption(self.fq_name)
		if 'relation' in kwargs:
			force_type(kwargs.get('relation'), 'db.DatabaseField.DatabaseField', caller=caller)
			self.relation = kwargs.get('relation')
		else:
			self.relation = None
			
	
	def clone (self):
		"""Clones this DatabaseField into a duplicate object.
		
		Returns:
			DatabaseField: The duplicate object.
		"""
		if self.relation != None:
			return DatabaseField(self.name, self.parent, self.grandparent, self.typ, self.nullable, self.key, self.default, protection=self.protection, relation=self.relation)
		else:
			return DatabaseField(self.name, self.parent, self.grandparent, self.typ, self.nullable, self.key, self.default, protection=self.protection)
		