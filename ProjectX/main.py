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
import multiprocess

seed=random.randint(1,2000)
random.seed(seed)

label=-1

class Community():
	def __init__(self):
		self.label=self.assign_label()
		self.members=[]
		self.color=( random.uniform(0.3,0.9) , random.uniform(0.3,0.9) , random.uniform(0.3,0.9) ) 
	def assign_label(self):
		global label
		label=label+1
		return label


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


def find_candidate_pairs(CA):
	(i_array,j_array)=np.where(CA>0)
	mask=(j_array-i_array)>0
	i_array=i_array[mask]
	j_array=j_array[mask]
	return (i_array,j_array)

def find_best_pair(candidate_pairs,CA):
	best_pair=[]
	best_dQ=-1e1000000
	can_merge=False
	(i_array,j_array)=candidate_pairs


	for element in range(len(i_array)):
		i=i_array[element]
		j=j_array[element]
		dQ=calc_dQ(CA,i,j)
		if dQ>best_dQ:
			best_dQ=dQ
			best_pair=[i,j]
			can_merge=True

	if can_merge==False:
		sys.exit( "There is no any possible merge. Hit the Isolated Communities. SYSTEM EXIT!"  )
	return (best_pair,best_dQ)

def find_best_pair_mproc(candidate_pairs,CA,ret,index_range):
	best_pair=[]
	best_dQ=-1e1000000
	can_merge=False
	start_index=index_range[0]
	end_index=index_range[1]
	(i_array,j_array)=candidate_pairs


	for element in range(start_index,end_index+1):
		i=i_array[element]
		j=j_array[element]
		dQ=calc_dQ(CA,i,j)
		if dQ>best_dQ:
			best_dQ=dQ
			best_pair=[i,j]
			can_merge=True

	if can_merge==False:
		best_dQ=-1e1000000
		best_pair=[-999,-999]
	ret.put( (best_pair,best_dQ) )



def update_community_pool(community_pool,best_pair):
	community_pool[best_pair[0]].members=community_pool[best_pair[0]].members+community_pool[best_pair[1]].members
	del community_pool[best_pair[1]]
	return community_pool

def update_CA(CA,best_pair):
	(row,col)=CA.shape
	delete_index=best_pair[1]

	row_index_to_update=np.where( CA[ best_pair[1] ]>0  ) 
	CA[best_pair[0],row_index_to_update]=CA[best_pair[0],row_index_to_update]+CA[best_pair[1],row_index_to_update]
	col_index_to_update=np.where( CA.T[ best_pair[1] ]>0  )
	CA[col_index_to_update,best_pair[0]]=CA[col_index_to_update,best_pair[0]]+CA[col_index_to_update,best_pair[1]]


	mask=np.ones(CA.shape, dtype=np.bool)
	mask[delete_index]=False
	mask.T[delete_index]=False

	return CA[mask].reshape((row-1,col-1))



def build_community_pool_from_joins(filename,Qmax):
	global label
	label=-1
	community_pool=[]
	d={}
	string_float=str(Qmax)
	Qmax=float(string_float)

	with open(filename,"r") as file:
		line=file.readline().strip()
		while line.split()[0] !="END":
			[key,value,Q]=line.split()
			key=int(key)
			value=int(value)
			Q=float(Q)

			if Q<=Qmax:
				if key not in d.keys():
					if value not in d.keys():
						d[key]=[key,value]
					elif value in d.keys():
						d[key]=[key]+d[value]
						del d[value]
				elif key in d.keys():
					if value not in d.keys():
						d[key]=d[key]+[value]
					elif value in d.keys():
						d[key]=d[key]+d[value]
						del d[value]

			if Q==Qmax:
				break
			line=file.readline().strip()
				
	for key in d.keys():
		community=Community()
		community.members=list(set(d[key]))
		community_pool.append(community)
	label=-1
	return community_pool



def dir_to_undir_A(dir_A):
	A=dir_A+dir_A.T
	return A


