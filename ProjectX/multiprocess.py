import numpy as np
import multiprocessing, Queue
import sys
import time

def multiprocess(func,func_args,cpu):
	return_list=[]
	ret=multiprocessing.Queue()
	task=len( func_args[0] )
	if task>cpu:
		chunk_num=cpu
	else:
		chunk_num=1

	chunk_size=task/chunk_num

	chunks=[]

	start=0
	end=chunk_size

	for i in range( chunk_num-1 ):
		chunk=( start,end-1 )
		chunks.append(chunk)
		start=start+chunk_size
		end=end+chunk_size

	chunks.append( (start,task-1) )

	pool=[]
	for i in range(chunk_num):
		p=multiprocessing.Process( target=func, args=func_args+ (ret,) +(chunks[i],) )
		pool.append(p)
		p.start()


	for proc in pool:
		proc.join()

	for i in range(chunk_num):
		return_list.append(ret.get())


	return return_list


def handle_mproc(arg_list):
	global MPROC
	cpu=1
	CPU_NUM_DEFINED=False
	for arg in arg_list:
		if arg.isdigit():
			cpu_requested=int(arg)
			CPU_NUM_DEFINED=True
	if CPU_NUM_DEFINED==False:
		sys.exit("Please refine your request. e.g. -mproc PositiveInteger")

	max_cpu=multiprocessing.cpu_count()

	if cpu_requested<=0:
		sys,exit("Please define your cpu number properly. e.g. -mproc PositiveInteger")
	elif cpu_requested==1:
		print "Multiprocessing is not available for 1 cpu. Default(single cpu) mode is chosen. " 
		MPROC=False
	elif cpu_requested>max_cpu:
		print "Your machine has only %d cpu(s)." %(max_cpu)
		print "Please request less or equal of your maximum cpu number.\nCRITICAL: Using all of your cpu power is dangerous. Use at your own risk!!"
		sys.exit()
	elif cpu_requested==max_cpu:
		print "You are using %d/%d of your cpu(s)." %(cpu_requested,max_cpu)
		print "CRITICAL: Using all of your cpu power is dangerous. Use at your own risk!! You can Press CTRL+C to stop..."
		time.sleep(7)
		MPROC=True
		cpu=cpu_requested
	else:
		print "You are using %d/%d of your cpu(s)." %(cpu_requested,max_cpu)
		MPROC=True
		cpu=cpu_requested

	return (MPROC,cpu)

def handle_find_best_pair(return_find_best_pair_mproc):
	best_dQ=-1e1000000
	for i in range(len(return_find_best_pair_mproc)):
		if return_find_best_pair_mproc[i][1]>best_dQ:
			best_dQ=return_find_best_pair_mproc[i][1]
			best_pair=return_find_best_pair_mproc[i][0]
	if best_dQ==-1e1000000:
		sys.exit( "There is no any possible merge. Hit the Isolated Communities. SYSTEM EXIT!"  )
	return (best_pair,best_dQ) 

