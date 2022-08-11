import numpy as np
import functools as ft
import itertools as it
import multiprocessing as mp

########################################################################

def gen():
"""An abstract generator

This function will always yield a call of itself and so the type of any
number of applications of `next` on it will always be a generator
"""

	yield gen()

########################################################################


def autoFormat( collection: type( np.array( [] ) ), 
				selection: type( np.array( [ bool ] ) ), 
				pre="", sep="", end="" 
				) -> str:
"""A subroutine for constructing complex strings 

Uses a boolean-array, `selection`, as a slice on the provided array,
`collection`. A complex formatted string is then formatted, which 
begins with `pre`, ends with `end`, and has exactly the 'elements'
in our slice, each seperated by `sep`
"""

	sepType = type( sep )


	# If we have a simple string seperator
	if( sepType == type( '' ) ):

		return pre + sep.join( collection[ selection ] ) + end

	# If we have a list of seperators
	elif( sepType == type( [] ) ):

		# We get the selection from collection so we can index
		# into it in our lambda expression
		selection = collection[ selection ]

		# This reduce iterates over selection and sep
		# and joins the former using the latter
		return ft.reduce( lambda acc, x: 
			acc + str ( selection[ x ] ) + sep[ x ], 
			range( len( selection ) ), 
			pre 
			) + end

	# If we have a generator of seperators
	elif( type( sep( [] ) ) == type( gen() ) ):

		# We get the generator for this given collection and selection
		sep = sep( collection[ selection ] )

		# Calculate the result by reducing over the selection
		# and joining on successive yields from sep
		return ft.reduce( lambda acc, x: 
			acc + str ( x ) + next(sep), 
			collection[ selection ], 
			pre 
			) + end


########################################################################

def checkOperatorType( oiqType, operatorName ):
"""A subroutine that checks if `oiq` and `operator` have compatible type

Checks if the `operatorName` provided is defined the `__dict__` 
of `oiqType`, and then returns the bool
"""

	return ( operatorName in oiqType.__dict__ )

########################################################################

def checkCollectionType( oiqType, collection ):
"""A subroutine for checking if  `collection` has a matching type

Takes in a target type and returns a boolean-array indicating which,
if any, `elements` in the provided `collection` have matching type
"""

	return np.array( [ ( oiqType and type( element ) ) for element in collection ] )

########################################################################

def checkLimitationType( oiqType, limitation ):
"""A subroutine for checking if `oiq` and `limitiation` are compatible

Checks if the 'Object in Question', `oiq`, has a 
compatible type, `oiqType`, with the 'Comparison Operator', `comparator`, 
and `bounds` in `limitation`
"""
	return np.array( [ 
				checkOperatorType( oiqType, limitation[ 0 ] ),
				checkCollectionType( oiqType, limitation[ 1 ][ 0 ] ),
				checkCollectionType( oiqType, limitation[ 1 ][ 1 ] ) 
			] )

########################################################################

# Function Names: checkLeftBounds & checkRightBounds

# Each are subroutines for checking if the 'Object in Question', `oiq`, 
# is bounded on either the left or right, respectively, by the specified `bounds` 
# according to the provided 'Comparison Operator', `comparator`

# Input:
# `oiq`			:	'Object in Question'
# `comparator`	:	'Comparison Operator'
# `bounds`		:	A collection of 'Left Bounds' or 'Right Bounds', respectively

# Output:
# Each return a boolean-array of which bounds -- left and right bounds, respectively -- succesffully 
# bound the 'Object in Question', `oiq`

def checkLeftBounds( oiq, comparator, bounds ):

	return np.array( [ comparator( bound, oiq ) for bound in bounds ] )

def checkRightBounds( oiq, comparator, bounds ):

	return np.array( [ comparator( oiq, bound ) for bound in bounds ] )

########################################################################

# Function Name: checkBounds

# A subroutine for checking if the 'Object in Question', `oiq`, 
# lies within the specified `bounds` according to the provided 
# 'Comparison Operator', `comparator`

# Input:
# `oiq`			:	'Object in Question'
# `comparator`	:	'Comparison Operator'
# `bounds`		:	A pair of 'Left Bounds' and 'Right Bounds'

# Output: 
# A pair of boolean-arrays of which left and right bounds succesfully bound the `oiq`

