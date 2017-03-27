import numpy as np
import json
from neo4j.v1 import GraphDatabase, basic_auth


   #     1   2   3   4   5   6   7   8   9   10   11   12   13
TEST=[ [ 0,  1,  1,  1,  0,  0,  0,  0,  0,  0,   0,   0,   0  ],  #1
	   [ 1,  0,  1,  0,  0,  0,  0,  0,  0,  0,   0,   0,   0  ],  #2
	   [ 1,  1,  0,  1,  1,  0,  0,  0,  0,  0,   0,   0,   0  ],  #3
	   [ 1,  0,  1,  0,  0,  0,  0,  0,  0,  0,   0,   0,   0  ],  #4
	   [ 0,  0,  1,  0,  0,  1,  1,  1,  0,  0,   0,   0,   0  ],  #5
	   [ 0,  0,  0,  0,  1,  0,  1,  0,  0,  0,   0,   0,   0  ],  #6
	   [ 0,  0,  0,  0,  1,  1,  0,  1,  0,  1,   0,   0,   0  ],  #7
	   [ 0,  0,  0,  0,  1,  0,  1,  0,  0,  0,   0,   0,   0  ],  #8
	   [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,   1,   0,   1  ],  #9
	   [ 0,  0,  0,  0,  0,  0,  1,  0,  1,  0,   1,   1,   0  ],  #10
	   [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  1,   0,   1,   0  ],  #11
	   [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,   1,   0,   1  ],  #12
	   [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  0,   0,   1,   0  ] ] #13
TEST=np.array(TEST).astype('int8')

def karate_club():
	clean_lines=[]
	with open('karate.txt') as f:
		lines=f.readlines()
	lines=[x.strip() for x in lines]

	for i in range(len(lines)):
		if lines[i]!="":
			clean_lines.append(lines[i])


	clean_lines=np.array(clean_lines).reshape((len(clean_lines)/2,2))
	(row,col)=clean_lines.shape
	KARATE=np.zeros((34,34)).astype('int8')

	for u in range(row):
		[fs1,sc1]=clean_lines[u,0].split()
		[fs2,sc2]=clean_lines[u,1].split()
		KARATE[ int(sc1)-1 , int(sc2)-1 ]=1
		KARATE[ int(sc2)-1 , int(sc1)-1 ]=1

	return KARATE


def football():
	clean_lines=[]
	with open('football.txt') as f:
		lines=f.readlines()
	lines=[x.strip() for x in lines]

	for i in range(len(lines)):
		if lines[i]!="":
			clean_lines.append(lines[i])


	clean_lines=np.array(clean_lines).reshape((len(clean_lines)/2,2))
	(row,col)=clean_lines.shape
	FOOTBALL=np.zeros((115,115)).astype('int8')

	for u in range(row):
		[fs1,sc1]=clean_lines[u,0].split()
		[fs2,sc2]=clean_lines[u,1].split()
		FOOTBALL[ int(sc1) , int(sc2) ]=1
		FOOTBALL[ int(sc2) , int(sc1) ]=1

	return FOOTBALL


def dolphin():
	clean_lines=[]
	with open('dolphin.txt') as f:
		lines=f.readlines()
	lines=[x.strip() for x in lines]

	for i in range(len(lines)):
		if lines[i]!="":
			clean_lines.append(lines[i])


	clean_lines=np.array(clean_lines).reshape((len(clean_lines)/2,2))
	(row,col)=clean_lines.shape
	DOLPHIN=np.zeros((62,62)).astype('int8')

	for u in range(row):
		[fs1,sc1]=clean_lines[u,0].split()
		[fs2,sc2]=clean_lines[u,1].split()
		DOLPHIN[ int(sc1) , int(sc2) ]=1
		DOLPHIN[ int(sc2) , int(sc1) ]=1

	return DOLPHIN


def gn():
	clean_lines=[]
	with open("benchmark/network.dat") as f:
		lines=f.readlines()
	lines=[x.strip() for x in lines]
	for i in range(len(lines)):
		if lines[i]!="":
			clean_lines.append(lines[i])

	clean_lines=np.array(clean_lines).reshape((len(clean_lines),1))
	(row,col)=clean_lines.shape
	size= int(clean_lines[row-1,0].split()[0])
	GN=np.zeros((size,size)).astype('int8')
	for u in range(row):
		[s,t]=clean_lines[u,0].split()
		GN[ int(s)-1 , int(t)-1 ]=1

	return GN

	
def arxivhepth():
	stream=[]

	with open("arxivhepth.txt") as f:
		lines=f.readlines()
	lines=[line.strip() for line in lines]
	lines=np.array(lines)
	length=len(lines)

	mat=lines.reshape((length,1))

	for i in range(length):
		[s,t]=mat[i,0].split()
		stream.append(int(s))
		stream.append(int(t))

	stream=np.array(stream)
	base=np.unique(stream)

	idx=0
	for i in base:
		stream[ np.where(stream==i) ]=idx
		idx+=1

	stream=stream.reshape((length,2))
	ARXIVHEPTH=np.zeros((len(base),len(base))).astype('int8')

	for i in range(length):
		ARXIVHEPTH[ stream[i,0] ,stream[i,1] ]=1
		ARXIVHEPTH[ stream[i,1] ,stream[i,0] ]=1

	return ARXIVHEPTH



