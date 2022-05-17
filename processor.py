from PIL import Image
import time

fileName = 'sample/IMG_8222.jpg'

myImage = Image.open(fileName)
myImageLoad = myImage.load()

# returns true if all the following are true:
#	x between values 0 inclusive, horizontal resolution exclusive
#	y between values 0 inclusive, vertical resolution exclusive
def imageBoundsCheck(image, x, y):
	size = image.size
	return (x >= 0 and y >= 0) and (x < size[0] and y < size[1])


def imageBoundsCheckRadius(image, x, y, radius):
	size = image.size
	return (x - radius >= 0 and y - radius >= 0) and (x < size[0] - radius and y < size[1] - radius)



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



def redBackgroundCheck(color):
	# the maximum value between G(reen) and B(lue)
	maxNonRedVal = max(color[1], color[2])
	maxNonRedValAllowed = 130
	
	# this is a highly generalized number: the GREATER the number, the GREATER the minimum difference will be
	diffBright = 160
	
	# the main algorithm for the minimum DIFFERENCE between the R(ed) and other G and B maximum
	diffThresh = min(int(diffBright * (maxNonRedVal / 255)), 255)
	
	# the R(ed) value of the color must exceed this amount for the whole color to be considered for our purposes "red"
	minimumRedVal = maxNonRedVal + diffThresh
	
	#print('given color: %s\tred minimum: %d\tdiffThresh: %d' % (str(color), minimumRedVal, diffThresh))
	
	isRed = (color[0] >= minimumRedVal) and (maxNonRedVal <= maxNonRedValAllowed)
	
	return isRed


