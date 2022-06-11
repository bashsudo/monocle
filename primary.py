# Project Monocle: Automated Image Cropping
# primary.py: Main Important Modules
from PIL import Image
import time

# returns true if all the following are true:
#	x between values 0 inclusive, horizontal resolution exclusive
#	y between values 0 inclusive, vertical resolution exclusive
def imageBoundsCheck(image, x, y):
	size = image.size
	return (x >= 0 and y >= 0) and (x < size[0] and y < size[1])


def imageBoundsCheckRadius(image, x, y, radius):
	size = image.size
	return (x - radius >= 0 and y - radius >= 0) and (x < size[0] - radius and y < size[1] - radius)


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
		
		if(not regionRedDetect):
			return None
		
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


class Cropper:
	
	# a method that is not SPECIFICALLY meant for the yearbook images (more generic)
	# "box" is a tuple: (left, upper, right, lower) pixel coordinate
	def chunkSetup(self, outerBox, innerBox, regionRadius):
		self.chunkDict['top'].chunkDefinePackAuto((innerBox[0], outerBox[1]), (innerBox[2], innerBox[1]), regionRadius)
		self.chunkDict['bottom'].chunkDefinePackAuto((innerBox[0], innerBox[3]), (innerBox[2], outerBox[3]), regionRadius)
		self.chunkDict['left'].chunkDefinePackAuto((outerBox[0], outerBox[1]), (innerBox[1], outerBox[3]), regionRadius)
		self.chunkDict['right'].chunkDefinePackAuto((innerBox[2], outerBox[1]), (outerBox[2], outerBox[3]), regionRadius)
	
	
	def chunkFillColor(self):
		colorIndex = 0
		
		for side in self.chunkSides:
			self.chunkDict[side].chunkFillColor(self.fillColorSamples[colorIndex])
			
			colorIndex = (colorIndex + 1) % len(self.fillColorSamples)
	
	
	def chunkSetupTextbook(self, distanceUntilTripod, leftRightChunkWidth, topBottomChunkHeight, regionRadius):
		imageWidth = self.imageObject.size[0]
		imageHeight = self.imageObject.size[1]
		
		outerBox = (0, 0, imageWidth, distanceUntilTripod)
		innerBox = (leftRightChunkWidth, topBottomChunkHeight, imageWidth - leftRightChunkWidth, distanceUntilTripod - topBottomChunkHeight)
		
		self.chunkSetup(outerBox, innerBox, regionRadius)
	
	
	# returns if the book is LEFT or RIGHT orientation
	# CAN RETURN STRING: "left" "right" "both"
	# SOMEWHAT REDUNDANT, MAY REMOVE LATER (effectively integrated this with the "crop" method)
	def orientationDetect(self, outlierThresh, filterBoundOutliers=True, strictFilter=False):
		# if chunks not set up yet
		if(not self.chunkDict):
			return None
		
		leftResults = self.chunkDict['left'].chunkRedDetectRegions(outlierThresh, filterBoundOutliers, strictFilter)
		rightResults = self.chunkDict['right'].chunkRedDetectRegions(outlierThresh, filterBoundOutliers, strictFilter)
		
		leftCount = len(leftResults['regionList'])
		rightCount = len(rightResults['regionList'])
		
		if(rightCount > leftCount):
			return "right"
		elif(leftCount > rightCount):
			return "left"
		else:
			return "both"
		
	
	# forceOrientation: you can have only EITHER left or right side of book cropped (NOT both left and right side)
	def crop(self, cropMarginPixel, outlierThresh, filterBoundOutliers=True, strictFilter=False, forceOrientation=False, debug=False):
		# if chunks not set up yet
		if(not self.chunkDict):
			return None
		
		imageWidth = self.imageObject.size[0]
		imageHeight = self.imageObject.size[1]
		
		
		defaultCropValues = {
			'top':0,
			'bottom':imageHeight,
			'left':0,
			'right':imageWidth
		}
		
		# each side has a list with the following values:
			# 0 = for a particular side of chunk, this is the side of THAT chunk OPPPOSITE to its side
			# 1 = determines whether to subtract (-1) or add (1) the margin
		
		chunkSideRegionRedCount = {
			'top':0,
			'bottom':0,
			'left':0,
			'right':0
		}
		
		cropSettings = {
			'top':['bottom', -1],
			'bottom':['top', 1],
			'left':['right', -1],
			'right':['left', 1]
		}
		
		cropValues = defaultCropValues.copy()
		
		chunkResults = {}
		
		for side in self.chunkSides:
			chunk = self.chunkDict[side]
			
			settings = cropSettings[side]
			
			results = chunk.chunkRedDetectRegions(outlierThresh, filterBoundOutliers, strictFilter, debug, False)
			chunkResults[side] = results
			
			if results:
				cropValues[side] = results['boundFarthest'][settings[0]] + cropMarginPixel * settings[1]
				chunkSideRegionRedCount[side] = len(results['regionList'])
				
		
		cropTop = cropValues['top']
		cropBottom = cropValues['bottom']
		cropLeft = cropValues['left']
		cropRight = cropValues['right']
		
		if(forceOrientation):
			leftCount = chunkSideRegionRedCount['left']
			rightCount = chunkSideRegionRedCount['right']
			orientation = 'both'
			
			if(rightCount > leftCount):
				orientation = 'right'
			elif(rightCount < leftCount):
				orientation = 'left'
			
			if(orientation == 'left'):
				cropRight = defaultCropValues['right']
				
			elif(orientation == 'right'):
				cropLeft = defaultCropValues['left']
				
			# if both, assume to crop both left and right
		
		if(debug):
			print('top: %d, bottom: %d, left: %d, right %d' % (cropTop, cropBottom, cropLeft, cropRight))
		
		imageCropped = self.imageObject.crop((cropLeft, cropTop, cropRight, cropBottom))
		
		# crop (left, upper, right, lower) tuple box
		return imageCropped
	
	
	def __init__(self, imageObject, imageLoaded):
		self.fillColorSamples = []
		
		for red in range(0, 2):
			for green in range(0, 2):
				for blue in range(0, 2):
					self.fillColorSamples.append((red * 255, green * 255, blue * 255))
		
		del self.fillColorSamples[0]
		del self.fillColorSamples[6]
		
		self.chunkSides = [
			'top',
			'bottom',
			'left',
			'right'
		]
		
		self.imageObject = imageObject
		self.imageLoaded = imageLoaded
		
		self.chunkDict = {}
		
		for side in self.chunkSides:
			self.chunkDict[side] = RegionChunk(imageObject, imageLoaded)
