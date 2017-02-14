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

def CommA(A,community_pool,total_edge):
	comm_num=len(community_pool)
	CA=np.zeros((comm_num,comm_num))
	for i in range(comm_num):
		for j in range(i,comm_num):
			if i==j:
				CA[i,i]=edge_ii(A,community_pool[i],total_edge)
			else:
				CA[i,j]=0.5*edge_ij(A,community_pool[i],community_pool[j],total_edge)
				CA[j,i]=CA[i,j]
	return CA


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
		for j in range(i+1,row):
			if CA[i,j]>0:
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
	CA[best_pair[0],:]=CA[best_pair[0],:]+CA[best_pair[1],:]
	CA[:,best_pair[0]]=CA[:,best_pair[0]]+CA[:,best_pair[1]]
	CA=np.delete( CA,(best_pair[1]),axis=0 )
	CA=np.delete( CA,(best_pair[1]),axis=1 )
	return CA


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
		print "Loading GN Benchmark Dataset... ",
		A=np.array(benchmark.gn(project_location))
		GN_CHOSEN=True
		print "OK"
	elif "-KARATE" in arg_list:
		print "Loading KARATE Dataset... ",
		A=np.array(benchmark.karate_club())
		print "OK"
	elif "-FOOTBALL" in arg_list:
		print "Loading FOOTBALL Dataset... ",
		A=np.array(benchmark.football())
		print "OK"
	elif "-DOLPHIN" in arg_list:
		print "Loading DOLPHIN Dataset... ",
		A=np.array(benchmark.dolphin())
		print "OK"
	elif "-TEST" in arg_list:
		print "Loading TEST Dataset... ",
		A=np.array(benchmark.TEST)
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

	print "Initializing Communities... ",
	curr_community_pool=initialize(A)
	community_pool=copy.deepcopy( curr_community_pool )

	CA=CommA(A,curr_community_pool,total_edge)
	curr_Q=calc_init_Q(CA)
	Q=curr_Q
	print "OK"

	print "Entering Main Loop... OK"
	print "Time Remains Untill End of the Core Algorithm: ... "
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
		print "Performance Evaluation in progress... ",
		performance_message=performance.performance_evaluation(community_pool,project_location)
		print "OK"
	t_end_perf=time.time()

	print "Calculating Statistics... OK"
	summary.print_statistics(t_start_algo,t_end_algo,t_start_perf,t_end_perf,Q,community_pool,performance_message)


	if NO_DRAW==True:
		sys.exit()

	print "Please wait for the graphs... OK"
	draw.draw_graph_adj(A,seed)
	draw.draw_graph_comm(A,community_pool,seed)
	draw.plot_Q(val_curr_Q,size_curr_community_pool)


