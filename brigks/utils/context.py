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