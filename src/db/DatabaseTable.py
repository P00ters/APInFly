# -*- coding: utf-8 -*-
"""Module containing logic and functions to model a database table.

Allows for a database table to be stored and interacted with. Allows for renaming of 
the table and retrieval of relational information.
"""

from shared.SharedServices import force_type
from db.AliasName import AliasName
from db.DatabaseField import DatabaseField
from db.ProtectionOption import ProtectionOption

class DatabaseTable:
	"""Class containing logic and functions to model a database table.

	Allows for a database table to be stored and interacted with. Allows for renaming of 
	the table and retrieval of relational information.
	
	Attributes: 
		name (str): The name of the table.
		fq_name (str): The fully qualified name of the table.
		db_name (str): The name of this field in the context of sql.
		api_name (AliasName): The names of this table in the context of api calls.
		parent (Database): The database this table belongs to.
		children (list of DatabaseField): The child fields in this table. 
		protection (ProtectionOption, optional): API protections to apply to the table. 
	"""
	def __init__ (self, name, parent, children, **kwargs):
		caller = 'DatabaseTable.__init__'
		force_type(name, 'str', caller=caller)
		force_type(parent, 'db.Database.Database', caller=caller)
		force_type(children, 'list', caller=caller)
		for c in children:
			force_type(c, 'db.DatabaseField.DatabaseField', caller=caller)
			
		self.name = name
		self.fq_name = parent.name + '.' + name
		self.api_name = AliasName(self.fq_name)
		self.db_name = None
		self.parent = parent
		self.children = children
			
		if 'protection' in kwargs:
			force_type(kwargs.get('protection'), 'db.ProtectionOption.ProtectionOption', caller=caller)
			self.protection = kwargs.get('protection')
		else:
			self.protection = ProtectionOption(self.fq_name)
			
	def clone (self):
		d = DatabaseTable(self.name, self.parent, self.children, protection=self.protection)
		d.db_name = self.db_name
		d.api_name = self.api_name
		return d