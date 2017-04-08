from neo4j.v1 import GraphDatabase, basic_auth
import igraph
import numpy as np
from   sys import stdout


driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "235689Or@")) # connecting to Neo4j database, currently localhost

# This function loads the citation network of papers into the neo4j database. Each record in records is the information about a paper.
# This function needs to be called once. And periodically later in case new paper/papers is added to the system.


def load_base_network_into_database(records, paper_pageranks):

	# url, usernama and password of the database will be configured later, currently default is used.
	# we may consider creating driver object once and make it global.
	
	session=driver.session()
	statement = "CREATE (:Paper {id:{id},title:{title}, pagerank:{pagerank}, keywords:{keywords}, authors:{authors}, metadata:{metadata}, date_:{date}  })" # this is the query template that will be used, fields can be changed later.

	for record in records["Papers"]: # how many records, that many rangeranks, no need for another iteration

		_id=record["_id"]		
		_title=record["title"]
		_pagerank=paper_pageranks[_id]
		_keywords=record["keywords"]
		_authors=record["authors"]
		_date=record["date"]
		_metadata=record["metadata"]

		res=session.run(statement,id=_id,title=_title, pagerank=_pagerank, keywords=_keywords, authors=_authors, metadata=_metadata, date=_date) # executing the query, right now auto-commit is used, meaning query is commited right after. We may consider doing one commit after pipelining all the changes.
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
def load_community_into_database(community_pool,level,new_G, community_pageranks):
	# url, usernama and password of the database will be configured later, currently default is used.
	
	# we may consider creating driver object once and make it global. 
	  	
	session=driver.session()

	template1= "CREATE (:Community {id:{id},level:{_level},pagerank:{_pagerank} })" # this is the query template that will be used, fields can be changed later.
	template2="match(c1:Community),(c2:Community) where  c1.id={id1} and c1.level={_level} and c2.level={_level} and c2.id={id2} create (c1)-[:Cites{weight:{weight}}]->(c2)"
	template3="match(parent:Community), (child:Paper) where parent.id={parent_id} and parent.level={parent_level} and child.id IN {parent_children} create (parent)-[:child]->(child)" # this template is used to add the membership relationship between the community and the nodes from one level below
	template4="match(parent:Community), (child:Community) where parent.id={parent_id} and parent.level={parent_level} and child.level={child_level} and child.id IN {parent_children} create (parent)-[:child]->(child)"																											

	
	# this iteration loads only community nodes																											
	index=0																										
	for community in community_pool:
		with session.begin_transaction() as tx:
			res=tx.run(template1,id=index,_level=level, _pagerank=community_pageranks[index] )
			res.consume()
			tx.success=True
		index=index+1

	
	# this iteration loads inter-community relationships/citations

	list_of_list_of_connected_nodes=new_G.get_adjlist(mode=igraph.OUT)

	for i in range(0,len(community_pool)):
		list_of_connected_nodes=list_of_list_of_connected_nodes[i]
		
		for ind in list_of_connected_nodes:

			new_es= new_G.es.select( _source_in=[i] )
			new_es= new_es.select( _target_in=[ind] )
			WEIGHT= new_es['weight']

			with session.begin_transaction() as tx:
				res=tx.run(template2,id1=i,_level=level,id2=ind,weight=WEIGHT)
				res.consume()
				tx.success=True

	# this iteration loads the membership relationshop between this level's communities and the nodes one level below
	# if level is 1, then template 3 is used, otherwise template 4 is used
	index=0
	for community in community_pool:
		with session.begin_transaction() as tx:
			
			if level>1:
				res=tx.run(template4,parent_id=index,parent_level=level,child_level=level-1,parent_children=community.vs['label'])
			else:
				res=tx.run(template3,parent_id=index,parent_level=level,parent_children=community.vs['label'])
			
			res.consume()
			tx.success=True
		
		index=index+1



def add_title_keywords_to_communities(ROOT_LEVEL):

	DESCRIPTOR_LIMIT=1 # number of entities (papers/sub-communities) to describe the parent community. If changed, the program will crash. Decision is to have 1 title and keywords list to describe a community.
					   # So, title of the parent community = title of the best(in terms of pagerank) entity (paper or sub-community) it holds inside,
					   #     keywords of the parent community = best entity`s keywords 

	# returns the number of communities on a level, e.g if 10, then the community ids on that level are [0,1,....9]
	template_0="MATCH (communities:Community) WHERE communities.level={level} RETURN count(communities) AS community_number"
	# returns the parent community`s children entities` titles and keywords as it is ordered by the pagerank value from best to worst and picks the best one
	template_1="MATCH (parent:Community)-[:child]->(children) WHERE parent.level={level} AND parent.id={parent_id} RETURN children.title, children.keywords, children.pagerank as pagerank ORDER BY pagerank DESC LIMIT {limit}"
	# adds the parent community`s found best entity`s title and keywords to the parent community
	template_2="MATCH (parent:Community) WHERE parent.level={level} AND parent.id={parent_id} SET parent.keywords={keywords}, parent.title={title}"

	session=driver.session()

	for level in range(1,ROOT_LEVEL+1): # from level 1 up to and including the root level
		
		print "Database: LEVEL: {}/{} community.title and community.keywords ---> NEO4J... ".format(level, ROOT_LEVEL),
		stdout.flush()

		# in this part, we get the community number on any level
		with session.begin_transaction() as tx:
			
			info=tx.run(template_0, level=level)
			records=list(info) # as far as i understood, we always need to convert the info to a python list to process the info
			community_number=records[0]["community_number"] # records[0] is the only object in the list( and it is a dict )
			info.consume()
			tx.success=True


		for parent_id in range(community_number): # iterating over the community ids

			keywords=[]
			title=""

			# in this part, we find the best entity and store its title and keywords values
			with session.begin_transaction() as tx:

				info=tx.run(template_1, level=level, parent_id=parent_id, limit=DESCRIPTOR_LIMIT)
				records=list(info)
				
				for record in records:
					keywords=[ str(keyword) for keyword in record["children.keywords"] ] # if I did not do this, list returned from record["children.keywords"] has elements with uncommon python string type 
					title=str(record["children.title"])

				info.consume()
				tx.success=True

			# in this part, we add the stored title and keywords values to a parent community 
			with session.begin_transaction() as tx:
				
				info=tx.run(template_2, level=level, parent_id=parent_id, keywords=keywords, title=title)
				info.consume()
				tx.success=True

		print "Done"