import igraph
import numpy as np
import sys
from   sys import stdout
import parser
import time
import random
import summary
import json
import database

seed=random.randint(1,2000)
random.seed(seed)


def intro(arg_list, NO_DRAW, MAX_DESIRED_COMMUNITY_SIZE):


	for arg in sys.argv:
		arg_list.append(arg.upper())


	if "-F" in arg_list:
		for position,arg in enumerate(arg_list):
			if arg=="-F":
				json_filename=arg_list[position+1].lower()
				json_filesize=int(arg_list[position+2])

		print "Parsing Paper Dataset... ",
		stdout.flush()
		G=parser.parse_json_create_graph(json_filename, json_filesize)
		print "Done"
		UG=G.as_undirected(mode="collapse", combine_edges=sum)

	else:
		sys.exit("Missing File Name. -f [filename]")

	if "-LIMIT" in arg_list:
		for position, arg in enumerate(arg_list):
			if arg=="-LIMIT":
				MAX_DESIRED_COMMUNITY_SIZE=int(arg_list[position+1])


	if "-NODRAW" in arg_list:
		NO_DRAW=True

	return (UG, G, NO_DRAW, MAX_DESIRED_COMMUNITY_SIZE, json_filename, json_filesize)


def run_community_detection(UG,tag):

	print "Running Community Detection: {}... ".format( tag ),
	stdout.flush()
	dendogram=UG.community_fastgreedy(weights='weight')
	clustering=dendogram.as_clustering()
	community_pool=clustering.subgraphs()
	Qmax=clustering.q
	print "Done"

	return (community_pool, Qmax)

def acquire_membership_vector(community_pool, G):
	membership=np.zeros((1,len(G.vs['label'])))
	community_id =0
	for community in community_pool:
		membership[0, community.vs['label']  ]=community_id
		community_id=community_id+1
	return membership[0]


def recalculate_Qmax(community_pool, UG):
	membership=acquire_membership_vector(community_pool, UG)
	Clustering=igraph.clustering.VertexClustering( UG, membership )
	new_Qmax=Clustering.q
	return new_Qmax


def handle_draw(NO_DRAW, UG, community_pool, draw_seed, tag):
	if NO_DRAW==False:
		random.seed(draw_seed)
		print "Drawing: {}: Please wait for the graph.".format(tag)

		if len(community_pool)>1:
			membership=acquire_membership_vector(community_pool, UG)
			Clustering=igraph.clustering.VertexClustering( UG, membership )
			layout=UG.layout("fruchterman_reingold")
			igraph.plot( Clustering ,layout=layout )
			print "\n"
		else:
			layout=UG.layout("fruchterman_reingold")
			igraph.plot( UG ,layout=layout )
			print "\n"


# calculates page ranks of vertices in the given graph: AdjMat, returns the list of pageranks.
def calculate_pageranks(G):
	pageranks=G.pagerank(weights='weight')
	pageranks = np.array(pageranks)*len(pageranks) #normalize by node number
	return pageranks


# calculates new network where vertices are communities from the network below, returns the new adjacency matrix of communities.
def create_new_network_from_the_base(community_pool,G):
	
	membership=acquire_membership_vector(community_pool, G)
	Clustering=igraph.clustering.VertexClustering( G, membership )
	new_G=Clustering.cluster_graph(combine_edges=False)
	new_G.vs['label']=np.arange(len(community_pool))
	new_G.simplify(multiple=True, loops=True, combine_edges=sum)
	new_UG=new_G.as_undirected(mode="collapse", combine_edges=sum)

	return (new_G, new_UG)



def find_community_indices_to_further_divide(community_pool, MAX_DESIRED_COMMUNITY_SIZE):

	community_indices_to_further_divide=[]
	for position, community in enumerate(community_pool):
		if len(community.vs['label'])>MAX_DESIRED_COMMUNITY_SIZE:
			community_indices_to_further_divide.append(position)
	return community_indices_to_further_divide



