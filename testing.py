from primary import *
from PIL import Image


#fileName = 'sample/IMG_8222.jpg'
#fileName = 'sample/IMG_8238.jpg'
fileName = 'sample/right_2.jpg'

myImage = Image.open(fileName)
myImageLoad = myImage.load()


def redBackgroundCheckDebugSimulation():
	lowBound = 0
	highBound = 140
	increment = 10
	
	regionSquareRadius = 50
	regionSquareDiameter = regionSquareRadius * 2
	
	# the number of different possible shades of red to test
	# also the number of squares needed to show each possible shade
	colorCount = int((highBound - lowBound) / increment) + 1
	
	print(colorCount)
	
	# image to render the regions onto
	blankImageRes = (colorCount * regionSquareDiameter, regionSquareDiameter)
	blankImage = Image.new("RGB", blankImageRes, "green")
	blankImageLoad = blankImage.load()

	print(blankImageRes)

	#redPaletteChunk = RegionChunk(blankImage, blankImageLoad)
	#success = redPaletteChunk.chunkDefineExact((0, 0), (0, 0), (colorCount, 1), regionSquareRadius, True, True)
	
	#print(success)
	#print(len(redPaletteChunk.regionList))

	posX = 0
	currentColorVal = lowBound

	diffBright = 150

	for regionIndex in range(colorCount):		
		#region = redPaletteChunk.regionList[regionIndex]
		region = Region(blankImage, blankImageLoad, (posX, regionSquareRadius), regionSquareRadius)
		
		maxNonRedVal = currentColorVal
		diffThresh = min(int(diffBright * (maxNonRedVal / 255)), 255)
		redShadeColor = (maxNonRedVal + diffThresh, maxNonRedVal, maxNonRedVal)
		
		print('index=%d\tmaxnonred=%d\tthresh=%d\tshade=%s' % (regionIndex, maxNonRedVal, diffThresh, str(redShadeColor)))
		
		region.imageFillRegion(redShadeColor)
		
		currentColorVal += increment
		posX += regionSquareDiameter
	
	blankImage.show()


def regionTestA():
	r1 = Region(myImage, myImageLoad, (2, 2), 2)

	print(r1.getRegionPixelList())
	print(r1.getRegionPixelAverage())

	r1.imageFillRegion((255, 0, 0))
	
	myImage.show()


# OLDER example of using a chunk to fill regions with their own average colors

def chunkTestA():
	rc1 = RegionChunk(myImage, myImageLoad)

	rc1.chunkDefineExact((0, 0), (0, 0), (40, 20), 25, True, True)

	rc1List = rc1.regionList

	print(len(rc1List))

	for reg in rc1List:
		#print('REGION: radius = %d, location = %s' % (reg.pixRadius, str(reg.pixLocation)))
		reg.imageFillRegion(reg.getRegionPixelAverage())

	myImage.show()


# example of using a chunk to fill regions with their own average colors
def chunkTestB():
	rc2 = RegionChunk(myImage, myImageLoad)
	
	rc2.chunkDefinePack((0, 0), (2000, 400), (80, 15), True)
	
	rc2.chunkFillColorAverage()
	
	myImage.show()


# new methods for the RegionChunk, especially the "red-detect" method
def chunkTestB2():
	rcb2 = RegionChunk(myImage, myImageLoad)
	
	imageWidth = myImage.size[0]
	imageHeight = myImage.size[1]
	
	print(myImage.size)
	#rcb2.chunkDefinePack((0, 0), (2000, 3500), (60, 100), True)
	rcb2.chunkDefinePackAuto((200, 0), (imageWidth, 600), 24)
	#rcb2.chunkDefinePackAuto((0, 0), (imageWidth, imageHeight), 25)
	
	print('available commnands: fill (color chunk regions), avg (show color averages of chun regions), rd (use red detection)')
	
	command = input('command? ')
	
	if(command == 'fill'):
		rcb2.chunkFillColor((255, 0, 255))
		
	elif(command == 'avg'):
		rcb2.chunkFillColorAverage()
		
	elif(command == 'rd'):
		attributes = {
			'filter outlier':'boolean',
			'strict average-only filter':'boolean',
			'outlier pixel threshold':'int'
		}
		
		attributeValues = {}
		
		for attName in attributes.keys():
			attType = attributes[attName]
			
			if attType == 'boolean':
				print('\n(this is a boolean, type "y" for true/yes, type "n" for false/no)')
			
			ask = input('ATTRIBUTE: %s (%s)> ' % (attName, attType))
			
			if(attType == 'boolean'):
				attributeValues[attName] = (ask == 'y')
				
			elif(attType == 'int'):
				attributeValues[attName] = int(ask)
			
			print('VALUE: %s (%s) = %s' % (attName, attType, str(attributeValues[attName])))
			print('- - - - - - - - -')
				
		print('RUNNING RED-DETECT IN 3 SECONDS...')
		
		outlierThresh = attributeValues['outlier pixel threshold']
		modeOutlierFilter = attributeValues['filter outlier']
		modeStrict = attributeValues['strict average-only filter']
		
		time.sleep(3)
		
		# thresh recommend 96
		results = rcb2.chunkRedDetectRegions(outlierThresh, modeOutlierFilter, modeStrict, True, True)
		#rcb2.chunkLabelRedDetectRegions()
		
		# PRINT RESULTS, EXCLUDING LIST OF REGION OBJECTS
		boundDataKeys = list(results.keys())[1:]
		
		print('\nRED-DETECT RESULTS:')
		for key in boundDataKeys:
			boundData = results[key]
			print('DATA: %s' % key)
			
			for direction in boundData.keys():
				print('\tDIRECTION: %s\t\tVALUE: %d' % (direction, boundData[direction]))
	myImage.show()


