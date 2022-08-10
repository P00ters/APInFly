# -*- coding: utf-8 -*-
"""Module implementing common functions for all database providers.

Condenses common database functions like connecting, closing and querying for 
all different providers into one common interface. 
"""

from shared.SharedServices import force_type
from db.providers.MySQL import MySQL

class DatabaseConnection:
	"""Provides connection and querying functions for any database.
	
	Condenses common database functions like connecting, closing and querying for 
	all different providers into one common interface.
	
	Attributes:
		dbc (db.DatabaseConnectionOption.DatabaseConnectionOption): The connection
			options specifying what and how to connect to the database.
	"""
	def __init__ (self, dbc):
		caller = 'DatabaseConnection.__init__'
		force_type(dbc, 'db.DatabaseConnectionOption.DatabaseConnectionOption', caller=caller)
		
		self.dbc = dbc
		
		if self.dbc.provider == 'mysql':
			self.provider = MySQL(self.dbc)
			
		self.__force_valid()
		
	def __force_valid (self):
		"""Ensures that the connection is valid.
		
		Checks to make sure that the database specified in the passed `DatabaseConnectionOption`
		is a valid database and can be connected to.
		
		Raises:
			ValueError: If the specified database connection options don't result in a connection.
		"""
		if not self.provider.is_valid():
			caller = 'DatabaseConnection.__force_valid'
			msg = '[' + caller + '] Unable to establish connection with specified DatabaseConnectionOption'
			raise ValueError(msg)
			
	def query (self, sql):
		"""Queries the provider and returns sql rows as a list.
		
		Returns:
			list of tuple: The rows resulting from the query.
		"""
		return self.provider.query(sql)
		
		
	def connect (self):
		"""Makes provider establish connection to the database.
		
		Returns:
			bool: True if the connection was established successfully, False if not.
		"""
		return self.provider.connect()
		
	def get_schema (self):
		"""Gets the schema of the database in the connection.
		
		Returns:
			list of Database: The schema of the underlying database.
		"""
		return self.provider.get_schema()