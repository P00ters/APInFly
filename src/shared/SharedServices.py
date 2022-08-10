# -*- coding: utf-8 -*-
"""A module containing miscellaneous shared functions.
"""

def is_type (variable, expected_type):
	"""Checks if a specified variable is of the expected type.
	
	This function checks if the variable type is of the expected type, allowing
	for an implementation of stricter type checking.
	
	Example:
		>>> variable = 'myVariable'
		...
		>>> is_type(variable, 'str')
		True
		>>> is_type(variable, 'int')
		False
	
	Args:
		variable: The variable to check against its expected type.
		expected_type (str): The expected type of the variable as a string.
	
	Returns:
		bool: True if the variable is of the expected type. False if not.
	"""
	if str(type(variable)) == "<class '" + expected_type + "'>":
		return True
	else:
		return False
		
def force_type (variable, expected_type, **kwargs):
	"""Forces the variable to be of the expected type.
	
	This function checks if the variable type is of the expected type and raises
	an Exception if not the case. 
	
	Example:
		>>> variable = 'myVariable'
		...
		>>> force_type(variable, 'str')
		...
		>>> force_type(variable, 'int', caller='my_method')
		TypeError: [force_type] Expecting variable of type '<class 'int'>', not '<class 'str'>'
		...
		>>> force_type(variable, 'list', caller='my_method', message='You did it wrong')
		TypeError: [my_method] You did it wrong
	
	Args:
		variable: The variable to force type on.
		expected_type (str): The expected type to force the variable to be of.
		caller (:obj:`str`, optional): The calling method. Used in exception messaging.
		message (:obj:`str`, optional): A custom message to display if exception occurs.
		
	Raises:
		TypeError: If the variable specified is not of the expected type specified. 
	"""
	if not is_type(variable, expected_type):
		message = '['
		if 'caller' in kwargs:
			message += kwargs.get('caller')
		else:
			message += 'force_type'
		message += '] '
		if 'message' in kwargs:
			message += kwargs.get('message')
		else:
			message += "Expecting variable of type '<class '" + expected_type + "'>', not '" + str(type(variable)) + "'"
		
		raise TypeError(message)