def checkBounds( oiq, comparatorName, bounds ):

	# First we translate the provided name, `comparatorName`, of a `comparator`
	comparator = oiqType.__dict__[ comparatorName ]

	# Then we assemble the pair by calling `checkLeftBounds` and `checkRightBounds`
	return ( checkLeftBounds( oiq, comparator, bounds[0] ), checkRightBounds( oiq, comparator, bounds[1] ) )

########################################################################

# Function Name: checkEvery

# A subroutine for checking that all boolean-subarrays, `subcollection`s, of the 
# boolean-array-array, `collection`, evaluate to True under application of `*.all()`

# Input:
# `collection`	:	A boolean-array-array

# Output:
# A boolean indicating whether every subarray is 'All' True or not

def checkEvery( collection, neg = False ):

	return np.array( [ ( neg ^ subcollection.all() ) for subcollection in collection ] )

########################################################################

# Function Name: generateErrorReport

# A formatting subroutine for assembling a user readable error report via a generator

# Input:
# `limitations`				:	An array of pairs containing a 'Comparison Operator' and 'Bounds'
# `limitationsTypeCheck`	:	An array of triples containing booleans indicating type compatability

# Output:
# A formatted string that can be passed to TypeError

def generateLimitationErrorReport( limitations, limitationsXCheck, typeCheck = True ):

	# If we are generating a typeChecking Error Report...
	if( typeCheck ):

		condition = "incompatible"	

	else:

		condition = "not met"

	sides = [ "Left", "Right" ]

	for limitationIndex in np.array( range( len( limitations ) ) )[ checkEvery( limitationsXCheck, neg = True ) ]:
		yield autoFormat( 
			[ "This Comparison Operator is incompatible\n" ] + map( lambda i : 
				autoFormat( 
					np.array( range( len( limitations[ limitationIndex ][ i + 1 ] ) ) ), 
					limitations[ limitationIndex ][ i + 1 ], 
					pre = "The " + sides[ i ] + " Bounds", 
					sep = ", ", 
					end = "are " + condition + "\n"
					),
				range(2) ) 
	, limitationsCheck[ limitationIndex ], 
			pre = "The " + str(i) + "th Limitation is " + condition + " because...\n",
			sep = "\n"
			)

########################################################################

# Function Name: checkLimitations

# A fault-tolerant subroutine for checking if the 'Object in Question', `oiq`, meets the
# specified `limitations`

# Input:
# `oiq`			:	'Object in Question'
# `limitations`	:	An array of pairs containing a 'Comparison Operator' and 'Bounds'

# Output ( if not verbose ):
# A boolean indicating whether all limitations are met or not

# Output ( if verbose ):
# A 3d-array of which `limitations` have been met
# The 1st dimension is which limitation, 
# the 2nd is which side failed to be bounded,
# the 3rd is which bound failed

def checkLimitations( oiq, limitations, verbose = False ):

	# First we will type-check the oiq against the `limitations`' 'Comparison Operators',
	# `comparator`s,  and `bounds`
	try:

		# So we assign `oiqType`
		oiqType = type( oiq )

		# We assert that every element in this array be True where this array is checking if the type of
		# each limitation is compatible with the 'Object in Question', `oiq`
		limitationsTypeCheck = np.array( [ 
			np.array( [ 
				checkOperatorType( oiqType, comparatorName ),
				checkCollectionType( oiqType, leftBounds ),
				checkCollectionType( oiqType, rightBounds ) 
			] )
		for ( comparatorName, ( leftBounds, rightBounds ) ) in limitations
		] )

		assert checkEvery( limitationsTypeCheck ).all()

	# In the case that our assertion fails, we raise a TypeError 
	except AssertionError:

		raise( TypeError( autoFormat( limitations, checkEvery( limitationsTypeCheck, neg = True ), 
			pre = "The following limitation(s) do not have compatible type(s):\n", 
			sep = generateLimitationErrorReport( limitations, limitationsTypeCheck )
		) ) )

	# Otherwise, we will then go about checking if the `limitations` are met by `oiq`
	else:

		try:

			# We assert that every element in this array be True where this array is checking if
			# each limitation is met by the 'Object in Question'
			limitationsCheck = np.array( [
				checkBounds( oiq, comparatorName, bounds )
				for ( comparatorName, bounds ) in limitations
				] )

			assert checkEvery( limitationsCheck ).all()

		# In the case that our assertion fails, we either return 
		# `limitationsCheck` or we raise a ValueError
		# depending on the value of `verbose`
		except AssertionError:

			if( verbose ):
				return limitationsCheck
			else:

				raise( ValueError( autoFormat( limitations, checkEvery( limitationsCheck, neg = True ),
					pre = "The following limitation(s) are not met:\n",
					sep = generateLimitationErrorReport( limitations, limitationsCheck, typeCheck = False ) 
				) ) )

		# Otherwise, we will return True because all limitations are met by the `oiq`
		else:
			return True

