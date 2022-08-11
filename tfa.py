import numpy as np
import functools as ft
import itertools as it
import multiprocessing as mp


#####

# Function Name: autoFormat

# A subroutine for constructing complex strings using a 
# boolean-array, `selection`, as a slice on the provided array, `collection`

# Input:
# `collection`	:	An array of string-compatible 'elements'
# `selection`	:	A boolean-array the same dimensions as `collection`
# `pre`			:	Any string needing to occur at the beginning of the result
# `sep`			:	Any string, or list of strings, or generator of strings, needing to occur in between 'selected elements'
# `end`			:	Any string needing to occur at the end of the result

# Output:
# A complex formatted string which begins with `pre`, ends with `end`, and has exactly the 'elements'
# from `collection` for which the same index yields a True in `selection`, each seperated by `sep`

def autoFormat( collection, selection, pre="", sep="", end="" ):

	if( type( sep ) == type( '' ) ):

		return ft.reduce( lambda acc, x: acc + str ( x ) + sep, collection[ selection ], pre ) + end

	elif( type( sep ) == type( [] ) ):

		selection = collection[ selection ]

		return ft.reduce( lambda acc, x: acc + str ( selection[ x ] ) + sep[ x ], range( len( selection ) ), pre ) + end

	elif( type( sep ) == type( ( lambda : ( yield ) )() ) )

		return ft.reduce( lambda acc, x: acc + str ( x ) + next(sep), collection[ selection ], pre ) + end


#####

# Function Name: checkOperatorType

# A subroutine for checking if the 'Object in Question', `oiq`, has a 
# compatible type, `oiqType`, with the provided `operatorName`

# Input:
# `oiqType`			:	'Object in Question'
# `operatorName`	:	The name of a function that may or may not be defined on the 'Object in Question'

# Output:
# A boolean indicating whether or not `oiqType` and the type of `operator` match

def checkOperatorType( oiqType, operatorName ):

	return ( operatorName in oiqType.__dict__ )

#####

# Function Name: checkOperatorType

# A subroutine for checking if the 'Object in Question', `oiq`, has a 
# compatible type, `oiqType`, with any `elements` in the provided `collection`

# Input:
# `oiqType`		:	'Object in Question'
# `collection`	:	An iterable that may or may not be completely of type `oiqType`

# Output:
# A boolean-array indicating whether or not `oiqType` and the type of each 'element' in `collection` match
def checkCollectionType( oiqType, collection ):

	return np.array( [ ( oiqType and type( element ) ) for element in collection ] )

#####

# Function Name: checkLimitationType

# A subroutine for checking if the 'Object in Question', `oiq`, has a 
# compatible type, `oiqType`, with the 'Comparison Operator', `comparator`, 
# and `bounds` in `limitation`

# Input:
# oiqType		:	The type of the 'Object in Question'
# limitation	:	A pair of 'Comparison Operator' and 'Bounds'

# Output:
# A boolean-triple indicating which of the 'Comparison Operator' and `bounds`
# have compatible type with `oiqType`

def checkLimitationType( oiqType, limitation ):

	return np.array( [ 
				checkOperatorType( oiqType, limitation[ 0 ] ),
				checkCollectionType( oiqType, limitation[ 1 ][ 0 ] ),
				checkCollectionType( oiqType, limitation[ 1 ][ 1 ] ) 
			] )

#####

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

	return np.array( [ comparator( bound, oiq ) for bound in bounds ] ).all()

def checkRightBounds( oiq, comparator, bounds ):

	return np.array( [ comparator( oiq, bound ) for bound in bounds ] ).all()

#####

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

#####

# Function Name: checkEvery

# A subroutine for checking that all boolean-subarrays, `subcollection`s, of the 
# boolean-array-array, `collection`, evaluate to True under application of `*.all()`

# Input:
# `collection`	:	A boolean-array-array

# Output:
# A boolean indicating whether every subarray is 'All' True or not

def checkEvery( collection, neg = False ):

	return np.array( [ ( neg ^ subcollection.all() ) for subcollection in collection ] )

#####

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

#####

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

#####	
