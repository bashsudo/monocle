# main functionality and parameters
* debug:
	* filling chunks with color
	* indicating red regions with pink
* cropping:
	* setting box:
		* "textbook" approach
		* generic outer-inner approach
		(default: use "textbook" approach with hardcoded integers if neither provided)
		(when either approach is provided, not both, they NEED argument values)
	* main behavior:
		* FUNC: filter bound outliers
			* FUNC: outlier threshold
			* FUNC: strict outlier filter
		* FUNC: force orientation
		* FUNC: crop margin pixels

(only tested with LINUX, not WINDOWS; especially with the paths; using POSIX path, not Windows path in pathlib)
