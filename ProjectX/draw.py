import igraph
import random
import numpy as np
import matplotlib.pyplot as plt


def plot_adj_matrix(A):

	fig = plt.figure()
	ax = fig.add_subplot(111)

	A=np.array(A)
	(row,col)=A.shape

	x=np.tile( np.arange(0,row),(row,1) ).T
	ax.scatter(x,x.T,c=A)
	plt.title("Adjacency Matrix")
	plt.show()


def plot_Q(val_curr_Q,size_curr_community_pool):

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(size_curr_community_pool,val_curr_Q)
	plt.xlabel("Community Numbers")
	plt.ylabel("Q factor")
	plt.title("Q factor over Community Number")
	plt.show()


def draw_graph_adj(A,seed):

	random.seed(seed)
	g=igraph.Graph()
	num=len(A)
	g.add_vertices(num)

	for i in range(num):
		for j in range(i,num):
			if A[i,j]>0:
				g.add_edges( [(i,j)] )

	vs=igraph.VertexSeq(g)
	es=igraph.EdgeSeq(g)
	vs["label"]=np.arange(num)

	layout=g.layout("fruchterman_reingold")
	igraph.plot(g,layout=layout)


def draw_graph_comm(A,community_pool,seed):

	random.seed(seed)
	g=igraph.Graph()
	num=len(A)
	g.add_vertices(num)

	for i in range(num):
		for j in range(i,num):
			if A[i,j]>0:
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