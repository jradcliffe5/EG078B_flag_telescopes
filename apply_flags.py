import os, re, time, datetime, sys, math, fnmatch
from os.path import join, getsize
from datetime import date
from collections import deque
import Utilities
#from multiprocessing import Process	# No longer needed now SERPent is parallel
#from multiprocessing import Pool
from AIPS import AIPS, AIPSDisk
from AIPSTask import AIPSTask, AIPSList
from AIPSData import AIPSUVData, AIPSImage, AIPSCat
from Wizardry.AIPSData import AIPSUVData as WizAIPSUVData
import math, time, datetime
from numpy import *
import itertools
from time import gmtime, strftime, localtime
import numpy as np
ti = time.time()    # To time the script

#### Inputs ####
AIPS.userno = 998
UVFITSFILESpath = './'
### Load the array that says what source are within the beams
EF_pointings = np.load('Effelsberg_flagging_table.npy')
LO_pointings = np.load('Lovell_flagging_table.npy')
###


def flag_data(uvdata,telescope,flag_file):
	pointing_names = ['P1','P2','P3','P4','HDFN']
	for i in range(len(flag_file[0])):
		if flag_file[0][i][:8] == uvdata.name:
			print flag_file[0][i][:8]
			for j in pointing_names:
					print j
					print np.any(flag_file[4,i] == j)
					if np.any(flag_file[4,i] == j):
						print ''
					else:
						uvflg = AIPSTask('UVFLG')
						uvflg.indata = uvdata
						uvflg.opcode = 'FLAG'
						uvflg.intext = 'PWD:%s_%s.txt' % (telescope,j)
						uvflg.go()


for file in os.listdir(UVFITSFILESpath):
    if file.endswith('.UV'):
		os.system('rsync -ar --progress %s%s ./' % (UVFITSFILESpath,file))
		for i in range(len(EF_pointings[0])):
				if EF_pointings[0][i][:8] == file[:8]:
					fitld = AIPSTask('FITLD')
					fitld.datain = 'PWD:%s' % file
					fitld.digicor = -1
					fitld.go()
					uvdata = AIPSUVData(file[:8],'MULTI',1,1)
					flag_data(uvdata,telescope='Ef',flag_file=EF_pointings)
					flag_data(uvdata,telescope='Lo',flag_file=LO_pointings)
					imagr = AIPSTask('IMAGR')
					imagr.indata = uvdata
					imagr.sources[1] = file[:8]
					imagr.cellsize[1:] = 0.001, 0.001
					imagr.imsize[1:] = 2048,2048
					imagr.nchav = 32
					imagr.niter = 100
					imagr.docalib = 2
					imagr.go()
					imagr.uvwtfn = 'NA'
					imagr.go()
					image1 = AIPSImage(file[:8],'ICL001',1,1)
					image2 = AIPSImage(file[:8],'ICL001',1,2)
					fittp = AIPSTask('FITTP')
					fittp.indata = uvdata
					fittp.dataout = 'PWD:%s_FG.UV' % file[:-3]
					fittp.go()
					fittp.indata = image1
					fittp.dataout = 'PWD:%s_FG_IM.fits' % file[:-3]
					fittp.go()
					fittp.indata = image2
					fittp.dataout = 'PWD:%s_FG_NA_IM.fits' % file[:-3]
					fittp.go()
					image1.zap()
					image2.zap()
					uvdata.zap()
					AIPSImage(file[:8],'IBM001',1,1).zap()
					AIPSImage(file[:8],'IBM001',1,1).zap()
