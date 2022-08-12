"""Module containing classes for falcon api routes.
"""

import falcon
import falcon.asgi
import json
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
	elif retno == 201:
		return falcon.HTTP_201
	elif retno == 204:
		return falcon.HTTP_204
	elif retno == 400:
		return falcon.HTTP_400
	elif retno == 404:
		return falcon.HTTP_404
	else:
		return falcon.HTTP_500
		
def max_body(limit):
	async def hook(req, resp, resource, params):
		length = req.content_length
		if length is not None and length > limit:
			msg = (
				'The size of the request is too large. The body must not '
				'exceed ' + str(limit) + ' bytes in length.'
			)

			raise falcon.HTTPPayloadTooLarge(
				title='Request body is too large', description=msg
			)

	return hook		


class RESTResource:
	def __init__ (self, apic):
		"""Class to handle REST requests for models by id.
		
		Attributes:
			apic (api.APIController): The APIController to extend the database into falcon.
			
		Raises:
			TypeError: If a non APIController is passed as the apic. 
		"""
		caller = 'RESTResource.__init__'
		force_type(apic, 'api.APIController.APIController', caller=caller)
		
		self.apic = apic
		
	async def on_get(self, req, resp, model, id):
		"""Method to handle REST get requests to get a single instance of a model.
		
		Args:
			req (falcon.asgi.request.Request): The falcon request. 
			resp (falcon.asgi.response.Response): The falcon response.
			model (str): The name of the model being queried.
			id (str): The id of the model instance. 
		"""
		if req.query_string != '':
			resp.status = falcon.HTTP_400
			resp.text = 'Bad parameters'
		else:
			result = self.apic.context_query_single(model, id)
			data = result[0]
			retno = result[1]
			
			resp.status = num_to_status(retno)
			resp.text = str(data)
			
	async def on_delete (self, req, resp, model, id):
		if req.query_string != '':
			resp.status = falcon.HTTP_400
			resp.text = 'Bad parameters'
		else:
			result = self.apic.context_del_single(model, id)
			data = result[0]
			retno = result[1]
			
			resp.status = num_to_status(retno)
			resp.text = str(data)
				

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
	
	@falcon.before(max_body(64 * 1024))
	async def on_post(self, req, resp, model):
		body = await req.stream.read()
		body = body.decode('utf-8')
		body_dict = json.loads(body)
		print(body_dict)
		
			
		result = self.apic.context_post_single(model, body_dict)
		data = result[0]
		retno = result[1]
			
		resp.status = num_to_status(retno)
		resp.text = str(data)
		
	async def on_get(self, req, resp, model):
		"""Method to handle get requests for multi-result requests.
		
		Attributes:
			req (falcon.asgi.request.Request): The falcon request. 
			resp (falcon.asgi.response.Response): The falcon response.
			model (str): The name of the model being queried.
		"""
		if req.query_string != '':
			args = qstr_to_args(req.query_string)
		else:
			args = {}
		
		result = self.apic.context_query_multiple(model, args)
		data = result[0]
		retno = result[1]
		
		resp.status = num_to_status(retno)
		resp.text = str(data)