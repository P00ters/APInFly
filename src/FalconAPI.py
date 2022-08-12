"""Module containing logic to run API via Falcon and uvicorn.

"""
import falcon
import falcon.asgi
import threading
from shared.SharedServices import force_type
from falc.FalconResources import GetManyResource, RESTResource


class FalconAPI: 
	def __init__ (self, apic):
		"""Class to run api via falcon.
		
		Attributes:
			apic (api.APIController): The api controller to extend.
			
		Raises:
			TypeError: If a non APIController is passed as the apic. 
		"""
		caller = 'FalconAPI.__init__'
		force_type(apic, 'api.APIController.APIController', caller=caller)
		
		self.apic = apic
		self.gm = GetManyResource(self.apic)
		self.r = RESTResource(self.apic)
	
	def run_app(self):
		self.app = falcon.asgi.App()
		self.app.add_route('/api/{model}', self.gm)
		self.app.add_route('/api/{model}/{id}', self.r)
		return self.app
		