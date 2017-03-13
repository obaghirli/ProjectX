import numpy as np 
import igraph
import random
import sys
import json
import datetime
import copy

seed=random.randint(1,1000)
random.seed(seed)

community_pool=[]
paper_pool=[]

class Community():
	def __init__(self):
		self.members=[]
		self.color=( random.uniform(0.3,0.9) , random.uniform(0.3,0.9) , random.uniform(0.3,0.9) )

class Paper():
	def __init__(self):
		self._id=None
		self.title=None
		self.keywords=[]
		self.metadata=[]
		self.authors=[]
		self.date=None
		self.out_connections=[]

def connect_internal(community_pool,global_A, min_out_degree,max_out_degree):

	for community in community_pool:
		
		degree=random.randint(min_out_degree,max_out_degree)
		dic={}

		community_size=len(community.members)
		community_A=np.zeros((community_size,community_size))
		
		for i in range(community_size):
			dic[i]=community.members[i]

		for from_node in range(community_size):
			for j in range(degree):
				while  True:
					to_node=random.randint(0,community_size-1)
					if (to_node != from_node) and ( community_A[from_node,to_node]==0 and community_A[to_node,from_node]==0):
						break 
				
				community_A[from_node,to_node]=1

		(i_index,j_index)=np.where(community_A==1)
		for u in range(len(i_index)):
			global_A[dic[i_index[u]] , dic[j_index[u]] ] = 1


def connect_external(community_pool,global_A, min_group_of, max_group_of,k):
	
	community_num=len(community_pool)
	if community_num==1:
		return 0

	group_of=random.randint(min_group_of,max_group_of)

	pool_index=range(community_num)

	groups=[]
	while len(pool_index)>group_of:
		groups.append(pool_index[0:group_of])
		pool_index=pool_index[group_of:]
		group_of=random.randint(min_group_of,max_group_of)
	groups.append(pool_index)

	for group in groups:
		if len(group)>1:
			for from_community in group:
				degree=int( k*len(community_pool[from_community].members)+1 )
				for i in range(degree):
					while True:
						from_node=community_pool[from_community].members[ random.randint(0, len(community_pool[from_community].members)-1 ) ]
						while True:
							to_community=group[ random.randint(0, len(group)-1) ]
							if to_community!=from_community:
								break
						to_node=community_pool[to_community].members[ random.randint(0, len(community_pool[to_community].members)-1 ) ]

						if to_node!=from_node and ( global_A[from_node,to_node]==0 and global_A[to_node,from_node]==0 ):
							break
					global_A[from_node,to_node]=1


	for group in groups:
		all_members_in_group=[]
		for from_community in group:
			all_members_in_group=all_members_in_group + community_pool[from_community].members
		join_community=Community()
		join_community.members=all_members_in_group
		community_pool.append( join_community )

	for i in range(community_num):
		del community_pool[0]

	connect_external(community_pool,global_A, min_group_of, max_group_of,k)


def draw_graph_comm(global_A,community_pool,seed):

	random.seed(seed)
	g=igraph.Graph(directed=True)
	num=len(global_A)
	g.add_vertices(num)

	for i in range(num):
		for j in range(num):
			if global_A[i,j]>0:
				g.add_edges( [(i,j)] )

	vs=igraph.VertexSeq(g)
	es=igraph.EdgeSeq(g)
	vs["label"]=np.arange(num)

	for c in community_pool:
		memlen=len(c.members)
		for i in range(memlen):
			vs[c.members[i]]["color"]=c.color


	layout=g.layout("fruchterman_reingold")
	igraph.plot(g,layout=layout)



def extract_design_parameters():
	with open("network.param","r") as file:
		lines=file.readlines()
	lines=[line.strip() for line in lines]

	for line in lines:
		tokens=line.split()
		if tokens[0].upper()=="NODE_NUMBER":
			node_number=int(tokens[1])
		elif tokens[0].upper()=="COMMUNITY_NUMBER":
			community_number=int(tokens[1])
		elif tokens[0].upper()=="MIN_COMMUNITY_SIZE":
			min_community_size=int(tokens[1])		
		elif tokens[0].upper()=="MAX_COMMUNITY_SIZE":
			max_community_size=int(tokens[1])	
		elif tokens[0].upper()=="MIN_OUT_DEGREE":
			min_out_degree=int(tokens[1])
		elif tokens[0].upper()=="MAX_OUT_DEGREE":
			max_out_degree=int(tokens[1])
		elif tokens[0].upper()=="MIN_GROUP_OF":
			min_group_of=int(tokens[1])
		elif tokens[0].upper()=="MAX_GROUP_OF":
			max_group_of=int(tokens[1])
		elif tokens[0].upper()=="MODULARITY_COEFF":
			modularity_coeff=float(tokens[1])

	return (node_number,community_number,min_community_size,max_community_size,min_out_degree,max_out_degree,min_group_of,max_group_of,modularity_coeff)


