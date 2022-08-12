# -*- coding: utf-8 -*-
"""Module containing logic and functions to model a database.
"""

from shared.SharedServices import force_type
from db.DatabaseTable import DatabaseTable
from db.ProtectionOption import ProtectionOption

class Database:
	"""Class containing logic and functions to model a database.
	
	Attributes:
		name (str): The name of thedatabasetable.
		children (list of DatabaseTable): The children tables in this database.
		protection (ProtectionOption, optional): API protections to apply to the database.
	"""
	def __init__ (self, name, children, **kwargs):
		caller = 'Database.__init__'
		force_type(name, 'str', caller=caller)
		force_type(children, 'list', caller=caller)
		for c in children:
			force_type(c, 'db.DatabaseTable.DatabaseTable', caller=caller)
		
		self.name = name
		self.children = children
		
		if 'protection' in kwargs:
			force_type(kwargs.get('protection'), 'db.ProtectionOption.ProtectionOption', caller=caller)
			self.protection = kwargs.get('protection')
		else:
			self.protection = db.ProtectionOption.ProtectionOption(self.name)
			
		
			
	def assemble_contexts (self):
		"""Assembles model contexts for the database in its present state.
		
		Creates models for each table child in the database for use in API 
		querying.

		Returns:
			(list of APIContext): All of the models queryable in the context of the api.
		"""
		return
		
	