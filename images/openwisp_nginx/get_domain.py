import os
import sys

import tldextract

ext = tldextract.extract(os.environ['API_DOMAIN'])
sys.stdout.write(ext.registered_domain)
