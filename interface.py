# Project Monocle: Automated Image Cropping for Books and Textbooks
# interface.py: Shell/CLI Commands for Using primary.py

# Eiza Stanford "charkybarky" 2022
import primary
import argparse
import pathlib
from PIL import Image

def commandParse():
	helpMsg = [
		'Set up the cropping a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a',
		'a'
	]
	
	helpMsg = ['blank' for i in range(100)]
	
	defaultRadius = 25
	defaultCropMargin = 0
	defaultOutlierThreshold = 95
	defaultImageSuffix = '_cropped'
	
	helpMsgIndex = 0
	
	def helpMsgCycle():
		nonlocal helpMsgIndex
		
		helpMsgIndex += 1
		
		return helpMsg[helpMsgIndex - 1]
	
	parser = argparse.ArgumentParser(description='Automatically crop images to the centered subject surrounded by a dark red background.')
	
	groupImage = parser.add_argument_group('images')
	groupImage.add_argument('image', type=pathlib.PosixPath, metavar='image', nargs='+', help=helpMsgCycle())
	groupImage.add_argument('-s', '--suffix', type=str, metavar='suffix', nargs='?', default=defaultImageSuffix, help=helpMsgCycle())
	
	groupChunk = parser.add_argument_group('chunk management')
	groupChunk.add_argument('-r', '--radius', metavar='pixels', nargs=1, type=int, default=defaultRadius, help=helpMsgCycle())
	
	groupChunkBox = parser.add_argument_group('chunk management: box approach')
	groupChunkBox.add_argument('-o', '--outer-box', metavar=('left', 'upper', 'right', 'lower'), nargs=4, type=int, help=helpMsgCycle())
	groupChunkBox.add_argument('-i', '--inner-box', metavar=('left', 'upper', 'right', 'lower'), nargs=4, type=int, help=helpMsgCycle())
	
	groupChunkBook = parser.add_argument_group('chunk management: book approach')
	groupChunkBook.add_argument('-B', '--book', dest='book', metavar=('tripod', 'vert', 'horiz'), nargs=3, type=int, help=helpMsgCycle())
	
	groupOutlier = parser.add_argument_group('outlier filtering')
	groupOutlier.add_argument('-f', '--filter-enable', action='store_true', help=helpMsgCycle())
	groupOutlier.add_argument('-t', '--threshold', metavar='pixels', nargs=1, type=int, default=defaultOutlierThreshold, help=helpMsgCycle())
	groupOutlier.add_argument('-S', '--strict', action='store_true', help=helpMsgCycle())
	
	groupMisc = parser.add_argument_group('miscellaneous crop options')
	groupMisc.add_argument('-O', '--force-orientation', action='store_true', help=helpMsgCycle())
	groupMisc.add_argument('-m', '--crop-margin', metavar='pixels', nargs=1, type=int, default=defaultCropMargin, help=helpMsgCycle())
	
	groupDebug = parser.add_argument_group('debugging')
	groupDebug.add_argument('-x', '--debug-chunk-fill', action='store_true', help=helpMsgCycle())
	#groupDebug.add_argument('-y', '--debug-background-fill', action='store_true', help=helpMsgCycle())
	
	args = parser.parse_args()
	#args = parser.parse_args(input('> ').split())
	
	print(args)
	
	# box (left, upper, right, lower)
	
	if not (args.book or args.outer_box or args.inner_box):
		parser.error('at least one of the following arguments is needed: --outer-box, --inner-box, or --book')
	
	for imagePath in args.image:
		if imagePath.exists():
			imagePathStr = str(imagePath)
			
			imageObject = Image.open(imagePathStr)
			imageLoaded = imageObject.load()
			
			cropper = primary.Cropper(imageObject, imageLoaded)
			
			regionRadius = args.radius
			
			if args.book:
				cropper.chunkSetupTextbook(*args.book, regionRadius)
				
			else:
				boxOuter = args.outer_box
				boxInner = args.inner_box
				
				size = imageObject.size
				center = (int(size[0] / 2), int(size[1] / 2))
				
				if boxOuter:
					boxOuter = tuple(boxOuter)
				
				else:
					boxOuter = (0, 0, size[0], size[1])
				
				if boxInner:
					boxInner = tuple(boxInner)
				
				else:
					boxInner = (center[0] - 1, center[0] - 1, center[0] + 1, center[0] + 1)
				
				cropper.chunkSetup(boxOuter, boxInner, regionRadius)
			
			imageFinal = None
			
			if args.debug_chunk_fill:
				cropper.chunkFillColor()
				imageFinal = imageObject
				
			else:
				imageFinal = cropper.crop(args.crop_margin, args.threshold, args.filter_enable, args.strict, args.force_orientation, False)
			
			print('PATH %s' % str(imagePath))
			print('SUFFIX %s' % args.suffix)
			
			imagePathNew = imagePath.with_name('%s%s' % (imagePath.stem, args.suffix))
			print('NEW PATH %s' % str(imagePathNew))
			#print('NEW: %s%s' % (imagePath.name, args.suffix))
			
			# (in pathlib, the suffix refers to the file extension)
			
			# (instead of using attribute suffix, suffixes is used in case the file name for some reason had multiple extensions)
			#imagePathNew = imagePathNew.with_suffix(''.join(imagePath.suffixes))
			
			imagePathNew = imagePathNew.with_suffix(imagePath.suffix)
			
			print('NEW PATH %s' % str(imagePathNew))
			imageFinal.save(imagePathNew)
		else:
			parser.error('no file exists at path %s' % str(imagePath))
	
	#if args.book:
	#	pass
	
	#else:
	#	boxOuter = args.outer_box
	#	boxInner = args.inner_box

def main():
	commandParse()

if __name__ == '__main__':
	main()
