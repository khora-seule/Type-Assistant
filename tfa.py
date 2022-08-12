import numpy as np
import functools as ft
import itertools as it
import multiprocessing as mp

########################################################################

def gen( arg ):
	"""Returns a generator-type

	This function return yield a generator type
	"""

	return type ( ( lambda : ( yield arg ) )() )

########################################################################

def arr( arg ):
	"""Returns the type of an arg-array

	This function will return a `numpy.ndarray.dtype`
	"""
	
	return type( np.array( [ arg ], dtype = arg ) )

########################################################################

def autoFormat( collection, selection, pre="", sep="", end="" ):
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
	elif( type( sep( [] ) ) == gen( type ) ):

		# We get the generator for this given collection and selection
		sep = sep( collection[ selection ] )

		# Calculate the result by reducing over the selection
		# and joining on successive yields from sep
		return ft.reduce( lambda acc, x: 
			acc + str ( x ) + next(sep), 
			collection[ selection ], 
			pre 
			) + end

	# Otherwise, we have run into an error
	else:

		raise( AssertionError )


########################################################################

def checkOperatorType( oiqType, operatorName ):
	"""Subroutine that checks if `oiq` & `operator` have compatible type

	Checks if the `operatorName` provided is defined in the `__dict__` 
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
	"""Subroutine for checking if `oiq` and `limitiation` are compatible

	Checks if the 'Object in Question', `oiq`, has a 
	compatible type, `oiqType`, with the 'Comparison Operator', 
	`comparator`, and `bounds` in `limitation`
	"""
	return np.array( [ 
				checkOperatorType( oiqType, limitation[ 0 ] ),
				checkCollectionType( oiqType, limitation[ 1 ][ 0 ] ),
				checkCollectionType( oiqType, limitation[ 1 ][ 1 ] ) 
			] )

########################################################################

def checkLeftBounds( oiq, comparator, bounds ):
	"""A subroutine for checking if `oiq` is bounded on the left

	Checks if the 'Object in Question' is bounded on the left 
	by `bounds` according to the 'Comparison Operator', `comparator`
	"""

	return np.array( [ comparator( bound, oiq ) for bound in bounds ] )

########################################################################

def checkRightBounds( oiq, comparator, bounds ):
	"""A subroutine for checking if `oiq` is bounded on the right

	Checks if the 'Object in Question' is bounded on the right by 
	`bounds` according to the 'Comparison Operator', `comparator`
	"""

	return np.array( [ comparator( oiq, bound ) for bound in bounds ] )

########################################################################

def checkBounds( oiq, comparator, bounds ):
	"""A subroutine for checking if `oiq` is bounded on the left & right

	Checks if the 'Object in Question' is bounded on the left and right 
	by `bounds` according to the 'Comparison Operator', `comparator`
	"""

	# First we translate the provided name, `comparatorName`,
	# into an actual `comparator`
	comparator = oiqType.__dict__[ comparatorName ]

	# Then we assemble the pair by calling `checkLeftBounds` 
	# and `checkRightBounds`
	return ( 
		checkLeftBounds( oiq, comparator, bounds[0] ), 
		checkRightBounds( oiq, comparator, bounds[1] ) 
		)

########################################################################

def checkEvery( collection, neg = False ):
	"""A subroutine for checking that all boolean-subarrays are all True

	Iterates over `subcollection`s of `collection` and checks if each of
	them are completely true by calling the `all` numpy method. `neg`
	can be set to `True` in order to check if `any` are `False`
	"""

	return np.array( [ 
		( neg ^ subcollection.all() ) 
		for subcollection in collection 
		] )

########################################################################

def generateLimitationErrorReport( limitations, limitationsCheck, typeCheck = True ):
	"""Formatting subroutine for assembling a user readable error report

	Takes in array of limitations and another array indicating the 
	ways in which each is either compatible / met or 
	incompatible / failed; it then generates a user readable report 
	of said data
	"""

	# If we are generating a TypeError Report...
	if( typeCheck ):

		condition = "incompatible"	

	# Otherwise -- i.e. we are generating a ValueError Report...
	else:

		condition = "not met"

	sides = [ "Left", "Right" ]

	# We get the limitations that have at least one 
	# failure / incompatability
	failures = checkEvery( limitationsCheck, neg = True )

	# Get the indices of the limitations in an array
	limIndices = np.array( range( len( limitations ) ) )

	# Iterate over the indices of only the limitations that are
	# specified by `failures`
	for limitationIndex in limIndices[ failures ]:

		# TODO: Refactor for readability and commentability
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

def checkLimitations( oiq, limitations, verbose = False ):
	"""Fault-tolerant subroutine, checks if `oiq` meets `limitations`

	First checks Type and Value to ensure that `limitations` are 
	compatible with `oiq` before then -- supposing the Type and 
	Value checks arepassed -- checking if the `limitations` are met by
	`oiq`
	"""

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

				# The ValueError we raise is generated using the
				# application of `autoFormat` to `limitation`
				# and the application of `checkEvery` on 
				# limitationsCheck in `neg` mode, with
				# a `sep` generator given by
				# `generateLimitationErrorReport`
				raise( ValueError( 
					autoFormat( 
						limitations, 
						checkEvery( limitationsCheck, neg = True ),
					pre = "The following limitation(s) are not met:\n",
					sep = generateLimitationErrorReport( 
						limitations, 
						limitationsCheck, 
						typeCheck = False 
						) 
				) ) )

		# Otherwise, we will return True because all limitations are met by the `oiq`
		else:
			return True

########################################################################

def askUserRTI(	question, answerTypeName, answerLimitations = None ):
	"""A fault-tolerant subroutine for asking for real-time input

	Takes a plain-text question and gets a Type and Value checked
	answer that also meets any additional Limitations imposed
	"""

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

class TypeFormerAssistant:
	"""Enables real-time user formation of Types via real-time input

	TODO
	"""
	def __init__( self, verbose = True ):

		self.__workers = mp.Pool()

		self.__exit = False

		if ( verbose ):

			# We greet the user and introduce the TypeFormerAssistant
			helloMessage()

			# We display the options available 
			displayMethods()

		# We begin the life-cycle loop of our TypeFormerAssistant
		while( not __exit ):

			__workers.map( __interpret, __awaitInput() )

	####################################################################

	def helloMessage( self ):
		"""Greets the user and introduces basic concepts

		This method is only called automatically if the 
		TypeFormerAssistant is started in `verbose` mode
		"""

		# TODO
		print( "Hello Message!" )

	####################################################################

	def displayMethods( self ):
		"""This method displays only the public methods

		This method is only called automatically if the 
		TypeFormerAssistant is started in `verbose` mode
		"""

		# TODO
		print( "Display Methods!")

	####################################################################

	def __awaitInput( self ):

		# TODO
		print( "Await Input!" )

	####################################################################

	def __interpret( self, input ):

		# TODO
		print( "Interpret!" )

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