def print_statistics(global_A,community_number,real_min_community_size,real_max_community_size,real_average_comm_size):
	node_number=len(global_A)
	edge_number=np.sum(global_A)
	average_degree=edge_number/node_number
	min_out_degree=np.min(np.sum(global_A, axis=1))
	max_out_degree=np.max(np.sum(global_A, axis=1))
	min_in_degree=np.min(np.sum(global_A, axis=0))
	max_in_degree=np.max(np.sum(global_A, axis=0))

	print "\n---Statistics---"
	print "NODE NUMBER: ",node_number
	print "EDGE NUMBER: ",edge_number
	print "AVERAGE DEGREE: ",average_degree
	print "MIN OUT DEGREE: ",min_out_degree
	print "MAX OUT DEGREE: ",max_out_degree
	print "MIN IN DEGREE: ",min_in_degree
	print "MAX IN DEGREE: ",max_in_degree
	print "AVERAGE COMMUNITY SIZE: ",real_average_comm_size
	print "MIN COMMUNITY SIZE: ",real_min_community_size
	print "MAX COMMUNITY SIZE: ",real_max_community_size
	print "COMMUNITY NUMBER: ",community_number
	print "-----------------\n"


	with open("network.stat",'w') as out_file:
		out_file.write("NODE NUMBER: {}\n".format(node_number))
		out_file.write("EDGE NUMBER: {}\n".format(edge_number))
		out_file.write("AVERAGE DEGREE: {}\n".format(average_degree))
		out_file.write("MIN OUT DEGREE: {}\n".format(min_out_degree))
		out_file.write("MAX OUT DEGREE: {}\n".format(max_out_degree))
		out_file.write("MIN IN DEGREE: {}\n".format(min_in_degree))
		out_file.write("MAX IN DEGREE: {}\n".format(max_in_degree))
		out_file.write("AVERAGE COMMUNITY SIZE: {}\n".format(real_average_comm_size))
		out_file.write("MIN COMMUNITY SIZE: {}\n".format(real_min_community_size))
		out_file.write("MAX COMMUNITY SIZE: {}\n".format(real_max_community_size))
		out_file.write("COMMUNITY NUMBER: {}\n".format(community_number))

def print_community_membership_to_file(community_pool):
	with open("community_assignment.dat", "w") as file:
		for index,community in enumerate(community_pool):
			for member in community.members:
				file.write( "{}\t{}\n".format(member,index) )


def print_links_to_file(global_A):
	with open("links.dat","w") as file:
		for source in range(len(global_A)):
			for target in np.where(global_A[source]==1)[0]:
				file.write( "{}\t{}\n".format(source,target) )


def fill_community_papers(paper_pool,community_pool):
	start=0
	for community in community_pool:
		community_size=len(community.members)
		end=start+2*community_size
		for member_paper in community.members:
			paper_pool[member_paper]._id=member_paper
			paper_pool[member_paper].title="Title_"+str(random.randint(0,10000))+str(random.randint(0,10))
			paper_pool[member_paper].keywords=list(set([ "keyword_"+str( random.randint(start,end-1) )  for i in range( random.randint(4,8) ) ]))
			paper_pool[member_paper].metadata=[]
			paper_pool[member_paper].authors=list(set(["Author_"+str(random.randint(start,end-1)) for i in range(random.randint(1,4))]))
			paper_pool[member_paper].date=str(datetime.date(random.randint(1992,2017),random.randint(1,12),random.randint(1,28) ))
		start=end


def add_out_connections(paper_pool,global_A):
	for paper in paper_pool:
		_id=paper._id
		paper.out_connections=np.where(global_A[_id]==1)[0].tolist()


def print_papers_to_json(paper_pool):

	root={}

	paper_array=[ {} for i in range(len(paper_pool)) ]
	for pool_index, paper_dict in enumerate(paper_array):
		paper_dict["_id"]=paper_pool[pool_index]._id
		paper_dict["title"]=paper_pool[pool_index].title
		paper_dict["keywords"]=paper_pool[pool_index].keywords
		paper_dict["metadata"]=paper_pool[pool_index].metadata
		paper_dict["authors"]=paper_pool[pool_index].authors
		paper_dict["date"]=paper_pool[pool_index].date
		paper_dict["references"]=paper_pool[pool_index].out_connections

	root["Papers"]=paper_array

	with open('data.json', 'w') as file:
	  file.write(json.dumps(root,separators=(',',':'), indent=4))


if __name__=="__main__":

	NODRAW=False

	arg_list=[]
	for arg in sys.argv:
		arg_list.append(arg.upper())

	if "-NODRAW" in arg_list:
		NODRAW=True

	(node_number,community_number,min_community_size,max_community_size,min_out_degree,max_out_degree,min_group_of,max_group_of,modularity_coeff)=extract_design_parameters()

	global_A=np.zeros((node_number,node_number)).astype("int8")

	nodes=np.arange(node_number)
	np.random.shuffle(nodes)
	nodes=nodes.tolist()

	for i in range(len(nodes)):
		paper=Paper()
		paper_pool.append(paper)

	start=0
	community_size_list=[]
	for i in range(community_number-1):

		community_size=random.randint( min_community_size, max_community_size )
		community_size_list.append(community_size)
		end=start+community_size

		community=Community()
		community.members=nodes[start:end]
		community_pool.append(community)

		start=end

	community=Community()
	community.members=nodes[start:]
	community_size_list.append(len(community.members))
	community_pool.append(community)
	initial_community_pool=copy.deepcopy(community_pool)

	fill_community_papers(paper_pool,community_pool)

	print_community_membership_to_file(community_pool)

	connect_internal(community_pool,global_A, min_out_degree,max_out_degree)

	connect_external(community_pool,global_A, min_group_of, max_group_of, modularity_coeff)

	real_min_comm_size=min(community_size_list)
	real_max_comm_size=max(community_size_list)
	real_average_comm_size=sum(community_size_list)/len(community_size_list)
	print_statistics(global_A,community_number,real_min_comm_size,real_max_comm_size,real_average_comm_size)

	add_out_connections(paper_pool,global_A)

	print_links_to_file(global_A)

	print_papers_to_json(paper_pool)


	print "---Files Generated---"
	print "network.stat"
	print "community_assignment.dat"
	print "links.dat"
	print "data.json"
	print "---------------------"

	if NODRAW==False:
		draw_graph_comm(global_A,initial_community_pool,313)

