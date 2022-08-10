# -*- coding: utf-8 -*-
"""Module defining naming class for use in database object models.

This module defines a naming class that can be used for modeling naming 
of database object models with functionality to rename and use aliases.
"""

from shared.SharedServices import force_type

def are_these (name1, name2):
	"""Checks if two alias names have overlap.
	
	Args:
		name1 (db.AliasName.AliasName): The first alias name.
		name2 (db.AliasName.AliasName): The second alias name.
		
	Returns:
		bool: True if there is any overlap, either in name or alias, False if not.
	
	Raises:
		TypeError: If either of the args are not AliasName's.
	"""
	caller = 'are_these'
	force_type(name1, 'db.AliasName.AliasName', caller=caller)
	force_type(name2, 'db.AliasName.AliasName', caller=caller)
	
	overlap = False
	if name1.name == name2.name:
		overlap = True
	for a1 in name1.aliases:
		if a1 == name2.name:
			overlap = True
	for a2 in name2.aliases:
		if a2 == name1.name:
			overlap = True
	for a1 in name1.aliases:
		for a2 in name2.aliases:
			if a1 == a2:
				overlap = True
				
	return overlap
	

class AliasName:
	"""A naming class for use in database object models.
	
	This class allows for database object models, like fields, tables and 
	databases to have multiple names.
	
	Attributes:
		__name (str): The actual name of the object.
		__aliases (:obj:`list` of :obj:`str`, optional): A list of viable alias names for the object.
	"""
	
	def __init__ (self, name, aliases=[]):
		# Validate attribute types
		caller = 'AliasName.__init__'
		force_type(name, 'str', caller=caller)
		force_type(aliases, 'list', caller=caller)
		for alias in aliases:
			force_type(alias, 'str', caller=caller)
		
		# Assign attributes
		self.name = name
		self.aliases = aliases
		
	def is_this (self, name):
		"""Checks if this name matches the provided name.
			
		Determine if this name instances matches the specified name, whether it
		be directly through its name or one of its aliases.
		
		Example:
			>>> alias = AliasName('Thomas', ['Tom', 'Tommy'])
			>>> alias.is_this('Thomas')
			True
			>>> alias.is_this('Tommy')
			True
			>>> alias.is_this('Rob')
			False
		
		Args:
			name (str): The name to see if this AliasName matches to.
			
		Returns:
			bool: True if the specified name is this AliasName, False otherwise.
		"""
		# Validate attribute types
		caller = 'AliasName.is_this'
		force_type(name, 'str', caller=caller)
		
		# Check is specified name matches
		matches = False
		if name == self.name:
			matches = True
		for a in self.aliases:
			if name == a:
				matches = True
		
		return matches
		
	def add_alias (self, alias):
		"""Adds a new alias to the AliasName.
		
		Example:
			>>> alias = AliasName('John', ['Johhny'])
			>>> alias.is_this('J')
			False
			>>> alias.add_alias('J')
			>>> alias.is_this('J')
			True
			
		Args:
			alias (str): The new alias to add.
			
		Raises:
			TypeError: If the aliases arg is not a str.
		"""
		# Validate attribute types
		caller = 'AliasName.add_alias'
		force_type(name, 'str', caller=caller)
		
		# Add the alias
		self.aliases.append(alias)
		
	def add_aliases (self, aliases):
		"""Adds multiple new aliases to the AliasName.
		
		Example:
			>>> alias = AliasName('John', ['Johhny'])
			>>> alias.is_this('J')
			False
			>>> alias.is_this('Jon')
			False
			>>> alias.add_aliases(['J', 'Jon'])
			>>> alias.is_this('J')
			True
			>>> alias.is_this('Jon')
			True
			
		Args:
			aliases (:obj:`list` of :obj:`str`): The new alias to add.
			
		Raises:
			TypeError: If the aliases arg is not a list of str.
		"""
		# Validate attribute types
		caller = 'AliasName.add_aliases'
		force_type(aliases, 'list', caller=caller)
		for a in aliases:
			force_type(a, 'str', caller=caller)
		
		# Add aliases
		for a in aliases:
			self.aliases.append(a)
			
	def remove_alias (self, alias):
		"""Removes the specified alias from the AliasName.
		
		Example:
			>>> alias = AliasName('Johnathan', ['John', 'Johnny'])
			>>> alias.is_this('Johnny')
			True
			>>> alias.remove_alias('Johnny')
			>>> alias.is_this('Johnny')
			False
		
		Args:
			alias (str): The alias to remove.
			
		Raises:
			TypeError: If the aliases arg is not a str.
			ValueError: If the alias provided is not a valid alias of the AliasName.
		"""
		# Validate attribute types
		caller = 'AliasName.remove_alias'
		force_type(name, 'str', caller=caller)
		
		# Check if alias is present
		if not alias in self.aliases:
			raise ValueError('[' + caller + "] The supplied alias '" + alias + "' is not a valid member")
		
		self.aliases.pop(alias)

