

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