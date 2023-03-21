import os
import sys

sys.stdout.write(".".join(os.environ['API_DOMAIN'].split(".")[1:]))