if __name__=="__main__":


	arg_list=[]
	NO_DRAW=False
	MAX_DESIRED_COMMUNITY_SIZE=1000000

	levels_init_down=""

	(UG, G, NO_DRAW, MAX_DESIRED_COMMUNITY_SIZE, json_filename, json_filesize)=intro(arg_list, NO_DRAW, MAX_DESIRED_COMMUNITY_SIZE)
	summary.data_characteristics(G, UG)

	#calculate papers` pageranks and adding paper objects into database

	print "Calculating Paper PageRanks... ",
	stdout.flush()
	paper_pageranks=calculate_pageranks(G)
	print "Done"
	print "Database: Paper Objects ---> NEO4J... ",
	stdout.flush()
	with open(json_filename,'r') as json_data:
		records=json.load(json_data)
  	database.load_base_network_into_database(records, paper_pageranks)
  	print "Done"


	print "\n---- Creating INITIAL Communities... "
	(community_pool, Qmax)=run_community_detection(UG, "on Original Data")
	summary.print_community_statistics(Qmax,community_pool,"Created Initial Communities")
	print 	"---- Creating INITIAL Communities: Done"
	levels_init_down=levels_init_down+"Size: {}: Initial\n".format( len(community_pool) )


	community_indices_to_further_divide=find_community_indices_to_further_divide(community_pool, MAX_DESIRED_COMMUNITY_SIZE)
	if len(community_indices_to_further_divide) >0:
		print "\n---- Going Downward...\n"
		
		level=0
		while len(community_indices_to_further_divide)>0:

			level=level+1
			check_list=[]
			del_list=[]
			counter=0

			for index in community_indices_to_further_divide:
				counter=counter+1

				text="Going Downward: Attempt: to Creating LEVEL:-{} - JOB: {}/{} ".format(level, counter, len(community_indices_to_further_divide))
				(new_community_pool, new_Qmax)=run_community_detection(community_pool[index], text)

				check_list.append( len(new_community_pool) )
				if len(new_community_pool)==1:
					print "WARNING: No further division possible from LEVEL: -{} to LEVEL: -{} for THIS community. Ignore THIS and CONTINUE!".format(level-1,level)
					continue
				else:
					del_list.append(index)
					for new_community in new_community_pool:
						community_pool.append(new_community)

			if sum(check_list)==len(community_indices_to_further_divide):
				print "WARNING: LEVEL: -{} NOT CREATED! No further division possible from LEVEL: -{} to LEVEL: -{} for ANY communities. Stopped GOING DOWNWARD beyond LEVEL: -{} and CONTINUE!".format(level,level-1, level, level-1)
				break
			else:
				print "LEVEL -{} created!".format(level)

				for index in sorted( del_list, reverse=True ):
					del community_pool[index]

				levels_init_down=levels_init_down+"Size: {}: Going Downward: Level: -{}\n".format( len(community_pool), level )
				community_indices_to_further_divide=find_community_indices_to_further_divide(community_pool, MAX_DESIRED_COMMUNITY_SIZE)

		new_Qmax=recalculate_Qmax(community_pool, UG)
		summary.print_community_statistics(new_Qmax ,community_pool,"Created Base Communities")

	print "\n"
	handle_draw(NO_DRAW, UG, community_pool,313,"Base Communities")


	if len(community_pool) >1:
		print "---- Going Upward...\n"

		levels_up=""
		level=0
		while len(community_pool)>1:

			level=level+1
			print "Creating LEVEL: +{}... ".format(level),
			stdout.flush()
			(new_G, new_UG)=create_new_network_from_the_base(community_pool,G)
			print "Done"

			print "Calculating LEVEL:+{} Community PageRanks... ".format(level),
			stdout.flush()
			community_pageranks=calculate_pageranks(new_G)
			print "Done"

			print "Database: LEVEL: +{} Objects ---> NEO4J... ".format(level),
			stdout.flush()
			database.load_community_into_database(community_pool,level,new_G, community_pageranks)
			print "Done"

			text="Going Upward: on LEVEL: +{}".format(level)
			(community_pool, Qmax)=run_community_detection(new_UG, text)
			print "\n"

			G=new_G
			levels_up=levels_up+"Size: {}: Going Upward: Level: +{}\n".format(new_G.vcount(), level )
			handle_draw(NO_DRAW, new_UG, community_pool,313, "LEVEL: +{} Communities".format(level)  )


	#add root to database/ root needs to be added seperately, since "Going Upward cannot handle len(community_pool==1), which is the case for root "
	#that means, last thing "Going Upward" does is merging 2X2 matrix and creating community_pool of 1 element, where run_community_detection must not be run on.
	#therefore this case handled seperately

	level=level+1 # level of root
	print "Creating ROOT: LEVEL: +{}... ".format(level),
	stdout.flush()
	(new_G, new_UG)=create_new_network_from_the_base(community_pool,G)
	print "Done"

	print "Calculating ROOT: LEVEL:+{} Community PageRanks... ".format(level),
	stdout.flush()
	dummy_root_pagerank=np.array([1.0])
	print "Done"

	print "Database: ROOT: LEVEL: +{} Objects ---> NEO4J... ".format(level),
	stdout.flush()
	database.load_community_into_database(community_pool,level,new_G, dummy_root_pagerank)
	print "Done"

	levels_up=levels_up+"Size: {}: Going Upward: Level: +{}: ROOT\n".format( len(community_pool), level ) # this creates the +levels content to save to levels.txt file
	print "\n"
	handle_draw(NO_DRAW, new_UG, community_pool,313, "ROOT: LEVEL: +{} Communities".format(level)  )

	summary.print_levels(levels_init_down, levels_up)
	
	print "Almost Finished! A few more steps to go ...\n"


	# adding community titles and keywords to the database
	ROOT_LEVEL=level
	print "Starting to add: community.title and community.keywords to the database... \n"
	database.add_title_keywords_to_communities(ROOT_LEVEL)
	
	print "\nFinished!"
	summary.print_files_generated()


