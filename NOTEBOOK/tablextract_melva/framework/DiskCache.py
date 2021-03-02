# DiskCache.py

import os
import pickle
import hashlib
import shutil

from filelock import FileLock


class DiskCache:

	# Constructor -------------------------------------------------------------

	FOLDER = os.environ["CACHE_FOLDER"] if "CACHE_FOLDER" in os.environ else "./workarea/cache"

	@staticmethod
	def initialise(name=None):
		shutil.rmtree(DiskCache.FOLDER, ignore_errors=True)
		os.makedirs(DiskCache.FOLDER, exist_ok=True)

	def __init__(self):
		pass

	# Business methods --------------------------------------------------------

	def hash_key(self, key):
		if isinstance(key, str):
			bytes = key.encode()
		else:
			bytes = pickle.dumps(key)

		result = hashlib.md5(bytes).hexdigest()

		return result

	def contains(self, key):
		filename = f"{DiskCache.FOLDER}/{hash}.pk"
		result = os.path.exists(filename)

		return result

	def get(self, key):
		hash = key.hash()
		filename = f"{DiskCache.FOLDER}/{hash}.pk"
		lockname = f"{DiskCache.FOLDER}/{hash}.lock"
		hit = os.path.exists(filename)
		if hit:
			with FileLock(lockname) as lock:
				with open(filename, "rb") as file:
					value = pickle.load(file)
		else:
			value = None

		result = (hit, value)

		return result

	def put(self, key, value):
		hash = key.hash()
		filename = f"{DiskCache.FOLDER}/{hash}.pk"
		lockname = f"{DiskCache.FOLDER}/{hash}.lock"
		with FileLock(lockname) as lock:
			with open(filename, "wb") as file:
				pickle.dump(value, file)

	# Ancillary methods -------------------------------------------------------
