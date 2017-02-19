import igraph
import numpy as np
import sys
import copy
import benchmark
import time
import random
import draw
import performance
import summary
import ETA


seed=random.randint(1,1000)
random.seed(seed)


class Community():
	def __init__(self):
		self.members=[]
		self.color=( random.uniform(0.3,0.9) , random.uniform(0.3,0.9) , random.uniform(0.3,0.9) ) 


def initialize(A):
	(row,col)=A.shape
	community_pool=[]
	for member in range(row):
		community=Community()
		community.members.append(member)
		community_pool.append(community)
	return community_pool

def edge_ij(A,thiscomm, othercomm,total_edge):
	B=A[thiscomm.members,:]
	C=B[:,othercomm.members]
	return float(np.sum(C))/total_edge

def edge_ii(A,thiscomm,total_edge):
	B=A[thiscomm.members,:]
	C=B[:,thiscomm.members]
	return 0.5*float(np.sum(C))/total_edge


def calc_init_Q(CA):
	Q=np.matrix.trace(CA)-np.sum( (np.sum(CA,axis=1))**2 )
	return Q

def calc_dQ(CA,i,j):
	dQ=2*( CA[i,j] - np.sum(CA[i,:])*np.sum(CA[j,:]) )
	return dQ


def find_best_pair(CA):
	best_pair=[]
	best_dQ=-1e1000000
	(row,col)=CA.shape
	can_merge=False

	for i in range(row):
		check_this=np.where(CA[i,i+1:col]>0)[0]
		for newj in range(len(check_this)):
			j=check_this[newj]+i+1
			dQ=calc_dQ(CA,i,j)
			if dQ>best_dQ:
				best_dQ=dQ
				best_pair=[i,j]
				can_merge=True


	if can_merge==False:
		sys.exit( "There is no any possible merge. Hit the Isolated Communities. SYSTEM EXIT!"  )
	return (best_pair,best_dQ)

def update_community_pool(community_pool,best_pair):
	community_pool[best_pair[0]].members=community_pool[best_pair[0]].members+community_pool[best_pair[1]].members
	del community_pool[best_pair[1]]
	return community_pool

def update_CA(CA,best_pair):
	(row,col)=CA.shape
	delete_index=best_pair[1]
	CA[best_pair[0],:]=CA[best_pair[0],:]+CA[best_pair[1],:]
	CA[:,best_pair[0]]=CA[:,best_pair[0]]+CA[:,best_pair[1]]

	mask=np.ones(CA.shape, dtype=np.bool)
	mask[delete_index]=False
	mask.T[delete_index]=False

	return CA[mask].reshape((row-1,col-1))


def extract_project_location():
	with open("project.location") as f:
		location=f.readline().strip()
	return location


if __name__=="__main__":

	project_location=extract_project_location()

	arg_list=[]
	GN_CHOSEN=False
	NO_DRAW=False

	for arg in sys.argv:
		arg_list.append(arg.upper())

	if "-GN" in arg_list:
		print "Loading GN Benchmark Dataset... "
		A=benchmark.gn(project_location)
		GN_CHOSEN=True
		print "OK"
	elif "-KARATE" in arg_list:
		print "Loading KARATE Dataset... "
		A=benchmark.karate_club()
		print "OK"
	elif "-FOOTBALL" in arg_list:
		print "Loading FOOTBALL Dataset... "
		A=benchmark.football()
		print "OK"
	elif "-DOLPHIN" in arg_list:
		print "Loading DOLPHIN Dataset... "
		A=benchmark.dolphin()
		print "OK"
	elif "-ARXIVHEPTH" in arg_list:
		print "Loading ARXIVHEPTH Dataset... "
		A=benchmark.arxivhepth()
		print "OK"
	elif "-TEST" in arg_list:
		print "Loading TEST Dataset... "
		A=benchmark.TEST
		print "OK"
	else:
		print "Loading GN Benchmark Dataset... ",
		A=np.array(benchmark.gn(project_location))
		GN_CHOSEN=True
		print "OK"

	if "-NODRAW" in arg_list:
		NO_DRAW=True

	total_edge=np.sum(A)/2

	t_start_algo=time.time()

	print "Initializing Communities... "
	curr_community_pool=initialize(A)
	community_pool=copy.deepcopy( curr_community_pool )
	
	CA=0.5*A/total_edge
	curr_Q=calc_init_Q(CA)
	Q=curr_Q
	print "OK"

	print "Entering Main Loop."
	print "Time Remains Untill End of the Core Algorithm:... "
	time_list=[]
	total_task_size=len(CA)
	val_curr_Q=[]
	size_curr_community_pool=[]
	val_curr_Q.append(curr_Q)
	size_curr_community_pool.append(len(curr_community_pool))


	while len(CA)>1:

		t_start_loop=time.time()

		(best_pair,best_dQ)=find_best_pair(CA)

		CA=update_CA(CA,best_pair)
		curr_community_pool=update_community_pool(curr_community_pool,best_pair)
		curr_Q=curr_Q+best_dQ

		if curr_Q>Q:
			del community_pool
			community_pool=copy.deepcopy(curr_community_pool)
			Q=curr_Q

		t_end_loop=time.time()
		val_curr_Q.append(curr_Q)
		size_curr_community_pool.append(len(curr_community_pool))
		eta=ETA.calculate_remaining_time(total_task_size,CA,t_start_loop,t_end_loop,time_list)
		print "%.4f minutes..." %eta,
		tab=random.randint(11,17)
		print tab*"\t","+"


	print "Core Algorithm: Done\n"

	t_end_algo=time.time()

	t_start_perf=time.time()
	performance_message="Performance Evaluation is only available for GN Benchmark Datasets."
	if GN_CHOSEN==True:
		print "Performance Evaluation in progress... "
		performance_message=performance.performance_evaluation(community_pool,project_location)
		print "OK"
	t_end_perf=time.time()

	print "Calculating Statistics."
	summary.print_statistics(t_start_algo,t_end_algo,t_start_perf,t_end_perf,Q,community_pool,performance_message)


	if NO_DRAW==True:
		sys.exit()

	print "Please wait for the graphs."
	draw.draw_graph_adj(A,seed)
	draw.draw_graph_comm(A,community_pool,seed)
	draw.plot_Q(val_curr_Q,size_curr_community_pool)