class RegionChunk:
	
	# you give the exact number of Regions in both the vertical and horizontal direction
	# "posByCorner" = the start X/Y is actually the top left CORNER of a Region instead of the CENTER
	# startPos: tuple (x,y)
	# jump: tuple (x,y)
	# regionNum: tuple (x,y)
	def chunkDefineExact(self, startPos, jump, regionNum, regionRadius, posByCorner=False, jumpByRadius=False):
		self.regionList = []
		navX = startPos[0]
		navY = startPos[1]
		
		if(jumpByRadius):
			jump = (regionRadius, regionRadius)
		
		if(posByCorner):
			navX += regionRadius
			navY += regionRadius
		
		if not imageBoundsCheckRadius(self.imageObject, navX, navY, regionRadius):
			return False
		
		for vert in range(regionNum[1]):
			for horz in range(regionNum[0]):
				self.regionList.append(Region(self.imageObject, self.imageLoaded, (navX, navY), regionRadius))
				
				navX += jump[0]
			
			navY += jump[1]
			navX -= jump[0] * (regionNum[0])
		
		return True
		
	# you give a number of pixels; it will try to pack as many Regions as it can depending on their radius
	# considered to be more "lazy"
	# "useMax" will choose the maximium calculated radius, instaed of minimum
	def chunkDefinePack(self, topLeftCorner, bottomRightCorner, regionNum, useMax=False):
		self.regionList = []
		
		width = bottomRightCorner[0] - topLeftCorner[0]
		height = bottomRightCorner[1] - topLeftCorner[1]
		
		radiusCalc = (int(width / regionNum[0]), int(height / regionNum[1]))
		radius = min(radiusCalc)
		
		if(useMax):
			radius = max(radiusCalc)
		
		# regions cannot have arbitrary widths or lengths, they MUST conform to a radius
		# therefore, the radius will be based on the SMALLER of the width or height
		
		return self.chunkDefineExact(topLeftCorner, (0, 0), regionNum, radius, True, True)


	def chunkDefinePackAuto(self, topLeftCorner, bottomRightCorner, regionRadius):
		self.regionList = []
		
		width = bottomRightCorner[0] - topLeftCorner[0]
		height = bottomRightCorner[1] - topLeftCorner[1]
		
		# LOOK AT THIS LATER: the getRegionPixelList method in the Region class gets an index out of bounds error
		# maybe getRegionPixelList is to blame, not this method
		regionNumHorz = max(int(width / regionRadius) - 1, 0)
		regionNumVert = max(int(height / regionRadius) - 1, 0)
		
		regionNum = (regionNumHorz, regionNumVert)
		
		return self.chunkDefineExact(topLeftCorner, (0, 0), regionNum, regionRadius, True, True)


	def chunkFillColorAverage(self):
		for region in self.regionList:
			region.imageFillRegion(region.getRegionPixelAverage())
	
	
	def chunkLabelRedDetectRegions(self):
		for region in self.regionList:
			if(region.isRegionRed()):
				region.imageFillRegion((255, 0, 255))
	
	
	def chunkFillColor(self, color):
		for region in self.regionList:
			region.imageFillRegion(color)
	
	
	# outlierThresh: for each direction, if the bound of a iterated red region EXCEEDS the average by a certain amount, then it will NOT be considered as the new "farthest"
	# label: color the region if it is red
	# strictFilter: ONLY use the AVERAGE BOUNDS if True, use both average and PREVIOUS CONSECUTIVE REGION BOUNDS is False
	def chunkRedDetectRegions(self, outlierThresh, filterBoundOutliers=True, strictFilter=False, label=False, verboseDebug=False): #boundCheckName
		
		regionRedDetect = []
		
		for region in self.regionList:
			if(region.isRegionRed()):
				regionRedDetect.append(region)
		
		# use the FIRST REGION IN THE WHOLE LIST, REGARDLESS IF IT IS RED OR NOT
		#regionFirst = self.regionList[0]
		
		# use the FIRST REGION in the LIST OF "RED" REGIONS (RECOMMENDED)
		regionFirst = regionRedDetect[0]
		
		
		regionFirstBounds = regionFirst.pixBounds
		
		# the topmost, bottommost, leftmost, rightmost regions that triggered
		# NOTE: this is calculated by side CLOSEST to a particular direction (e.g. topmost), NOT the center alone
		boundDirs = ['top', 'bottom', 'left', 'right']
		
		boundFarthest = {
			'top' : regionFirstBounds['top'],
			'bottom' : regionFirstBounds['bottom'],
			'left' : regionFirstBounds['left'],
			'right' : regionFirstBounds['right']
		}
		
		boundAverage = boundFarthest.copy()
		
		boundSum = boundFarthest.copy()
		
		# for left and top, find minimum value; for right and bottom, find maximum value
		dirLessThan = ['left', 'top']
		dirGreaterThan = ['right', 'bottom']
		
		regionCountForAverage = 0
		
		regionPrevBounds = regionFirstBounds
		
		if verboseDebug:
			print('FIRST REGION BOUND: %s' % str(boundFarthest))
			time.sleep(3)
		
		diffPrev = 0
		
		for region in regionRedDetect[1:]:
			bounds = region.pixBounds
			
			#for b in boundDirs:
			#	boundSum[b] += bounds[b]
			#	boundAverage[b] = boundSum[b] / regionCountForAverage
			
			#isOutlierAnyDir = False
			
			# PERSONAL NOTES:
			# situation A: there is only ONE OUTLIER region very far away from the rest
			# siutation B: there is a GROUP OF OUTLIERS far away from the MAJORITY
			
			# using diffAvg alone is BEST for SITUATION B, as it will STRICTLY ignore ANY NUMBER OF REGIONS that are far away from the rest
			# using both diffAvg and diffPrev is BEST for accurate "boundFarthest" results, BUT can be tricked by a small group of outlier regions
			# 		(a small group, as in, consecutive regions in the list: one after the other)
			
			for b in dirLessThan:
				diffAvg = abs(bounds[b] - boundAverage[b])
				
				if strictFilter:
					diffPrev = diffAvg
				else:
					diffPrev = abs(bounds[b] - regionPrevBounds[b])
				
				if(diffAvg <= outlierThresh or diffPrev <= outlierThresh or not filterBoundOutliers):
					regionCountForAverage += 1
					boundSum[b] += bounds[b]
					boundAverage[b] = boundSum[b] / regionCountForAverage
					
					if(bounds[b] < boundFarthest[b]):
						boundFarthest[b] = bounds[b]
				
			#for b in dirGreaterThan:
			#	diff = abs(bounds[b] - boundAverage[b])
			#	
			#	if(bounds[b] > boundFarthest[b] and (diff <= outlierThresh or not filterBoundOutliers)):
			#		boundFarthest[b] = bounds[b]
			
			for b in dirGreaterThan:
				diffAvg = abs(bounds[b] - boundAverage[b])
				
				if strictFilter:
					diffPrev = diffAvg
				else:
					diffPrev = abs(bounds[b] - regionPrevBounds[b])
				
				if(diffAvg <= outlierThresh or diffPrev <= outlierThresh or not filterBoundOutliers):
					regionCountForAverage += 1
					boundSum[b] += bounds[b]
					boundAverage[b] = boundSum[b] / regionCountForAverage
					
					if(bounds[b] > boundFarthest[b]):
						boundFarthest[b] = bounds[b]
			
			#for b in dirLessThan:
			#	diff = abs(bounds[b] - boundAverage[b])
			#	
			#	checkOutlier = (diff > outlierThresh)
			#	if(checkOutlier)
			#	
			#	else(bounds[b] < boundFarthest[b] and (not checkOutlier or not filterBoundOutliers)):
				
			#for b in dirGreaterThan:
			
			if label:
				region.imageFillRegion((255, 0, 255))
			
			regionPrevBounds = bounds
			
			if verboseDebug:
				print('-----')
				print('\nPOS: %s' % str(region.pixLocation))
				print('\nAVG')
				
				for d in boundDirs:
					print('\tDIR: %s\tVALUE: %s' % (d, int(boundAverage[d])))
				
				time.sleep(0.1)
		
		return {
			'regionList' : regionRedDetect,
			'boundFarthest' : boundFarthest,
			'boundSum' : boundSum,
			'boundAverage' : boundAverage
		}
				
	
	
	def __init__(self, imageObject, imageLoaded):
		self.imageObject = imageObject
		self.imageLoaded = imageLoaded
		self.regionList = []



