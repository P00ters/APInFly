"""Module containing classes for falcon api routes.
"""

import falcon
import falcon.asgi
import threading
from shared.SharedServices import force_type


def qstr_to_args (query_str):
	"""Parses a query string to an args dict.
	
	Args:
		query_str (str): The url query string to parse.
	
	Returns:
		dict: A dict containing the arg values by key.
	"""
	bare = query_str.split('&')
	pairs = []
	for b in bare:
		pair = b.split('=')
		pairs.append(pair)
	args = {}
	for p in pairs:
		args[p[0]] = p[1]
	return args
	
def num_to_status (retno):
	"""Converts return numbers from APIController to falcon 
	compatible responses.
	
	Args:
		retno (int): The return number from the APIController.
		
	Returns:
		str: The equivalent falcon response type.
	"""
	if retno == 200:
		return falcon.HTTP_200
	elif retno == 400:
		return falcon.HTTP_400
	elif retno == 404:
		return falcon.HTTP_404
	else:
		return falcon.HTTP_500


class GetManyResource:
	def __init__ (self, apic):
		"""Class to handle the route to retrieve many instances of a model.
		
		Attributes:
			apic (api.APIController): The APIController to extend the database into falcon.
			
		Raises:
			TypeError: If a non APIController is passed as the apic. 
		"""
		caller = 'GetManyResource.__init__'
		force_type(apic, 'api.APIController.APIController', caller=caller)
		
		self.apic = apic
		
	async def on_get(self, req, resp, model):
		if req.query_string != '':
			args = qstr_to_args(req.query_string)
		else:
			args = {}
		
		result = self.apic.context_query_multiple(model, args)
		data = result[0]
		retno = result[1]
		
		resp.status = num_to_status(retno)
		resp.text = str(data)