import sys
import pdb


def _stdin_is_tty():
	try:
		return bool(sys.stdin.isatty())
	except Exception:
		return False


def _logger():
	try:
		return system.util.getLogger("utils.debug")
	except Exception:
		return None


def brk():
	# Drop into pdb when a tty is attached; otherwise log and return.
	if _stdin_is_tty():
		pdb.Pdb().set_trace(sys._getframe().f_back)
		return
	log = _logger()
	if log is not None:
		log.warn("utils.debug.brk() called without a tty - skipping pdb prompt")


def post_mortem():
	if _stdin_is_tty():
		pdb.post_mortem()
		return
	log = _logger()
	if log is not None:
		log.warn("utils.debug.post_mortem() called without a tty - skipping pdb prompt")
