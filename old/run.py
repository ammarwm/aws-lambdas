import sys
import os
working_directory = os.path.dirname(os.path.realpath(__file__))
if 'linux' in sys.platform:
    sys.path.append(working_directory)
