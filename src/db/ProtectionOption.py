# -*- coding: utf-8 -*-
"""Module containing functionality to protect database data.

Provides functionality to exclude and control access to data 
from a database, allowing for specification of what data is 
ultimately extended into the API.
"""

from shared.SharedServices import force_type

class KeyFob:
	"""A class storing keys for controlling access.
	
	Stores keys used to unlock several functions with respect
	to performing operations on the data through the API or
	customizing functionality of the API. Any keys not provided
	on initialization are set to None.
	
	Attributes:
		ckey (str, optional): The key to allow create operations. Applicable to table level.
		rkey (str, optional): The key to allow get operaitons. Applicable to table and field level.
		ukey (str, optional): The key to allow update operations. Applicable to table and field level.
		dkey (str, optional): The key to allow delete operations. Applicable to table level.
		rnkey (str, optional): The key to allow alias renaming. Applicable to database, table and field level.
	"""
	def __init__ (self, **kwargs):
		# Validate presence and types
		self.__validate_kwargs(kwargs)
		
		self.ckey = (kwargs.get('ckey') if 'ckey' in kwargs else None)
		self.rkey = (kwargs.get('rkey') if 'rkey' in kwargs else None)
		self.ukey = (kwargs.get('ukey') if 'ukey' in kwargs else None)
		self.dkey = (kwargs.get('dkey') if 'dkey' in kwargs else None)
		self.rnkey = (kwargs.get('rnkey') if 'rnkey' in kwargs else None)
			
	def __validate_kwargs (self, kwargs):
		"""Validates kwargs passed to init for type.
		
		Ensures that all kwargs passed through on initialization are of valid type,
		in this case all of type `str`.
		
		Args:
			kwargs (:obj:`dict`): The kwargs passed in __init__.
		
		Raises:
			TypeError: If one of the kwargs passed is not of valid type.
		"""
		caller = 'KeyFob.__validate_kwargs'
		if 'ckey' in kwargs:
			force_type(kwargs.get('ckey'), 'str', caller=caller)
		if 'rkey' in kwargs:
			force_type(kwargs.get('rkey'), 'str', caller=caller)
		if 'ukey' in kwargs:
			force_type(kwargs.get('ukey'), 'str', caller=caller)
		if 'dkey' in kwargs:
			force_type(kwargs.get('dkey'), 'str', caller=caller)
		if 'rnkey' in kwargs:
			force_type(kwargs.get('rnkey'), 'str', caller=caller)
			
	def to_dict (self):
		"""Gets the KeyFob as a `dict`, for use in extending in the API.
		
		Returns:
			dict: The `dict` representation of this object.
		"""
		d = {
				'ckey': self.ckey,
				'rkey': self.rkey,
				'ukey': self.ukey,
				'dkey': self.dkey,
				'rnkey': self.rnkey
			}
		return d

class ProtectionOption:
	"""A class for storing data protection options for database models.
	
	Provides functions to control access and operations to database components 
	via the API. If not specified, the options will default to allow all access 
	to all components.
	
	Attributes:
		name (str): The name of the parent database, table or field the ProtectionOption applies to.
		exclude (bool, optional): Exclude the model from the schema entirely.
		hide (bool, optional): Hides the data behind the model, but keeps in the schema.
		protect (bool, optional): Controls access to data as specified by values in a KeyFob.
		keys (`KeyFob`, optional): The keys controlling access via specific operations.
	"""
	def __init__ (self, name, exclude=False, hide=False, protect=False, keys=KeyFob()):
		# Validate types
		caller = 'ProtectionOption.__init__'
		force_type(name, 'str', caller=caller)
		force_type(exclude, 'bool', caller=caller)
		force_type(hide, 'bool', caller=caller)
		force_type(protect, 'bool', caller=caller)
		force_type(keys, 'db.ProtectionOption.KeyFob', caller=caller)
		
		self.name = name
		self.exclude = exclude
		self.hide = hide
		self.protect = protect
		self.keys = keys
		
	def is_unprotected (self):
		"""Checks to see if this ProtectionOption specifies unprotected access.
		
		Example:
			>>> p1 = ProtectionOption()
			>>> p2 = ProtectionOption(True, False, False, KeyFob())
			...
			>>> p1.is_unprotected()
			True
			>>> p2.is_unprotected()
			False
		
		Returns:
			bool: True if the ProtectionOption is unprotected, False otherwise.
		"""
		return (self.exclude == False and self.hide == False and self.protect == False)
		
	def to_dict (self):
		"""Gets the ProtectionOption as a `dict`, for use in extending in the API.
		
		Returns:
			dict: The `dict` representation of this object.
		"""
		d = {
				'exclude': self.exclude,
				'hide': self.hide,
				'protect': self.protect,
				'keys': self.keys.to_dict()
			}
		return d

