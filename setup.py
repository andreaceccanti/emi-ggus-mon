
'''
Created on 30/ago/2011

@author: andreaceccanti
'''
from distutils.core import setup
import sys
sys.path.insert(0,"src")

from emi_ggus_mon import __version__

setup(name='cnaf_mon',
      version=__version__,
      author="Andrea Ceccanti",
      author_email="andrea.ceccanti@cnaf.infn.it",
      maintainer="Andrea Ceccanti",
      maintainer_email="andrea.ceccanti@cnaf.infn.it",
      description="A python script to monitor EMI support performance",
      license="Apache Software License",
      package_dir={'':'src'},
      packages=['emi_ggus_mon'],
      scripts=['src/cnaf.py'])