# This function loads the citation network of papers into the neo4j database. Each record in records is the information about a paper.
# This function needs to be called once. And periodically later in case new paper/papers is added to the system.


def load_base_network_into_database(records):

	# url, usernama and password of the database will be configured later, currently default is used.
	
	# we may consider creating driver object once and make it global.
	driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "235689Or@")) # connecting to Neo4j database, currently localhost
  	
	session=driver.session()
	statement = "CREATE (:Paper {id:{id},title:{title}})" # this is the query template that will be used, fields can be changed later.

	for record in records["Papers"]:

		_id=record["_id"]		
		_title=record["title"]

		res=session.run(statement,id=_id,title=_title) # executing the query, right now auto-commit is used, meaning query is commited right after. 
														# we may consider doing one commit after pipelining all the changes.
		res.consume() # for moving the cursor right so that changes are saved in database( I dont get it )


	# second iteration over records will be for adding citation relationships between papers that already must exist in database now
	
	statement="match(a:Paper),(b:Paper) where a.id={id} and b.id IN {references} create (a)-[:Cites]->(b)" # this is the template query

	# unlike above, here we explicitly commit in the end. 
	
	with session.begin_transaction() as tx:
		for record in records["Papers"]:
			res=tx.run(statement,id=record["_id"],references=record["references"])
			res.consume()
		tx.success=True



# This function loads the community pool into the database
# This function needs to be called once. And periodically later in case new paper/papers is added to the system.
# Inputs->
# community_pool : list of list showing what members from the one level below the community contains. Members are shown as the ids of the members. Index in the pool is the global id of the community.
# adj_mat: adj matrix showing the inter-community connections, indices denoting the ids of the communities present in community pool
# level : it is the level at which these community pool resides
def load_community_into_database(community_pool,level,adj_mat):
	# url, usernama and password of the database will be configured later, currently default is used.
	
	# we may consider creating driver object once and make it global. 
	driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "235689Or@")) # connecting to Neo4j database, currently localhost
  	
	session=driver.session()


	template1= "CREATE (:Community {id:{id},level:{_level}})" # this is the query template that will be used, fields can be changed later.
	template2="match(c1:Community),(c2:Community) where  c1.id={id1} and c1.level={_level} and c2.level={_level} and c2.id={id2} create (c1)-[:Cites{weight:{weight}}]->(c2)"
	
	template3="match(parent:Community), (child:Paper) where parent.id={parent_id} and parent.level={parent_level} and child.id IN {parent_children} create (parent)-[:child]->(child)" # this template is used to add the membership relationship
																												# between the community and the nodes from one level below

	template4="match(parent:Community), (child:Community) where parent.id={parent_id} and parent.level={parent_level} and child.level={child_level} and child.id IN {parent_children} create (parent)-[:child]->(child)"																											

	

	# this iteration loads only community nodes																											
	index=0																										
	for community in community_pool:
		with session.begin_transaction() as tx:
			res=tx.run(template1,id=index,_level=level)
			res.consume()
			tx.success=True
		index=index+1

	
	
	# this iteration loads inter-community relationships/citations
	for i in range(0,len(community_pool)):
		list_of_connected_nodes=[j for j,e in enumerate(adj_mat[i]) if e!=0]
		
		for ind in list_of_connected_nodes:

			with session.begin_transaction() as tx:
				res=tx.run(template2,id1=i,_level=level,id2=ind,weight=adj_mat[i][ind])
				res.consume()
				tx.success=True


	# this iteration loads the membership relationshop between this level's communities and the nodes one level below
	# if level is 1, then template 3 is used, otherwise template 4 is used

	index=0
	for community in community_pool:
		with session.begin_transaction() as tx:
			
			if level>1:
				res=tx.run(template4,parent_id=index,parent_level=level,child_level=level-1,parent_children=community.members)
			else:
				res=tx.run(template3,parent_id=index,parent_level=level,parent_children=community.members)
			

			

			res.consume()
			tx.success=True
		

		index=index+1


	



def parse_json_create_dir_A(json_data_filename, total_entry_number):


	dir_A=np.zeros((total_entry_number, total_entry_number)).astype("int8")

	with open(json_data_filename,'r') as json_data:
		records=json.load(json_data)

	
  	load_base_network_into_database(records) # I commented it out because, I needed this once to load things into the database (for testing too).
  	for record in records["Papers"]:

    		
		dir_A[record["_id"], record["references"]]=1
	
    
	return dir_A 







