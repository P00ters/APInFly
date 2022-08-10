# -*- coding: utf-8 -*-
"""Module containing logic to specify options for a database connection.

Attributes:
	ALL_PROVIDERS (:obj:`list` of :obj:`str`): All valid database providers.
	REQUIRED_FOR (:obj:`dict` of :obj:`str`: :obj:`list` or :obj:`str`): All required parameters per provider.
	OPTIONAL_FOR (:obj:`dict` of :obj:`str`: :obj:`list` or :obj:`str`): All optional parameters per provider.
	DESC_REQUIRED (:obj:`dict` of :obj:`str`: :obj:`list` or :obj:`str`): Descriptions for required parameters.
	DESC_OPTIONAL (:obj:`dict` of :obj:`str`: :obj:`list` or :obj:`str`): Descriptions for optional parameters.
"""

from shared.SharedServices import force_type
from db.ProtectionOption import ProtectionOption

ALL_PROVIDERS = ['mysql']
REQUIRED_FOR = 	{
					'mysql': [ 'host', 'username', 'password' ]
				}
OPTIONAL_FOR = 	{
					'mysql': [ 'port', 'protection' ]
				}
DESC_REQUIRED = {
					'mysql': 	[
									'The hostname for the mysql server',
									'The username to login to the mysql server with',
									'The password to login to the mysql server with'
								]
				}
DESC_OPTIONAL = {
					'mysql':	[
									'The port for the mysql server - defaults to 3306',
									'Any ProtectionOption to apply to databases, tables or fields'
								]
				}
				
				
class DatabaseConnectionOption:
	"""A class representing options to connect to a database.
	
	Used to model and store the necessary data to provide to database providers 
	to establish connection.
	
	Attributes:
		provider (str): The database provider for the connection.
		
	Raises:
		TypeError: If any of the attributes are of unexpected types.
		ValueError: If the provider is not a valid provider or a required attribute is missing.
		NameError: If a passed attribute is not valid for the provider.
	"""
	def __init__ (self, provider, **kwargs):
		# Validate types
		caller = 'DatabaseConnectionOption.__init__'
		force_type(provider, 'str', caller=caller)
		if provider not in ALL_PROVIDERS:
			raise ValueError('[' + caller + '] Provider \'' + provider + '\' not valid')
		for required in REQUIRED_FOR[provider]:
			if required not in kwargs:
				raise ValueError('[' + caller + '] Missing required parameter \'' + required + '\'')
		for kwarg in kwargs:
			if kwarg not in REQUIRED_FOR[provider] and kwarg not in OPTIONAL_FOR[provider]:
				msg = '[' + caller + '] Parameter \'' + kwargs + '\' not valid for provider \'' + provider + '\''
				raise NameError(msg)
		
		self.provider = provider
		self.options = kwargs
		for optional in OPTIONAL_FOR[provider]:
			if optional not in self.options:
				self.options[optional] = None
				
		if self.options['protection'] != None:
			for protection in self.options['protection']:
				force_type(protection, 'db.ProtectionOption.ProtectionOption', caller=caller)
		else:
			self.options['protection'] = []
		
		
	def to_dict (self):
		"""Method to render the DatabaseConnectionOption as a `dict`.
		
		Returns:
			dict: The `dict` representation of this object. 
		"""
		if self.options['protection'] != None:
			opt = self.options
			prot = []
			for protection in self.options['protection']:
				prot.append(protection.to_dict())
			opt['protection'] = prot
		else:
			opt = self.options
			
		d =	{
				'provider': self.provider,
				'options': self.options
			}
		return d
		
		