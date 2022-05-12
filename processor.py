from PIL import Image

fileName = 'sample/IMG_8218.jpg'

image = Image.open(fileName)
imageLoad = image.load()

class Region:

	def getRegionPixelList(self):
		centerX = self.pixLocation[0]
		centerY = self.pixLocation[1]
		
		pixelList = []
		
		if self.pixRadius == 0:
			pixelList.append(self.imageLoaded[centerX, centerY])
		else:
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


	def __init__(self, imageLoaded, pixLocation, pixRadius=1):
		self.imageLoaded = imageLoaded
		self.pixLocation = pixLocation
		self.pixRadius = pixRadius

r1 = Region(imageLoad, (5, 5), 1)
print(r1.getRegionPixelList())
print(r1.getRegionPixelAverage())
