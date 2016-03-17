from distutils.core import setup  
import py2exe  
import sys  
includes = ["encodings", "encodings.*"]  
sys.argv.append("py2exe")  
options = {"py2exe":   { "compressed": True, "bundle_files": 1 }}  
setup(options = options,        
      zipfile=None,  
      console = [{"script":'main.py', 'icon_resources':[(1, 'image/redis.ico')]}])
