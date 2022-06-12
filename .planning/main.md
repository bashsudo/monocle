5/11/2022

# Major Parts of Image
* the red shirt under the yearbook
	* PURPOSE: helps this program identify the boundaries of the yearbook
	* varying shades and darkness/lightness of red
		* the program will need to be able to identify the red region despite its varying levels of intensity (i.e. the lighter and darker reds)
* the boundaries of the yearbook
* the spine of the yearbook (the edge where both pages meet)
	* notice how all the colors, regardless of WHAT the colors are (e.g. red, green, yellow, etc.), get darker as they approach the spine
		* the page is very bent and warped at the spine
		* the actual edge is the local minimum of the color values (i.e. the darkest point of all the colors)

# General Techniques
* scanning by chunks/regions:
	* instead of looking at pixels individually, the program will start by looking at far-apart pixels (e.g. every 10th, 20th, or 30th pixel, etc.) and focus on each pxiel's surrounding pixels within a radius
	* the program will initially make a coarse, rough judgement of a part of the image with VERY far-apart pixels (MAYBE 50-100 pixels) with a larger radius (MAYBE 10-25 pixels, 20-50 diameter)
	* then, as it locates roughly what it is looking for...
		* within the coarse region with the items of interest, it will probe with LESS FAR-APART pixels with a SMALLER RADIUS
		* it will do this over and over until it meets the level of precision it needs

# Process of processing image
1. get rid of bottom half of image that does not incldue the red shirt
2. determine the boundaries of the book
3. determine where the spine of the book is (shared edge of both visible pages)

(MOER SHOULD BE ADDED HERE)
