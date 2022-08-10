# -*- coding: utf-8 -*-
"""Module implementing mysql connection functionality.

Allows for connection to and querying of a mysql database. Also provides functionality to
generate a model of the schema of a valid mysql database.

Attributes:
	SCHEMA_EXCEPTIONS (list of str): A list of system tables to exclude when generating schema model.
"""

import mysql.connector
from mysql.connector import Error
from db.Database import Database
from db.DatabaseTable import DatabaseTable
from db.DatabaseField import DatabaseField
from db.ProtectionOption import ProtectionOption
from shared.SharedServices import force_type

SCHEMA_EXCEPTIONS = ['information_schema', 'mysql', 'performance_schema', 'sys']

class MySQL:
	"""Class implementing mysql connection functionality.
	
	Attributes:
		options (db.DatabaseConnectionOption.DatabaseConnectionOption): The connection options
			used to connect to the mysql database with.
			
	Raises:
		TypeError: If the options attribute is not a valid DatabaseConnectionOption.
	"""
	def __init__ (self, options):
		caller = 'MySQL.__init__'
		force_type(options, 'db.DatabaseConnectionOption.DatabaseConnectionOption', caller=caller)
		
		self.options = options
		
	def connect (self):
		"""Attempts to connect to the mysql database using the provider options.
		
		Returns:
			bool: True if the connection was established successfully, False if not.
		"""
		self.conn = None
		try:
			if self.options.options['port'] != None:
				port = self.options.options['port']
			else:
				port = 3306
			self.conn = mysql.connector.connect(host=self.options.options['host'], 
												port=port, 
												username=self.options.options['username'], 
												password=self.options.options['password'])
		except Error as e:
			print(e)
			return False
		return True
		
	def close (self):
		"""Closes the connection to the mysql database if it is already active.
		"""
		self.conn.close()
		self.conn = None
		
	def is_valid (self):
		"""Checks to see if the connection is valid.
		
		Attempts to make a connection to the mysql database with the supplied DatabaseConnectionOption
		and closes the connection if it was successful.
		
		Returns:
			(bool): True if the connection can be established, False if not. 
		"""
		valid = self.connect()
		if self.conn is not None:
			self.close()
		
		return valid
		
	def query (self, query):
		"""Executes a query on the mysql database.
		
		Attempts to execute a query on the specified database. If successful, it will collect and return 
		the result of that query as rows. 
		
		Args:
			query (str): The sql query string to attempt to execute.
		
		Returns:
			list of tuple: The results of the query in a list of rows. 
		
		Raises:
			RuntimeError: Raised if the query could not be successfully executed.
		"""
		caller = 'MySQL.__init__'
		force_type(query, 'str', caller=caller)
		
		result = []
		try:
			if self.connect():
				cursor = self.conn.cursor()
				cursor.execute(query)
				rows = cursor.fetchall()
				for row in rows:
					result.append(row)
			else:
				return None
		except Error as e:
			print(e)
			raise RuntimeError('[MySQL] Could not query with provider \'' + self.options.provider + '\' with query "' + query + '"')
		finally:
			self.close()
				
		return result
		
	def get_schema (self):
		"""Gets the schema of the database in the connection.
		
		Returns:
			list of Database: The schema of the underlying database.
		"""
		if not self.is_valid():
			raise RuntimeError('[MySQL] Unable to generate schema, database not valid')
			
		dbs = []
		
		db_available_query = 'SELECT schema_name FROM information_schema.schemata;'
		db_rows = self.query(db_available_query)
		if len(db_rows) > 0:
			for db_row in db_rows:
				db_name = db_row[0]
				p = ProtectionOption(db_name)
				if db_name not in SCHEMA_EXCEPTIONS:
					for protection in self.options.options['protection']:
						if protection.name == db_name:
							p = protection
					if not p.exclude:
						d = Database(db_name, [], protection=p)
						dbs.append(d)
		
		for d in dbs:
			table_available_query = 'SHOW tables FROM ' + d.name + ';'
			table_rows = self.query(table_available_query)
			for table_row in table_rows:
				table_name = table_row[0]
				p = ProtectionOption(d.name + '.' + table_name)
				for protection in self.options.options['protection']:
					if protection.name == d.name + '.' + table_name:
						p = protection
				if not p.exclude:
					t = DatabaseTable(table_name, d, [], protection=p)
					d.children.append(t)
					
		for d in dbs:
			for t in d.children:
				field_available_query = 'SHOW columns FROM ' + t.fq_name + ';'
				field_rows = self.query(field_available_query)
				for field_row in field_rows:
					field_name = field_row[0]
					field_type = str(field_row[1].decode('utf-8'))
					field_nullable = (True if field_row[2] == 'NO' else False)
					field_key = field_row[3]
					field_default = (False if field_row[4] == 'None' else True)
					
					fq_name = d.name + '.' + t.name + '.' + field_name
					p = ProtectionOption(fq_name)
					for protection in self.options.options['protection']:
						if protection.name == fq_name:
							p = protection
					if not p.exclude:
						f = DatabaseField(field_name, t, d, field_type, field_nullable, field_key, field_default, protection=p)
						t.children.append(f)
						
		references_query = '''SELECT 
								`TABLE_SCHEMA`, `TABLE_NAME`, `COLUMN_NAME`,
								`REFERENCED_TABLE_SCHEMA`, `REFERENCED_TABLE_NAME`,
								`REFERENCED_COLUMN_NAME`
						FROM
								`INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE`
						WHERE
								`REFERENCED_TABLE_NAME` IS NOT NULL;'''
		ref_rows = self.query(references_query)
		for ref_row in ref_rows:
			infq = ref_row[0] + '.' + ref_row[1] + '.' + ref_row[2]
			outfq = ref_row[3] + '.' + ref_row[4] + '.' + ref_row[5]
			
			for d in dbs:
				for t in d.children:
					for f in t.children:
						if f.fq_name == infq:
							infield = f
						if f.fq_name == outfq:
							outfield = f
			
			if infield != None and outfield != None:
				infield.relation = outfield
						
		return dbs