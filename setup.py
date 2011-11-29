
'''
Created on 30/ago/2011

@author: andreaceccanti
'''
from distutils.core import setup

setup(name='emi_ggus_mon',
      version="0.4",
      author="Andrea Ceccanti",
      author_email="andrea.ceccanti@cnaf.infn.it",
      maintainer="Andrea Ceccanti",
      maintainer_email="andrea.ceccanti@cnaf.infn.it",
      description="A python script to monitor EMI support performance",
      license="Apache Software License",
      package_dir={'':'src'},
      packages=['emi_ggus_mon'],
      scripts=['src/ggus.py'])
      
      
      