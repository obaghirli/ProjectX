def calculate_remaining_time(total_task_size,CA,t_start_loop,t_end_loop,time_list):
	remaining_task_size=len(CA)
	time_taken_prev_task=(t_end_loop-t_start_loop)/60.0
	time_list.append(time_taken_prev_task)

	if remaining_task_size>total_task_size/2.0:
		return remaining_task_size*sum(time_list)/len(time_list)
	else:
		return remaining_task_size * sum(time_list[-remaining_task_size+1:])/len(time_list[-remaining_task_size+1:])



