#!/bin/csh
# ---------------------------------------------
# Set up path to BNN software
# ---------------------------------------------
# change to location of your fbm installation
setenv BNNPATH `pwd`/fbm.2004-11-10

setenv PATH `pwd`/bin:${BNNPATH}/bin:${PATH}

setenv PYTHONPATH `pwd`/python:$PYTHONPATH
