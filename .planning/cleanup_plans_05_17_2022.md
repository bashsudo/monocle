5-17-2022

* the overall phases to use when cleaning up and refactoring my code:
	1. try to separate the one huge "processor.py" into multiple files/modules
		* try to have THREE main modules:
			* the "primary" module (has EVERYTHING integral to the cropping -- all the classes and important global fucntions)
			* the "interface" module (how a user can actually interface with the program via CLI)
			* the "testing" module (filled with "junky" code that roughly tests the primary module)
	2. properly document the CURRENT process of how each class and global function generally operates
		* this way, we can identify inefficiencies in the behavior of the code and the assumptions we make about the code
		* we want to NARROW our assumptions to where we can have EFFICIENT CODE that will NOT break or be IMPROPERLY IMPLEMENTED
			* e.g. reduce as many "recalculations" as possible
	3. implement a NEW, EFFICIENT version of the primary module with the new plans
		* CONSIDER using a VERSION NUMBERING SYSTEM
		* the ORIGINAL PRIMARY MODULE will be v1.X.X
		* the NEW PRIMARY MODULE will be v2.X.X
		* then 3.X.X, 4.X.X, and so on as we make radical changes
