import itertools as it

import multiprocessing as mp
from abc import ABC, abstractmethod
import numpy as np

#######################################################################

def infGen():

	return ( _ for _ in it.cycle( ( None ) ) )
#######################################################################

def applyString( func, args ):

	return "{f}({x})".format( f = func, x = ",".join( args ) )

#######################################################################

#def formatify( labels, values ):

#	apply( ",".join( [ "{" + label + "}" for label in labels ] ) )

#######################################################################


#def extract( info ):

#	return  ( info[ 0 ], info[ 1 : ] ) if ( info != None ) else ( None, None )

#######################################################################

def swapStringGen( a, b ):

	swapTup, indexCycle = ( str( a ), str( b ) ), it.cycle( range( 2 ) )

	swapper = ( swapTup[ i ] for i in indexCycle )

	return ( "{x}, {y} = {y}, {x}".format( x = next(swapper), y = next(swapper) ) )

#######################################################################

def typeProperty( name ):

	base = "\n".join( ( "{decorator}", "def {name}( {args} ):", "{body}" ) )

	stringTups = zip( (
		( "@property", "@{name}.setter", "@{name}.deleter" ),
		( "self", "self, new{Name}", "self" ),
		(
		"""
		return self._{name}
		""", 
		"""	
		if ( self.__{name}Init ):

			self.__old{Name}, self._{name} = self._{name}, new{Name}

			self.__{name}Init = True if ( ( self.__old{Name} != None ) or ( self._{name} != None ) ) else False

		elif ( self.{name} != new{Name} ):

			self._{name} = new{Name}

			self.__{name}Init = True
		""", 
		"""
		del self._{name}

		del self.__old{Name}

		self.__{name}Init = False
		""",
		) ) )


	swapdateBody = """
		swapdater = swapStringGen( ( self.form, self.data, self.process ), ( self.__oldForm, self.__oldData, self.__oldProcess ) ) 
		
		while( True ):

			yield exec( next( swapdater ) )
		"""

	swapdateString = base.format( decorator = decorator, name = "swapdate", args = "self" body = swapdateBody )

	return [  base.format( decorator = decorator, name = name, Name = name.capitalize(), args =  args, body = body ) for ( decorator, args, body ) in stringTups ]

#######################################################################

class TypeMethod( ABC ):

	def __init__( self, info = None ):

		self.__properties = []

		( self.__dataInit, self.__processInit ) = ( False, False )

		[ exec( typeProperty( name ) ) for name in ( "data", "process" ) ]

		self.update( info )

	####################################################################

	@staticmethod
	@abstractmethod
	def init( form, data ):
		"""Abstract static method for generating process from info

		Any derived MethodClass must define this method and return a
		a process of the appropriate type ( according to info )
		"""

		pass

	####################################################################

	def update( self, newInfo ):
		"""Public method for updating process

		Uses newInfo to update form, data, and -- using 
		those -- process
		"""

		( newForm, newData ) = extract( newInfo )

		( currMatch, oldMatch ) = [ ( match == ( newForm, newData ) ) for match in ( ( self.form, self.data ), ( self.__oldForm, self.__oldData ) ) ]

		if( not ( currMatch or oldMatch ) ):

			( self.form, self.data ) = ( newForm, newData )

			self.process = init( self.form, self.data )

			self.__initialized = True

		elif( oldMatch ): 

			self.swapdate()


########################################################################

class TypeWorker( ABC ):
	"""Abstract-Base-Class for Type-related Workers

	Worker classes that derive from this class include:
	TypeChecker, TypeFormer, TypeStructor, and TypeComputer
	"""

	class WorkerPool( TypeMethod ):

		@staticmethod
		def init( form, data ):

			return Pool() if ( form == 0 ) else apply( Pool, data )

	class Worker( TypeMethod ):

		@staticmethod
		@abstractmethod
		def init( form, data ):

			pass

	def __init__( self, info, args ):
		"""Initialization for TypeWorker derived classes

		Creates `worker` using `info` before calling the `work` method
		"""
		
		[ exec( typeProperty( name ) ) for name in ( "pool", "worker" ) ]

		( self.form, self.poolInfo, self.workerInfo ) = info

		self.update()

		self.work( args )

	####################################################################

	@staticmethod
	@abstractmethod
	def __displayInfo( infoFormat, info ):
		"""Abstract method for displaying 'info'

		Any derived TypeWorker must define this method and return
		the selected info as a formatted string according to
		infoFormat
		"""

		pass

	####################################################################

	def displayPoolInfo( self ):
		"""Method for displaying poolInfo

		Calls __display on poolInfo with infoFormat
		"""

		return __displayInfo( self.infoFormat, self.poolInfo )

	####################################################################

	def displayWorkerInfo( self ):
		"""Method for displaying workerInfo

		Calls __display on workerInfo with infoFormat
		"""

		return __displayInfo( self.infoFormat, self.workerInfo )

########################################################################