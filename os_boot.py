import os
import os.path
import sys

os.popen("ndndstop")
os.popen("ndndstart")

dirpath = os.path.dirname(__file__)
print dirpath
propath = os.path.join(dirpath, "producer.py")
os.popen("python %s" %(propath))