# actually cropping an image for the first time
def chunkTestB3():
	imageWidth = myImage.size[0]
	imageHeight = myImage.size[1]
	regionRadius = 24
	#regionRadius = 4
	
	# the amount of pixels until you pass the red shirt and are now in the "tripod" area for my test images
	pixelLocationTripod = 2850
	
	topBottomChunkHeight = 400
	leftRightChunkWidth = 300
	
	print(myImage.size)
	
	topChunk = RegionChunk(myImage, myImageLoad)
	topChunk.chunkDefinePackAuto((leftRightChunkWidth, 0), (imageWidth - leftRightChunkWidth, topBottomChunkHeight), regionRadius)
	
	bottomChunk = RegionChunk(myImage, myImageLoad)
	bottomChunk.chunkDefinePackAuto((leftRightChunkWidth, pixelLocationTripod - topBottomChunkHeight), (imageWidth - leftRightChunkWidth, pixelLocationTripod), regionRadius)
	
	leftChunk = RegionChunk(myImage, myImageLoad)
	leftChunk.chunkDefinePackAuto((0, 0), (leftRightChunkWidth, pixelLocationTripod), regionRadius)
	
	rightChunk = RegionChunk(myImage, myImageLoad)
	rightChunk.chunkDefinePackAuto((imageWidth - leftRightChunkWidth, 0), (imageWidth, pixelLocationTripod), regionRadius)
	
	chunkDict = {
		'top':topChunk,
		'bottom':bottomChunk,
		'left':leftChunk,
		'right':rightChunk
	}
	
	print('available commnands: fill (color chunk regions), show (show original image without any modification), rd (use red detection)')
	
	command = input('command? ')
	
	if(command == 'fill'):
		topChunk.chunkFillColor((255, 0, 0))
		bottomChunk.chunkFillColor((0, 0, 255))
		leftChunk.chunkFillColor((255, 255, 0))
		rightChunk.chunkFillColor((0, 255, 0))
		myImage.show()
	
	# show the original image
	elif(command == 'show'):
		myImage.show()
	
	# red detect
	elif(command == 'rd'):
		ask = input('debug (d) or crop (c)? (c/d) ')
		
		cropMarginPixel = int(regionRadius * 1.25)
		outlierThresh = 96
		filterOutlier = True
		strictFilter = False
		
		# fill in red regions with pink for debug purposes
		fillFinding = (ask == 'd')
		
		chunkResults = {}
		
		for chunkName in chunkDict.keys():
			chunk = chunkDict[chunkName]
			
			chunkResults[chunkName] = chunk.chunkRedDetectRegions(outlierThresh, filterOutlier, strictFilter, fillFinding, False)
			
		cropTop = chunkResults['top']['boundFarthest']['bottom'] - cropMarginPixel
		cropBottom = chunkResults['bottom']['boundFarthest']['top'] + cropMarginPixel
		#cropRight = chunkResults['left']['boundAverage']['right']
		cropLeft = chunkResults['left']['boundFarthest']['right'] - cropMarginPixel
		
		print('top %d, bottom %d, right %d' % (cropTop, cropBottom, cropLeft))
		
		# crop: (left, upper, right, lower)
		myImageCropped = myImage.crop((cropLeft, cropTop, imageWidth, cropBottom))
		
		if(ask == 'd'):
			myImage.show()
		else:
			myImageCropped.show()


def chunkTestB4():
	c1 = Cropper(myImage, myImageLoad)
	
	c1.chunkSetupTextbook(2850, 300, 400, 24)
	
	c1.crop(18, 96, True, False, True, False).show()
	
	#myImage.show()


# running the debug method for showing the palettes of red for the red region detection
def chunkTestC():
	redBackgroundCheckDebugSimulation()
	#color = myImageLoad[0, 0]

	#redBackgroundCheck(color)
	

def main():
	testFunctionDict = {
		'RA':[regionTestA, 'a test for initializing a Region object and filling it in with red'],
		'A':[chunkTestA, 'a test for the first chunk definition function chunkDefineExact'],
		'B':[chunkTestB, 'a test for the higher-level chunkDefinePack function; fills cover averages over some regions'],
		'B2':[chunkTestB2, 'an interface for controlling the color/red-detection system with basic commands'],
		'B3':[chunkTestB3, 'a prototype of the cropping system without the Cropper class with basic commands'],
		'B4':[chunkTestB4, 'the final implementation of the cropping system: creates a Cropper object and uses Cropper.crop'],
		'C':[chunkTestC, 'runs the "red background check simulation" showing the different shades of red that would actually count as "red"']
	}
	
	print('WARNING: as the project is updated and modified over time, these test functions may break.')
	print('At the time that this UI was created, all test functions should be operational.')
	print('Please select a test function to execute:\n')
	
	for label in testFunctionDict:
		print('%s: %s' % (label, testFunctionDict[label][1]))
	
	userLabel = None
	
	while not userLabel in testFunctionDict:
		userLabel = input('select> ').upper()
	
	print('Executing %s...' % userLabel)
	
	testFunctionDict[userLabel][0]()

if __name__ == '__main__':
	main()
