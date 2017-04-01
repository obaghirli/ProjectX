import numpy as np
import json
import igraph


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



def parse_json_create_graph(json_filename, json_filesize):

	with open(json_filename,'r') as json_data:
		records=json.load(json_data)	

	G=igraph.Graph(directed=True)
	G.add_vertices(json_filesize)
	G.vs["label"]=np.arange(json_filesize)

	for record in records["Papers"]:
		G.add_edges( [ (record["_id"],reference  ) for reference in record["references"] ] )

	G.es["weight"]=1

	return G







