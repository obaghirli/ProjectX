import numpy as np


def print_community_stat(community_pool):
	size_array=[]
	for community in community_pool:
		size=len(community.vs['label'])
		size_array.append(size)
	sorted_array=sorted(size_array)

	line1= "Size of the Smallest Community: {}\n".format(sorted_array[0])
	line2= "Size of the Largest Community: {}\n".format(sorted_array[-1])
	line3= "Size of the Average Community: {}\n".format( sum(sorted_array)/len(sorted_array) )
	return line1+line2+line3


def data_characteristics(G, UG):

	node_number=len(G.vs)

	edge_number=np.sum(G.es['weight'])
	average_degree=edge_number/node_number
	min_out_degree=np.min(G.outdegree())
	max_out_degree=np.max(G.outdegree())
	min_in_degree=np.min(G.indegree())
	max_in_degree=np.max(G.indegree())

	edge_number_undirected=np.sum(UG.es['weight'])
	average_degree_undirected=2*edge_number_undirected/node_number
	min_out_degree_undirected=np.min(UG.outdegree())
	max_out_degree_undirected=np.max(UG.outdegree())
	min_in_degree_undirected=np.min(UG.indegree())
	max_in_degree_undirected=np.max(UG.indegree())

	line1= "\n---Data Characteristics---\n"
	line2=   "--------------------------\n\n"
	line3= "Total Node Number: {}\n\n".format(node_number)
	line4= "Total Edge Number:Directed: {}\n".format(edge_number)
	line5= "Average Degree per Node:Directed: {}\n".format(average_degree)
	line6= "Min Out Degree:Directed: {}\n".format(min_out_degree)
	line7= "Max Out Degree:Directed: {}\n".format(max_out_degree)
	line8= "Min In Degree:Directed: {}\n".format(min_in_degree)
	line9= "Max In Degree:Directed: {}\n\n".format(max_in_degree)
	line10= "Total Edge Number:Undirected: {}\n".format(edge_number_undirected)
	line11= "Average Degree per Node:Undirected: {}\n".format(average_degree_undirected)
	line12= "Min Out Degree:Undirected: {}\n".format(min_out_degree_undirected)
	line13= "Max Out Degree:Undirected: {}\n".format(max_out_degree_undirected)
	line14= "Min In Degree:Undirected: {}\n".format(min_in_degree_undirected)
	line15= "Max In Degree:Undirected: {}\n\n".format(max_in_degree_undirected)
	line16= "-------------END---------\n"

	with open("statistics.txt", 'w') as file:
		file.write( line1+line2+line3+line4+line5+line6+line7+line8+line9+line10+line11+line12+line13+line14+line15+line16  )


def print_community_statistics(Qmax,community_pool, section_name):
	line1= "\n---Community Statistics---\n"
	line2= "---{}---\n".format(section_name)
	line3= "--------------------------\n"
	line4= "Quality Factor: {}\n".format(Qmax)
	line5= "Total Number of Communities: {}\n".format(len(community_pool))
	line6= print_community_stat(community_pool)
	line7= "---------\n"
	line8= "---END---\n"

	with open("statistics.txt", 'a') as file:
		file.write( line1+line2+line3+line4+line5+line6+line7+line8 )


def print_levels(levels_init_down, levels_up):
	content="\n---Levels Created---\n\n"+levels_init_down+levels_up
	with open("levels.txt", 'w') as file:
		file.write(content)

def print_files_generated():
	print "\n-----------------------"
	print 	"Generated System Files"
	print   "-----------------------"
	print   "levels.txt"
	print 	"statistics.txt"
	print 	"\n"