class Region:

	def isRegionRed(self):
		colorAverage = self.getRegionPixelAverage()
		return redBackgroundCheck(colorAverage)


	def imageFillRegion(self, color):
		centerX = self.pixLocation[0]
		centerY = self.pixLocation[1]
		
		# should I have a +1 to the right-hand bound of the horizontal and vertical range??
		# the +1 results in an index bound error when in an image with a resolution INDENTICAL to the region size
		for x in range(centerX - self.pixRadius, centerX + self.pixRadius):
			for y in range(centerY - self.pixRadius, centerY + self.pixRadius):
				self.imageLoaded[x, y] = color


	def getRegionPixelList(self):
		centerX = self.pixLocation[0]
		centerY = self.pixLocation[1]
		
		pixelList = []
		
		if self.pixRadius == 0:
			pixelList.append(self.imageLoaded[centerX, centerY])
		else:
			# should I have a +1 to the right-hand bound of the horizontal and vertical range??
			# the +1 results in an index bound error when in an image with a resolution INDENTICAL to the region size
			# YET, the +1 produces the correct (or at least expected) number of items in the pixelList
			for x in range(centerX - self.pixRadius, centerX + self.pixRadius):
				for y in range(centerY - self.pixRadius, centerY + self.pixRadius):
					#print('[[ %d , %d ]]' % (x, y))
					pixelList.append(self.imageLoaded[x, y])
		
		return pixelList
	

	def getRegionPixelAverage(self):
		redSum = 0
		greenSum = 0
		blueSum = 0
		pixelList = self.getRegionPixelList()
		pixelCount = len(pixelList)
		
		for color in pixelList:
			redSum += color[0]
			greenSum += color[1]
			blueSum += color[2]
		
		return (int(redSum / pixelCount), int(greenSum / pixelCount), int(blueSum / pixelCount))


	def __init__(self, imageObject, imageLoaded, pixLocation, pixRadius=1):
		self.imageObject = imageObject
		self.imageLoaded = imageLoaded
		self.pixLocation = pixLocation # the center of the region
		self.pixRadius = pixRadius
		
		# the topmost, bottommost, leftmost, and rightmost x/y values
		self.pixBounds = {
			'top':(pixLocation[1] - pixRadius),
			'bottom':(pixLocation[1] + pixRadius),
			'left':(pixLocation[0] - pixRadius),
			'right':(pixLocation[0] + pixRadius)
		}