def intro(arg_list, GN_CHOSEN, JSON_CHOSEN, NO_DRAW, NO_PERF):

	MPROC=False
	cpu=1


	for arg in sys.argv:
		arg_list.append(arg.upper())

	if "-MPROC" in arg_list:
		(MPROC,cpu)=multiprocess.handle_mproc(arg_list)

	if "-GN" in arg_list:
		print "Loading GN Benchmark Dataset... "
		A=benchmark.gn()
		dir_A=None
		GN_CHOSEN=True
		print "OK"
	elif "-KARATE" in arg_list:
		print "Loading KARATE Dataset... "
		A=benchmark.karate_club()
		dir_A=None
		print "OK"
	elif "-FOOTBALL" in arg_list:
		print "Loading FOOTBALL Dataset... "
		A=benchmark.football()
		dir_A=None
		print "OK"
	elif "-DOLPHIN" in arg_list:
		print "Loading DOLPHIN Dataset... "
		A=benchmark.dolphin()
		dir_A=None
		print "OK"
	elif "-ARXIVHEPTH" in arg_list:
		print "Loading ARXIVHEPTH Dataset... "
		A=benchmark.arxivhepth()
		dir_A=None
		print "OK"
	elif "-TEST" in arg_list:
		print "Loading TEST Dataset... "
		A=benchmark.TEST
		dir_A=None
		print "OK"
	elif "-JSON" in arg_list:
		print "Loading Paper Dataset [data.json <- created by dirnetgen.py]... "

		for position,arg in enumerate(arg_list):
			if arg=="-JSON":
				json_file_size=int(arg_list[position+1])

		dir_A=benchmark.parse_json_create_dir_A("data.json", json_file_size) # 500 [0...499] is the total paper number in the data.json, you need to know it beforehand
		print "OK"
		print "Converting to undirected data... "
		A=dir_to_undir_A(dir_A)
		JSON_CHOSEN=True
		print "OK"


	if "-NODRAW" in arg_list:
		NO_DRAW=True

	if "-NOPERF" in arg_list:
		NO_PERF=True


	if JSON_CHOSEN==False:
		summary.data_characteristics(A)
		print "\n"
	elif JSON_CHOSEN==True:
		summary.dir_data_characteristics(dir_A)
		print "\n"

	return (A, dir_A, GN_CHOSEN, JSON_CHOSEN, NO_DRAW, NO_PERF, MPROC,cpu)




def run_community_detection(A,MPROC,cpu):

	total_edge=np.sum(A)/2
	print "Initializing Communities... "
	curr_community_pool=initialize(A)
	print "OK"
	CA=0.5*A/total_edge
	print "Calculating Initial Q..."
	curr_Q=calc_init_Q(CA)
	Q=curr_Q
	print "OK"


	val_curr_Q=[] #PLot Q
	size_curr_community_pool=[] #Plot Q
	val_curr_Q.append(curr_Q) #PLot Q
	size_curr_community_pool.append(len(curr_community_pool)) #Plot_Q

	file_joins=open("joins.txt","w")

	print "Entering Main Loop.\n"
	t_start_algo=time.time()

	while len(CA)>1:

		t_start_loop=time.time()
		print "--------------------"
		print "Finding Best Pair..."
		if MPROC==True:
			candidate_pairs=find_candidate_pairs(CA)
			return_find_best_pair_mproc=multiprocess.multiprocess_best_pair( find_best_pair_mproc,(candidate_pairs,CA),cpu )
			(best_pair,best_dQ)=multiprocess.handle_return_find_best_pair(return_find_best_pair_mproc)
		elif MPROC==False:
			candidate_pairs=find_candidate_pairs(CA)
			(best_pair,best_dQ)=find_best_pair(candidate_pairs,CA)
		print "OK"
		curr_Q=curr_Q+best_dQ

		content_joins=str( curr_community_pool[ best_pair[0] ].label )+"\t"+str( curr_community_pool[ best_pair[1] ].label )+"\t"+str(curr_Q)+"\n"
		file_joins.write(content_joins)

		print "Updating CA matrix..."
		CA=update_CA(CA,best_pair)
		print "OK"
		print "Updating community pool..."
		curr_community_pool=update_community_pool(curr_community_pool,best_pair)
		print "OK"

		if curr_Q>Q:
			Q=curr_Q

		t_end_loop=time.time()

		val_curr_Q.append(curr_Q)
		size_curr_community_pool.append(len(curr_community_pool))
		eta= ETA.calculate_remaining_time(CA, len(candidate_pairs[0]),t_start_loop,t_end_loop)
		print "Time remaining: %.6f minutes..." %eta,
		tab=random.randint(11,17)
		print tab*"\t","+"
		print "---------------------\n"
	file_joins.write("END")
	file_joins.close()

	print "---------------------"
	print "Core Algorithm: Done"
	print "---------------------\n"
	t_end_algo=time.time()

	print "Building Community pool from joins.txt..."
	community_pool=build_community_pool_from_joins("joins.txt",Q)
	print "OK"

	return (community_pool, Q, val_curr_Q, size_curr_community_pool, t_start_algo, t_end_algo)


def handle_performance( GN_CHOSEN, JSON_CHOSEN, community_pool):
	global NO_PERF
	if NO_PERF==False:
		performance_message="Performance Evaluation is only available for PAPER [DATA.JSON] and GN Benchmark Datasets."
		if GN_CHOSEN==True or JSON_CHOSEN==True:
			print "Performance Evaluation in progress... "
			performance_message=performance.performance_evaluation(community_pool,JSON_CHOSEN)
			NO_PERF=True
			print "OK"
	
	elif NO_PERF==True:
		performance_message="Performance Evaluation is disabled by -NOPERF argument either by the user or algorithm.\nNote: Performance Evaluation is only available for the first round."
	
	return performance_message

def handle_data_characteristics(dir_A,A,JSON_CHOSEN):

	if JSON_CHOSEN==False:
		summary.data_characteristics(A)
	elif JSON_CHOSEN==True:
		summary.dir_data_characteristics(dir_A)

	

