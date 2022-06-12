# Project Monocle: Automated Image Cropping for Books and Textbooks
# interface.py: Shell/CLI Commands for Using primary.py

# Eiza Stanford "charkybarky" 2022
import primary
import argparse
import pathlib
from PIL import Image

def commandParse():
	
	# === DEFAULT VALUES ===
	# this is NOT an argument; used if there is no inner box provided but an outer box
	defaultInnerBoxOffset = 300
	
	defaultRadius = 25
	defaultCropMargin = 0
	defaultOutlierThreshold = 95
	defaultImageSuffix = '_cropped'
	
	# === HELP MESSAGES (WITH DEFAULTS SUBSTITUTED IN) ===
	helpMsg = {
		'image':'This is the path(s) to the image(s) to be used and cropped. The original image(s) will NOT be modified in any way.',
		
		'suffix':'The suffix is placed between the name and file extension of the image(s). Optional. "%s" by default.' % defaultImageSuffix,
		
		'radius':'The radius of each region of pixels in the left, right, top, bottom chunk. The smaller, the more "fine," the larger, the more "coarse." Optional. %d by default.' % defaultRadius,
		
		'outer-box':'Defines the dimensions for the outer box or the farthest boundaries of the chunks for cropping. Cannot be called with -B/--book. By default, defined with the farthest pixels (leftmost, rightmost, topmost, bottommost); the default adapts to each unique image..',
		
		'inner-box':'Defines the dimensions for the inner box or the innermost boundaries of the chunks for cropping (the chunks essentially "surround" the inner box). Cannot be called with -B/--book. By default, defined using the outer box if an outer box was specified: each side of the inner box is %d pixels "smaller" than the outer box.' % defaultInnerBoxOffset,
		
		'book':'Defines the boundaries of the chunks for cropping with values that are relevant to the sample images the repository. The value "tripod" refers to the number of pixels from the top of the image to the part of the image with the tripod/floor (effectively a cutoff point). The value "vert" refers to the pixel WIDTH of the vertical chunks (the left chunk and the right chunk). The value "horz" refers to the pixel HEIGHT of the horizontal chunks (the top chunk and the bottom chunk). Cannot be called with either -o/--outer-box or -i/--inner-box.',
		
		'filter-enable':'Enables the outlier filtering in the cropping process. This is intended to ignore any background/red region of pixels that is highly remote or isolated from the main bodies or areas of background/red regions. Optional. Disabled by default.',
		
		'threshold':'Must be used with -f/--filter-enable. This is the maximum number of pixels that a background/red region\'s overall position can be from either the average background/red region position OR the position of the last consecutive background/red region, depending on if -S/--strict is used. Optional. %d by default.' % defaultOutlierThreshold,
		
		'strict':'Must be used with -f/--filter-enable. If used, then outliers must be within the threshold number of pixels (specified with -t/--threshold) of both the average background/red region position AND the position of the last consecutive background/red region. If not used, then only the average will be used. Optional. Disabled by default.',
		
		'force-orientation':'If used, then only either the left or right chunk will be cropped, leaving one of them unused for the cropping process. Between those two chunks, the chunk with the larger number of background/red pixel regions will be used for cropping. If not used, then BOTH the left and right chunk is used for cropping. It is RECOMMENDED to USE this flag when dealing with larger books where only the page to the left or right can be fit in frame at once, such as textbooks. Optional. Disabled by default.',
		
		'crop-margin':'This is the number of pixels by which the cropped area of the image increases in all four directions. For example, if the margin was 25 pixels, then the cropped area will have its upper bound brought up by 25 pixels, its lower bound brought down by 25 pixels, etc. This is USEFUL for when the cropping is eating into the subject of the image, such as a book page. Basically, the greater the margin, the "less cropped" the image will be. Optional. %d by default.' % defaultCropMargin,
		
		'debug-chunk-fill':'If used, then the output/written image will NOT be cropped; instead, the left, right, top, and bottom chunks will be colored in with different colors. This is USEFUL to see the overall parts of the image that will be scanned for cropping. Cannot be called with other debug flags. Optional. Disabled by default.',
		
		'debug-background-fill':'If used, then the output/written image will NOT be cropped; instead, the background/red regions will be filled with the color pink. This is USEFUL to see what is considered a part of the background/red and what is not. Cannot be called with other debug flags. Optional. Disabled by default.'
	}
	
	parser = argparse.ArgumentParser(description='Automatically crop images to the centered subject surrounded by a dark red background.')
	
	groupImage = parser.add_argument_group('images')
	groupImage.add_argument('image', type=pathlib.PosixPath, metavar='image', nargs='+', help=helpMsg['image'])
	groupImage.add_argument('-s', '--suffix', type=str, metavar='suffix', nargs=1, default=[defaultImageSuffix], help=helpMsg['suffix'])
	
	groupChunk = parser.add_argument_group('chunk management')
	groupChunk.add_argument('-r', '--radius', metavar='pixels', nargs=1, type=int, default=[defaultRadius], help=str(helpMsg['radius']))
	
	groupChunkBox = parser.add_argument_group('chunk management: box approach')
	groupChunkBox.add_argument('-o', '--outer-box', metavar=('left', 'upper', 'right', 'lower'), nargs=4, type=int, help=helpMsg['outer-box'])
	groupChunkBox.add_argument('-i', '--inner-box', metavar=('left', 'upper', 'right', 'lower'), nargs=4, type=int, help=helpMsg['inner-box'])
	
	groupChunkBook = parser.add_argument_group('chunk management: book approach')
	groupChunkBook.add_argument('-B', '--book', dest='book', metavar=('tripod', 'vert', 'horiz'), nargs=3, type=int, help=helpMsg['book'])
	
	groupOutlier = parser.add_argument_group('outlier filtering')
	groupOutlier.add_argument('-f', '--filter-enable', action='store_true', help=helpMsg['filter-enable'])
	groupOutlier.add_argument('-t', '--threshold', metavar='pixels', nargs=1, type=int, default=[defaultOutlierThreshold], help=helpMsg['threshold'])
	groupOutlier.add_argument('-S', '--strict', action='store_true', help=helpMsg['strict'])
	
	groupMisc = parser.add_argument_group('miscellaneous crop options')
	groupMisc.add_argument('-O', '--force-orientation', action='store_true', help=helpMsg['force-orientation'])
	groupMisc.add_argument('-m', '--crop-margin', metavar='pixels', nargs=1, type=int, default=[defaultCropMargin], help=helpMsg['crop-margin'])
	
	groupDebug = parser.add_argument_group('debugging')
	groupDebug.add_argument('-x', '--debug-chunk-fill', action='store_true', help=helpMsg['debug-chunk-fill'])
	groupDebug.add_argument('-y', '--debug-background-fill', action='store_true', help=helpMsg['debug-background-fill'])
	args = parser.parse_args()
	
	# even when nargs=1, a list is returned: so the single value must be retrieved from the list
	args.suffix = args.suffix[0]
	args.radius = args.radius[0]
	args.threshold = args.threshold[0]
	args.crop_margin = args.crop_margin[0]
	
	# reminder: PIL tuple box formatted as (left, upper, right, lower)
	
	if not args.filter_enable and (args.threshold != defaultOutlierThreshold or args.strict):
		parser.error('in order to change the behavior of the outlier filtering, the filter must first be enabled (-f or --filter-enable)')
	
	if args.debug_chunk_fill and args.debug_background_fill:
		parser.error('only one debug option can be used at a time')
	
	if not (args.book or args.outer_box or args.inner_box):
		parser.error('at least one of the following arguments is needed: --outer-box, --inner-box, or --book')
	
	if args.book and (args.outer_box or args.inner_box):
		parser.error('only one chunk definition type can be used (box or book)')
	
	for imagePath in args.image:
		
		# if the file exists, continue cropping; if not, send an error
		if imagePath.exists():
			imagePathStr = str(imagePath)
			
			# objects created with PIL
			imageObject = Image.open(imagePathStr)
			imageLoaded = imageObject.load()
			
			# Cropper object from primary.py
			cropper = primary.Cropper(imageObject, imageLoaded)
			
			regionRadius = args.radius
			
			# if the user wants to crop with the "book" approach
			if args.book:
				cropper.chunkSetupTextbook(*args.book, regionRadius)
			
			# if the user wants to crop with the "box" approach
			else:
				boxOuter = args.outer_box
				boxInner = args.inner_box
				
				# find the size and center of the image with 2D integer tuples
				size = imageObject.size
				center = (int(size[0] / 2), int(size[1] / 2))
				
				# these if-else blocks either convert existing arg values to tuples, OR substituting in defaults
				if boxOuter:
					boxOuter = tuple(boxOuter)
				
				else:
					boxOuter = (0, 0, size[0], size[1])
				
				if boxInner:
					boxInner = tuple(boxInner)
				
				else:
					# (safe to assume that an outer box exists)
					
					left = min(center[0] - 1, boxOuter[0] + defaultInnerBoxOffset)
					upper = min(center[1] - 1, boxOuter[1] + defaultInnerBoxOffset)
					right = max(center[0] + 1, boxOuter[2] - defaultInnerBoxOffset)
					lower = max(center[1] + 1, boxOuter[3] - defaultInnerBoxOffset)
					
					boxInner = (left, upper, right, lower)
				
				cropper.chunkSetup(boxOuter, boxInner, regionRadius)
			
			imageFinal = None
			
			# finally crop the image; or, if a debug flag enabled, do not crop and update the image with the debug information or content
			if args.debug_chunk_fill:
				cropper.chunkFillColor()
				imageFinal = imageObject
				
			elif args.debug_background_fill:
				cropper.chunkFillRedDetect(args.threshold, args.filter_enable, args.strict, args.force_orientation)
				imageFinal = imageObject
				
			else:
				imageFinal = cropper.crop(args.crop_margin, args.threshold, args.filter_enable, args.strict, args.force_orientation, False)
			
			# part 1: update the name (wipes out the extension)
			# WARNING: if there are multiple suffixes (extensions) in the file name, this **WILL** break
			# in the future this should be fixed with "suffixes" (list of suffixes) and using "stem" until reaching the true stem
			imagePathNew = imagePath.with_name('%s%s' % (imagePath.stem, args.suffix))
			
			# part 2: put the extension back
			# (in pathlib, the suffix refers to the file extension)
			imagePathNew = imagePathNew.with_suffix(imagePath.suffix)
			
			# part 3: actually write the file
			imageFinal.save(imagePathNew)
			
		else:
			parser.error('no file exists at path %s' % str(imagePath))

def main():
	commandParse()

if __name__ == '__main__':
	main()