########################################################################

# Function Name: askUserRTI

# A fault-tolerant subroutine for asking the user for real-time input

# Input:
# `question`			:	A string expressing the inquiry for the user
# `answerTypeName`		:	A string representing the name of the type `answer` must be coercible to
# `answerLimitations`	:	An optional array of pairs containing a 'Comparison Operator' and 'Bounds'

# Output:
# A validated answer recieved via real-time input

def askUserRTI( question, answerTypeName, answerLimitations = None ):

	answered = False

	# First we ensure that our `answerTypeName` is well-defined
	try:

		answerType = locals()[ answerTypeName ]

	# If the `answerType` is unable to be retrieved we raise the KeyError
	except KeyError as e:

		raise( e )
		
	# Otherwise we use the `answerType` as our constructor on `answer`
	else:

		while( not answered ):

			# To get `answer` we ask `question`
			answer = input( question + "\n\t->\t" )

			# We then want to see if `answerType` is able to act on `answer` without error
			try:

				answer = answerType( answer )

			# If answerType is unable to coerce strings, we raise the TypeError
			except TypeError as e:

				# We simply raise the answer -- instead of alerting the user -- this is
				# because answerType -- although defined -- is not a valid choice
				# as it is unable to coerce text input from the user
				raise( e )

			# If answerType is unable to coerce the specific string given, we request
			# a new answer from the user
			except ValueError as e:

				# First, we tell the user about the error and that we are going to describe it
				print( """ 
						Sorry! Your answer isn't valid. The `ValueError` is printed below,
						and it means that your answer doesn't fall within the range of strings that 
						the answer type for this question is able to understand. Once you
						understand how to correct your answer, please try again.
					""" )

				# Then, we pass along the `ValueError` text itself
				print( "Value Error: " + str( e ) )

			# If `answerType` is able to coerce the given string, then we check if
			# `answer` is able to pass all requirements in `answerLimitations` 
			else:
				
				limitationsCheck = checkLimitations( answer, answerLimitations, verbose = True )

				if( checkEvery( np.array( [ checkEvery( subcollection ) for subcollection in limitationsCheck ] )  ) ):
					print( "Answer Accepted!" )
					answered = True
	finally:
		return answer

########################################################################

# Class Name: TypeFormerAssistant

# This class enables real-time user formation of Types via asking the user for real-time input.

# Parameters:
# None

class TypeFormerAssistant:

	def __init__( verbose = True ):

		self.__workers = mp.Pool()

		self.__exit = False

		if ( verbose ):

			# We greet the user and introduce the TypeFormerAssistant
			helloMessage()

			# We display the options available 
			displayMethods()

		# We begin the life-cycle loop of our TypeFormerAssistant
		while( not __exit ):

			__workers.map( self.interpret, awaitInput() )


	####################################################################

	def helloMessage():
	"""Greets the user and introduces basic concepts

	This method is only called if the TypeFormerAssistant is started 
	in `verbose` mode
	"""

		# TODO
		print( "Hello Message!" )

	####################################################################

	def displayMethods():
	"""This method displays only the public methods

	This method is only called if the TypeFormerAssistant is started 
	in `verbose` mode
	"""

		# TODO
		print( "Display Methods!")

########################################################################

def main():
"""This is the main for TypeFormerAssistant


Side-effects are dependent on 'Real-Time-Input' from the User:
Results can be printed to terminal during runtime, or
Results can be written to files as serialized objects ( JSON ), or
Results can be written to files as binaries to be reloaded 
later ( pickling )
"""

	# TODO
	print( "Main!" )

if __name__ == '__main__':
	main()