import sys
import time

print("1. Importing core framework...")
import my_framework

print("   [Check] Is extension loaded in sys.modules?", "my_framework_ext" in sys.modules)

print("\n2. Doing core work (no extension needed)...")
# time.sleep(1) 

print("\n3. Accessing extension for the first time...")
# This triggers __getattr__ -> imports my_framework_ext
tool = my_framework.ext.SuperTool()

print("   [Check] Is extension loaded in sys.modules?", "my_framework_ext" in sys.modules)

print(f"\n4. Result: {tool.run()}")
