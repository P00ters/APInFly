"""Module for handling sql query translation into JSON api responses.

Attributes:
	NONSP_PARAMS (list of str): Shared parameters allowed that aren't specific to context.
	NONSP_TYPES (list of str): The types for each of the common params.
"""

NONSP_PARAMS = ['order_by', 'order_dir', 'page', 'q']
NONSP_TYPES = ['str', 'str', 'int', 'str']

from shared.SharedServices import force_type, is_type

class APIController:
	"""Class for handling sql query translation to api responses.
	
	Parses query parameters and generates valid sql for any model.
	Executes generated sql against the database and formats the 
	response into JSON compatible formatting.
	
	Attributes:
		dbc (DatabaseConnection): Valid connection to the database for querying.
		contexts (list of APIContext): The contexts to include in the api.
		page_lim (int): Max amount of results to return at once. If 0, returns all.
	"""
	def __init__ (self, dbc, contexts, page_lim):
		caller = 'APIController.__init__'
		force_type(dbc, 'db.DatabaseConnection.DatabaseConnection', caller=caller)
		force_type(contexts, 'list', caller=caller)
		for c in contexts:
			force_type(c, 'api.APIContext.APIContext', caller=caller)
		force_type(page_lim, 'int', caller=caller)
		
		self.dbc = dbc
		self.contexts = contexts
		self.page_lim = page_lim
		
	
	def context_query_multiple (self, context_name, args):
		"""Queries for multiple instances of a context using params.
		
		Args:
			context_name (str): The api name ('database_table') of the context.
			args (dict): The parameters from the request. 
			
		Returns:
			dict, int: The error message if a bad query or JSON resultant if good. An
						http response error code based on query execution.
		
		Raises:
			TypeError: If the arg types are unexpected.
		"""
		caller = 'APIController.context_query_multiple'
		force_type(context_name, 'str', caller=caller)
		force_type(args, 'dict', caller=caller)
		
		context = None
		for c in self.contexts:
			if c.name == context_name:
				context = c
		
		if context == None:
			return "Bad model/context requested: '" + context_name + "'", 400
		
		if len(context.tables) < 1:
			return "Bad model/context processing: '" + context_name + "'", 500
			
		if 'page' in args and self.page_lim == 0:
			return 'Bad \'page\' parameter, api not using paging', 400
			
		fields = context.flat_fields()
		valid_params = []
		param_types = []
		for f in fields:
			valid_params.append(f.api_name.name)
			if 'char' in f.typ || 'text' in f.typ:
				param_types.append('str')
			elif 'tinyint' in f.typ:
				param_types.append('bool')
			elif 'int' in f.typ:
				param_types.append('int')
			elif 'float' in f.typ or 'real' in f.typ:
				param_types.append('float')
			else:
				param_types.append('any')
		
		sql_query = context.get_sql_parts()
		if len(context.joins) != 0:
			sql_query += ' \n\tAND '
			
		if 'q' in args:
			for key in args:
				if key not in NONSP_PARAMS:
					return 'Bad parameters for \'q\'', 400

			keys = list(args.keys())
			vals = list(args.values())
			
			q = args['q']
			
			for f in fields:
				typ = param_types[fields.index(f)]
				if type == 'str':
					sql_query += f.sql_name + ' LIKE "%s" AND ' % q
				else:
					sql_query += f.sql_name + ' LIKE %s AND ' % q
					
			if 'order_by' in args or 'order_dir' in args:
				if 'order_by' in args and 'order_dir' in args:
					this_f = None
					for f in fields:
						if f.api_name.name == args['order_by']:
						this_f = f
					if this_f == None:
						return "Bad parameter: 'order_by' not a valid field", 400
					if args['order_dir'].upper() not in ['ASC', 'DESC']:
						return "Bad parameter: 'order_dir' not a valid value", 400
						
					sql_query += '\nORDER BY ' + this_f.sql_name + ' ' + args['order_dir'].upper()
					
				else:
					return "Bad parameters: 'order_by' and 'order_dir' must both be present", 400
			
			if 'page' in args:
				max = args['page'] * self.page_lim
				sql_query += '\nLIMIT ' + args['page'] + ';'
			else:
				sql_query += ';'
					
			
		
	def context_query_single (self, context_name, id):
		"""Queries a single instance of a context by id. 
		
		Args:
			context_name (str): The api name ('database_table') of the context.
			id (any): The primary id of the single instance to select.
			
		Returns:
			dict, int: The error message if a bad query or JSON resultant if good. An
						http response error code based on query execution.
		
		Raises:
			TypeError: If the arg types are unexpected.
		"""
		caller = 'APIController.context_query_single'
		force_type(context_name, 'str', caller=caller)
		
		context = None
		for c in self.contexts:
			if c.name == context_name:
				context = c
		
		if context == None:
			return "Bad model/context requested: '" + context_name + "'", 400
		
		if len(context.tables) < 1:
			return "Bad model/context processing: '" + context_name + "'", 500
		
		key_field = None
		for key in context.model:
			field = context.model[key]
			if not is_type(field, 'dict'):
				if field.key == 'PRI':
					key_field = field
				
		if key_field == None:
			return "No primary key field found for '" + context_name + "'", 500
			
		sql_query = context.get_sql_parts()
		if len(context.joins) != 0:
			sql_query += ' \n\tAND '
		if 'varchar' in key_field.typ:
			sql_query += key_field.sql_name + '="%s";' % id
		else:
			sql_query += key_field.sql_name + '=%s;' % id
		print(sql_query)
		
		result = self.dbc.query(sql_query)

		if len(result) == 0:
			return '', 404
		elif len(result) == 1:
			json_data = context.unpack_single(result[0])
			return json_data, 200
		else:
			return 'Found more than expected contexts', 500