def handle_draw(NO_DRAW, JSON_CHOSEN, dir_A, A, community_pool, val_curr_Q, size_curr_community_pool,draw_seed):

	if NO_DRAW==False:

		print "Please wait for the graphs."

		if JSON_CHOSEN==False:
			draw.draw_graph_adj(A,draw_seed)
			draw.draw_graph_comm(A,community_pool,draw_seed)
			draw.plot_Q(val_curr_Q,size_curr_community_pool)
		elif JSON_CHOSEN==True:
			draw.draw_graph_dir_adj(dir_A,draw_seed)
			draw.draw_graph_dir_comm(dir_A,community_pool,draw_seed)
			draw.plot_Q(val_curr_Q,size_curr_community_pool)	

# calculates page ranks of vertices in the given graph: AdjMat, returns the list of pageranks.
def calculate_pageranks(AdjMat):

	# convert AdjMat to igraph object, we should avoid such conversions, it is only for testing purposes. In future we consider implementing Igraph stuff ourselves
	baseGraph=Graph()
	baseGraph.add_vertices(len(AdjMat))

	for i in range(len(AdjMat)):
		for j in range(len(AdjMat)):
			if AdjMat[i][j]>0: # graph is possibly weighted
				baseGraph.add_edge(i,j,weight=AdjMat[i][j])

	
	pageranks=baseGraph.pagerank(weights='weight')
	pageranks = np.array(pageranks)
	return pageranks


# calculates new network where vertices are communities from the network below, returns the new adjacency matrix of communities.

def create_new_network_from_the_base(community_pool,AdjMat):
	
	new_AdjMat=np.zeros((len(community_pool), len(community_pool)))
	
	for i in range(len(community_pool)):
		for j in range(i+1,len(community_pool)):
		
			#check if there are edges from community_i to community_j, if yes add the edge to the new adjacency matrix
			# I assume A[i][j]>0 if there is an edge with some weight from vertex i to j!
			
			B=AdjMat[community_pool[i].members,:]
			
			C=B[:,community_pool[j].members]
			new_AdjMat[i][j]=np.sum(C)
			
			
			# check if there is an edge from community_j to community_i, if yes add the edge
			
			B=AdjMat[community_pool[j].members,:]
			C=B[:,community_pool[i].members]
			new_AdjMat[j][i]=np.sum(C)

	return new_AdjMat





if __name__=="__main__":


	arg_list=[]
	GN_CHOSEN=False
	JSON_CHOSEN=False
	NO_DRAW=False
	NO_PERF=False


	(A, dir_A, GN_CHOSEN, JSON_CHOSEN, NO_DRAW, NO_PERF, MPROC,cpu)=intro(arg_list, GN_CHOSEN, JSON_CHOSEN, NO_DRAW, NO_PERF)


	handle_data_characteristics(dir_A,A,JSON_CHOSEN)
	print "\n"

	(community_pool, Q,val_curr_Q,size_curr_community_pool, t_start_algo, t_end_algo)=run_community_detection(A,MPROC,cpu)

	t_start_perf=time.time()
	performance_message=handle_performance( GN_CHOSEN, JSON_CHOSEN, community_pool)
	t_end_perf=time.time()
	handle_data_characteristics(dir_A,A,JSON_CHOSEN)
	summary.print_statistics(t_start_algo,t_end_algo,t_start_perf,t_end_perf,Q,community_pool,performance_message)
	handle_draw(NO_DRAW, JSON_CHOSEN, dir_A, A, community_pool, val_curr_Q, size_curr_community_pool,313)

	print "##################################################################################################"

	if JSON_CHOSEN==True:
		dir_A=create_new_network_from_the_base(community_pool,dir_A)
		A=dir_to_undir_A(dir_A)
	else:
		A=create_new_network_from_the_base(community_pool,A)


	while len(community_pool)>1:

		handle_data_characteristics(dir_A,A,JSON_CHOSEN)
		print "\n"

		(community_pool, Q,val_curr_Q,size_curr_community_pool, t_start_algo, t_end_algo)=run_community_detection(A,MPROC,cpu)

		t_start_perf=time.time()
		performance_message=handle_performance( GN_CHOSEN, JSON_CHOSEN, community_pool)
		t_end_perf=time.time()
		handle_data_characteristics(dir_A,A,JSON_CHOSEN)
		summary.print_statistics(t_start_algo,t_end_algo,t_start_perf,t_end_perf,Q,community_pool,performance_message)
		handle_draw(NO_DRAW, JSON_CHOSEN, dir_A, A, community_pool, val_curr_Q, size_curr_community_pool,313)

		print "##################################################################################################"

		if JSON_CHOSEN==True:
			dir_A=create_new_network_from_the_base(community_pool,dir_A)
			A=dir_to_undir_A(dir_A)
		else:
			A=create_new_network_from_the_base(community_pool,A)