def regionTestA():	
	r1 = Region(myImage, myImageLoad, (2, 2), 2)

	print(r1.getRegionPixelList())

	print(r1.getRegionPixelList())
	print(r1.getRegionPixelAverage())

	r1.imageShowRegion()


# OLDER example of using a chunk to fill regions with their own average colors

def chunkTestA():
	rc1 = RegionChunk(myImage, myImageLoad)

	rc1.chunkDefineExact((0, 0), (0, 0), (40, 20), 25, True, True)

	rc1List = rc1.regionList

	print(len(rc1List))

	for reg in rc1List:
		#print('REGION: radius = %d, location = %s' % (reg.pixRadius, str(reg.pixLocation)))
		reg.imageFillRegion(reg.getRegionPixelAverage())

	myImage.show("cooleo")


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
				print('\n(this is a boolean, type "y" for true/yes, type "n" for false/no')
			
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
	
	# the amount of pixels until you pass the red shirt and are now in the "tripod" area for my test images
	pixelLocationTripod = 2850
	leftChunkWidth = 300
	
	print(myImage.size)
	
	topChunk = RegionChunk(myImage, myImageLoad)
	topChunk.chunkDefinePackAuto((leftChunkWidth, 0), (imageWidth, 550), regionRadius)
	
	bottomChunk = RegionChunk(myImage, myImageLoad)
	bottomChunk.chunkDefinePackAuto((leftChunkWidth, pixelLocationTripod - 400), (imageWidth, pixelLocationTripod), regionRadius)
	
	leftChunk = RegionChunk(myImage, myImageLoad)
	leftChunk.chunkDefinePackAuto((0, 0), (leftChunkWidth, pixelLocationTripod), regionRadius)
	
	chunkDict = {
		'top':topChunk,
		'bottom':bottomChunk,
		'left':leftChunk
	}
	
	command = input('command? ')
	
	if(command == 'fill'):
		topChunk.chunkFillColor((255, 0, 0))
		bottomChunk.chunkFillColor((0, 0, 255))
		leftChunk.chunkFillColor((255, 255, 0))
		myImage.show()
	
	elif(command == 'rd'):
		cropMarginPixel = 24
		outlierThresh = 96
		filterOutlier = True
		strictFilter = False
		
		# fill in red regions with pink for debug purposes
		fillFinding = False
		
		chunkResults = {}
		
		for chunkName in chunkDict.keys():
			chunk = chunkDict[chunkName]
			
			chunkResults[chunkName] = chunk.chunkRedDetectRegions(outlierThresh, filterOutlier, strictFilter, fillFinding, False)
			
		cropTop = chunkResults['top']['boundFarthest']['bottom'] - cropMarginPixel
		cropBottom = chunkResults['bottom']['boundFarthest']['top'] + cropMarginPixel
		#cropRight = chunkResults['left']['boundAverage']['right']
		cropRight = chunkResults['left']['boundFarthest']['right'] - cropMarginPixel
		
		print('top %d, bottom %d, right %d' % (cropTop, cropBottom, cropRight))
		
		# crop: (left, upper, right, lower)
		myImageCropped = myImage.crop((cropRight, cropTop, imageWidth, cropBottom))
		
		myImageCropped.show()


# running the debug method for showing the palettes of red for the red region detection
def chunkTestC():
	redBackgroundCheckDebugSimulation()
	#color = myImageLoad[0, 0]

	#redBackgroundCheck(color)
	


#chunkTestA()
#chunkTestB()
#chunkTestB2()
chunkTestB3()
#chunkTestC()
