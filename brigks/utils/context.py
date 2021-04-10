import contextlib

from maya import cmds

@contextlib.contextmanager
def selection(*args, **kwargs):
	"""A context manager that resets selections after exiting.

	Args:
		args: Passed to ``cmds.select``.
		kwargs: Passed to ``cmds.select``.

	A list of the original selection will be bound to the target of the with
	statement. Changes to that list will be applied.

	Example::

		>>> with selection(clear=True):
		...     # Do something with an empty selection, but restore the user's
		...     # selection when we are done.

	"""
	existing = cmds.ls(selection=True, long=True) or []
	try:
		if args or kwargs:
			cmds.select(*args, **kwargs)
		yield existing
	finally:
		if existing:
			existing = [x for x in existing if cmds.objExists(x)]
			cmds.select(existing, replace=True)
		else:
			cmds.select(clear=True)


class undoChunk(object):
	 def __init__(self, name="", raise_error=True):
			 self.raise_error = raise_error
			 self.name = name

	 def __enter__(self):
			 cmds.undoInfo(openChunk=True, chunkName=self.name)
			 cmds.waitCursor(state=True)
			 cmds.refresh(suspend =True)

	 def __exit__(self, exc_type, exc_val, exc_tb):
			 """ Turn refresh on again and raise errors if asked """
			 cmds.refresh(suspend =False)
			 cmds.refresh()
			 cmds.waitCursor(state=False)
			 cmds.undoInfo(closeChunk=True)
			 if exc_type is not None:
					 if self.raise_error:
							 import traceback
							 traceback.print_tb(exc_tb)
							 raise exc_type, exc_val
					 else:
							 sys.stderr.write("%s" % exc_val)

# ----------------------------------------------------------------------------------
# DECORATOR
# ----------------------------------------------------------------------------------
def command(resetSelection=True):
	def wrapper(func):
		name = func.__name__
		@wraps(func)
		def decorator(*args, **kwargs):
			ts = datetime.datetime.now()

			if resetSelection:
				with selection():
					with undoChunk(name):
						result = func(*args, **kwargs)
			else:
				with undoChunk(name):
					result = func(*args, **kwargs)

			te = datetime.datetime.now()
			print '%s [%s]' % (name, te-ts)
			return result 
		return decorator
	return wrapper
