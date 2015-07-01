"""
Measures elapsed wall-clock time of a program and sub-tasks.
"""
from time import time

class ProgramTimer:
	"""Measure elapsed wall-clock time of a program and its sub-tasks."""
	def __init__(self):
		"""Initialize program start and task start to current time."""
		self.program_start_time = time()
		self.task_start_time = time()
	def start(self):
		"""Set task start time to current time"""
		self.task_start_time = time()
	def stop(self):
		"""Return seconds elapsed between current time and task start time and restarts task timer."""
		elapsed = time() - self.task_start_time
		self.start()
		return elapsed
		
	def end(self):
		"""Return seconds elapsed between current time and program start time."""
		return time() - self.program_start_time
