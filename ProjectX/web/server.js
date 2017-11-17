var express = require ("express");
var bodyParser = require('body-parser');
var neo4j = require('neo4j-driver').v1;

var server = express();
var driver = neo4j.driver("bolt://localhost:7687", neo4j.auth.basic("neo4j", "235689Or@"));

server.use( bodyParser.json() );
server.use(bodyParser.urlencoded({
	extended: true
}));

//template_nodes_query_results="MATCH (n:Paper) WHERE {keyword} in n.keywords RETURN n  ORDER BY n.pagerank LIMIT {limit}";


server.use(express.static('client'));

function process_search_query(query_array, res, search_field){

	if (search_field==0){
		var template_nodes_query_results="MATCH (n:Paper) WHERE ANY (m IN {query_array} WHERE m in n.keywords) RETURN n  ORDER BY n.pagerank LIMIT {limit}";
		var template_group_id="MATCH (child:Paper)<-[:child]-(parent) WHERE child.id={child_id}  RETURN parent.id AS parent_id";
		var template_is_connected="MATCH(n1:Paper), (n2:Paper) WHERE n1.id={id1} and n2.id={id2} RETURN n1.id AS n1_id, n2.id AS n2_id, exists( (n1)-[:Cites]->(n2) ) AS is_connected";
	} else if (search_field==1){
		var template_nodes_query_results="MATCH (n:Paper) WHERE ANY (m IN {query_array} WHERE m in n.id) RETURN n  ORDER BY n.pagerank LIMIT {limit}";
		var template_group_id="MATCH (child:Paper)<-[:child]-(parent) WHERE child.id={child_id}  RETURN parent.id AS parent_id";
		var template_is_connected="MATCH(n1:Paper), (n2:Paper) WHERE n1.id={id1} and n2.id={id2} RETURN n1.id AS n1_id, n2.id AS n2_id, exists( (n1)-[:Cites]->(n2) ) AS is_connected";
	} else if (search_field==2){
		var template_nodes_query_results="MATCH (n:Paper) WHERE ANY (m IN {query_array} WHERE m in n.title) RETURN n  ORDER BY n.pagerank LIMIT {limit}";
		var template_group_id="MATCH (child:Paper)<-[:child]-(parent) WHERE child.id={child_id}  RETURN parent.id AS parent_id";
		var template_is_connected="MATCH(n1:Paper), (n2:Paper) WHERE n1.id={id1} and n2.id={id2} RETURN n1.id AS n1_id, n2.id AS n2_id, exists( (n1)-[:Cites]->(n2) ) AS is_connected";
	}


	var D3_JSON={};
	var obj_list=[];
	var links_list=[]
	var child_id_list=[];
	var result_length=0;
	var counter1=0;
	var counter2=0;


	var record_id_list=[];


	var session=driver.session();
	session
	  .run( template_nodes_query_results,{query_array:query_array, limit:100 } )
	  .then( function(results){
	  		if (results.records.length==0){
	  			res.send("NOT-FOUND");
	  			return;
	  		}

	  		for (var i in results.records){
	  			result_length+=1;
	  			record_id_list.push( parseInt(results.records[i].toObject().n.properties.id) );
	  		}

	  		results.records.forEach(function(record){
	  			var record_body=record.toObject().n;
	  			var record_id=parseInt(record_body.properties.id)
	  			session
	  				.run(template_group_id,{child_id:record_id})
	  				.then(function(parent_record){

	  					var group_id=parseInt(parent_record.records[0].toObject().parent_id);
		  				var paper={ "title":record_body.properties.title, "keywords":record_body.properties.keywords,
							 "id":parseInt(record_body.properties.id), "metadata":record_body.properties.metadata,
							 "pagerank":parseFloat(record_body.properties.pagerank), "authors":record_body.properties.authors, 
							 "date":record_body.properties.date_, "group_id":group_id };
						obj_list.push(paper);
						counter1++;


						for (var i=0; i<record_id_list.length; i++){

							session
								.run(template_is_connected, {id1:parseInt(record_body.properties.id), id2:record_id_list[i]  })
								.then(function(bool_record){

									if (bool_record.records[0]._fields[2]==true){
										var link={ "source": parseInt( bool_record.records[0]._fields[0]),
												    "target": parseInt( bool_record.records[0]._fields[1]),
												    "value":1 }
										links_list.push(link);
									}

									counter2++;

									if ( links_list!=[] && counter2==result_length && counter1==result_length ){

										size_of_links_list_t1=links_list.length;
										setTimeout(function(){

											D3_JSON={ "nodes":obj_list, "links":links_list  };
											//D3_JSON=JSON.stringify(global_obj,null,2 );
											//print (D3_JSON);
											res.json(D3_JSON);

									  		session.close();
									  		//driver.close();

										}, 2000);
									}
								})
						}
	  				})
	  		})
	  })
}


function handle_search_query (search_query, search_field) {
	var query_array=[];
	for (var i=0; i<search_query.length; i++) {
		var predicate_list=[];
		var predicates=search_query[i].split(" ");
		for (var j=0; j<predicates.length; j++){
			if (predicates[j]!="") {
				if (search_field==0 || search_field==2) {
					predicate_list.push(predicates[j]);
				} else if (search_field==1){
					predicate_list.push( parseInt(predicates[j]) );
				}
			}
		}
		if (search_field==0 || search_field==2){
			query_array.push(predicate_list.join("_"));
		} else if (search_field==1){
			query_array.push(parseInt( predicate_list.join("_")));
		}
	}

	return query_array;
	
}


server.post("/process_search_query", function(req, res){

	var search_query=req.body.search_query.split(",");
	var search_field=parseInt(req.body.search_field);


	query_array=handle_search_query(search_query, search_field);

	process_search_query(query_array, res, search_field);

} )


server.listen(3000, function() {
	console.log("listening on port:3000");
} )


function print (content) {console.log(content)}