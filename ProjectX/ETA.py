def calculate_remaining_time(CA, edge_num, t_start, t_end):
	node_num=len(CA)
	edge_num_per_node=edge_num/node_num
	average_time_per_computation=1.0*(t_end-t_start)/edge_num/60


	remaining_computation_size=0
	edge_num=edge_num-edge_num_per_node
	while node_num>2:
		remaining_computation_size=remaining_computation_size+edge_num
		edge_num=edge_num-edge_num_per_node
		if edge_num<0:
			edge_num=0
		node_num=node_num-1
	return remaining_computation_size*average_time_per_computation