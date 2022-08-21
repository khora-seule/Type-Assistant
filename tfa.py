import numpy as np
import functools as ft
import itertools as it
import multiprocessing as mp
from abc import ABC, abstractmethod

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

def reIndex( index, reiterable ):
	"""Indexes into reiterable with the result of indexing with index


	"""
	
	return reiterable[ reiterable[ index ] ]

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

	# If we have a list or tuple of seperators
	elif( sepType in ( type( [] ), type( () ) ) ):

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

def checkLimitType( oiqType, limit ):
	"""Subroutine for checking if `oiq` and `limitiation` are compatible

	Checks if the 'Object in Question', `oiq`, has a 
	compatible type, `oiqType`, with the 'Comparison Operator', 
	`comparator`, and `bounds` in `limit`
	"""
	return np.array( [ 
				checkOperatorType( oiqType, limit[ 0 ] ),
				checkCollectionType( oiqType, limit[ 1 ][ 0 ] ),
				checkCollectionType( oiqType, limit[ 1 ][ 1 ] ) 
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

def generateLimitErrorReport( limits, limitsCheck, typeCheck = True ):
	"""Formatting subroutine for assembling a user readable error report

	Takes in array of limits and another array indicating the 
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

	sides = ( "Left", "Right" )

	# We get the limits that have at least one 
	# failure / incompatability
	failures = checkEvery( limitsCheck, neg = True )

	# Get the indices of the limits in an array
	limIndices = np.array( range( len( limits ) ) )

	# Iterate over the indices of only the limits that are
	# specified by `failures`
	for limitIndex in limIndices[ failures ]:

		# TODO: Refactor for readability and commentability
		yield autoFormat( 
			[ "This Comparison Operator is incompatible\n" ] + map( lambda i : 
				autoFormat( 
					np.array( range( len( limits[ limitIndex ][ i + 1 ] ) ) ), 
					limits[ limitIndex ][ i + 1 ], 
					pre = "The " + sides[ i ] + " Bounds", 
					sep = ", ", 
					end = "are " + condition + "\n"
					),
				range(2) ) 
	, limitsCheck[ limitIndex ], 
			pre = "The " + str(i) + "th Limit is " + condition + " because...\n",
			sep = "\n"
			)

########################################################################

def checkLimits( oiq, limits, verbose = False ):
	"""Fault-tolerant subroutine, checks if `oiq` meets `limits`

	First checks Type and Value to ensure that `limits` are 
	compatible with `oiq` before then -- supposing the Type and 
	Value checks arepassed -- checking if the `limits` are met by
	`oiq`
	"""

	# First we will type-check the oiq against the `limits`' 'Comparison Operators',
	# `comparator`s,  and `bounds`
	try:

		# So we assign `oiqType`
		oiqType = type( oiq )

		# We assert that every element in this array be True where this array is checking if the type of
		# each limit is compatible with the 'Object in Question', `oiq`
		limitsTypeCheck = np.array( [ 
			np.array( [ 
				checkOperatorType( oiqType, comparatorName ),
				checkCollectionType( oiqType, leftBounds ),
				checkCollectionType( oiqType, rightBounds ) 
			] )
		for ( comparatorName, ( leftBounds, rightBounds ) ) in limits
		] )

		assert checkEvery( limitsTypeCheck ).all()

	# In the case that our assertion fails, we raise a TypeError 
	except AssertionError:

		raise( TypeError( autoFormat( limits, checkEvery( limitsTypeCheck, neg = True ), 
			pre = "The following limit(s) do not have compatible type(s):\n", 
			sep = generateLimitErrorReport( limits, limitsTypeCheck )
		) ) )

	# Otherwise, we will then go about checking if the `limits` are met by `oiq`
	else:

		try:

			# We assert that every element in this array be True where this array is checking if
			# each limit is met by the 'Object in Question'
			limitsCheck = np.array( [
				checkBounds( oiq, comparatorName, bounds )
				for ( comparatorName, bounds ) in limits
				] )

			assert checkEvery( limitsCheck ).all()

		# In the case that our assertion fails, we either return 
		# `limitsCheck` or we raise a ValueError
		# depending on the value of `verbose`
		except AssertionError:

			if( verbose ):
				return limitsCheck
			else:

				# The ValueError we raise is generated using the
				# application of `autoFormat` to `limit`
				# and the application of `checkEvery` on 
				# limitsCheck in `neg` mode, with
				# a `sep` generator given by
				# `generateLimitErrorReport`
				raise( ValueError( 
					autoFormat( 
						limits, 
						checkEvery( limitsCheck, neg = True ),
					pre = "The following limit(s) are not met:\n",
					sep = generateLimitErrorReport( 
						limits, 
						limitsCheck, 
						typeCheck = False 
						) 
				) ) )

		# Otherwise, we will return True because all limits are met by the `oiq`
		else:
			return True

########################################################################

def askUserRTI(	question, answerTypeName, answerLimits = None ):
	"""A fault-tolerant subroutine for asking for real-time input

	Takes a plain-text question and gets a Type and Value checked
	answer that also meets any additional Limits imposed
	"""

	answered = False

	# First we ensure that our `answerTypeName` is well-defined
	try:

		answerType = globals()[ answerTypeName ]

	# If the `answerType` is unable to be retrieved we first check if
	# the type exists in `builtins` before raising the error
	except KeyError as e:

		try:
			answerType = globals()[ "__builtins__" ].__dict__[ answerTypeName ]
		except:
			raise( e )
		
	# Finally we use the `answerType` as our constructor on `answer`
	finally:

		while( not answered ):

			# To get `answer` we ask `question`
			answer = input( "|| " + question + "\n\\\\>>>\t" )

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

				
				errorMessage =	( 
								"||\n" + "VV\n||\n" +
								"|]===[ Sorry! Your answer isn't valid!\n||\n \\\\\n"+
								"  |]===[ The `ValueError` is printed below, and it means that your \n" +
							   	"  |]===[ answer doesn't fall within the range of strings that\n" +
							   	"  |]===[ the answer type for this question is able to understand.\n" +
							   	"  ||\n" + "  VV\n" +
							   	"  ||"
							   	"  |]===[ Once you understand how to correct your answer, please try again.\n\n" 
							   	)

				# First, we tell the user about the error and that we are going to describe it
				print( errorMessage )

				# Then, we pass along the `ValueError` text itself
				print( "Value Error: " + str( e ) )

			# If `answerType` is able to coerce the given string, then we check if
			# `answer` is able to pass all requirements in `answerLimits` 
			else:
				
				if( answerLimits ):

					limitsCheck = checkLimits( answer, answerLimits, verbose = True )

					if( checkEvery( np.array( [ checkEvery( subcollection ).all() for subcollection in limitsCheck ] )  ).all() ):
						answered = True
					else:
						print( "Limits Failed!" )
				else:
					answered = True

			
		return answer

########################################################################

class TypeWorker( ABC ):
	"""Abstract-Base-Class for Type-related Workers

	Worker classes that derive from this class include:
	TypeFormer, TypeConstructor, TypeDestructor, and TypeChecker
	"""

	def __init__( self, info, args ):
		"""Initialization for TypeWorker derived classes

		Creates `__worker` using `info` before calling the `work` method
		"""
		
		( poolInfo, workerInfo ) = info

		self.__initPool( poolInfo )

		self.__initWorker( workerInfo )

		self.work( args )

	####################################################################

	@abstractmethod
	def __initPool( self, info ):
		"""Abstract method for generating __pool

		Any derived TypeWorker must define this method and return a
		a process Pool
		"""

		pass

	####################################################################

	@abstractmethod
	def __initWorker( self, info ):
		"""Abstract method for generating __worker

		Any derived TypeWorker must define this method and return a
		a function that can take in the desired `args`
		"""

		pass

	####################################################################

	def work( self, args ):
		"""Public method for __worker

		Assigns the result of applying `__worker` to `args` to 
		`__myType`
		"""

		self.__myType = self.__worker( args )

	####################################################################

	def myType( self ):
		"""Public accessor for __myType

		Simply returns the private data-memeber `__myType`
		"""

		return self.__myType

########################################################################

class TypeStructor( TypeWorker ):
	"""TypeWorker derived class for both 'Type*structor's

	"""

	def __initPool( self, poolInfo ):

		pass

	def __initWorker( self, blueprint ):

		( self.__typeMap, self.__constructorList, self.__destructorList ) = blueprint

		labels = np.array( [ t[ 0 ] for t in np.hstack( ( self.__constructorList, self.__destructorList ) )

		( numOfC, numOfD ) = it.map( lambda iterable : range( len ( iterable ) ), ( self.__constructorList, self.__destructorList ) )

		( self.constructor, self.destructor ) = it.map( ( lambda number, iterable : dict( zip( range( number ), iterable ) ) ), ( ( numOfC, self.__constructorList ), ( numOfD, self.__destructorList ) ) )

		for t in self.constructor:

			self.constructor[ self.constructor[ t ] ] = ( lambda args : self.__destructorList[ t ][ 1 ].constructor( self.__typeMap( self.__constructorList[ t ][ 1 ].constructor, self.__constructorList[ t ][ 1 ].destructor, args ) ) )

		for t in self.destructor:

			self.destructor[ self.destructor[ t ] ] = ( lambda args : self.__destructorList[ t ][ 1 ]( args ) )

		self.__worker = self.constructor

    ####################################################################

########################################################################

class TypeFormer( TypeWorker ):
	"""TypeWorker derived class which holds Type formation info

	A worker responsible for turning representations of types into the
	type that is being represented
	"""

	def __initWorker( self, formation ):
		"""Derived method for creating __worker

		`formation` must be a triple containing a 'Structure'
		function, `typeMap`, a 'Constructor TypeList' `constructorTypes`, 
		and a 'Destructor TypeList' `destructorTypes`
		"""
		
		structor = ( lambda constructorArgs : TypeStructor( formation, constructorArgs ) )

		return ( lambda name : np.array( ( name, structor ) ) )
			

########################################################################

class TypeChecker:
	"""Enables automatic TypeChecking and Error Reports

	TODO
	"""

	def __initWorker( self, workers ):
		"""

		"""


########################################################################

class TypeAssistant:
	"""Enables user management of Types via user real-time input

	TODO
	"""

	def __init__( self, verbose = True ):

		self.__workers = mp.Pool()

		self.__types = {}

		self.__exit = False

		if ( verbose ):

			# We greet the user and introduce the TypeAssistant
			helloMessage()

			# We display the options available 
			displayMethods()

		# We begin the life-cycle loop of our TypeAssistant
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

	####################################################################

	def create( self, manual = None ):

		# TODO
		print( "Create a Type!" )

	####################################################################

	def edit( self, manual = None ):

		# TODO
		print( "Edit a Type!" )

	####################################################################

	def delete( self, manual = None ):

		# TODO
		print( "Delete a Type!" )

	####################################################################

	def export( self, manual = None ):

		# TODO
		print( "Export a Type!" )

########################################################################

def main():
	"""This is the main for TypeAssistant


	Side-effects are dependent on 'Real-Time-Input' from the User:
	Results can be printed to terminal during runtime, or
	Results can be written to files as serialized objects ( JSON ), or
	Results can be written to files as binaries to be reloaded 
	later ( pickling )
	"""

	# TODO
	print( "Main!" )
	answer = askUserRTI( "How many?", 'int' )
	print( "The Answer you gave was:", answer )
	print( "The Type of Answer was:", type( answer ) )
 
if __name__ == '__main__':
	main()