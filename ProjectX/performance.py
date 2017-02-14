#-----------------------------------------------------------------------------------------------------------
import numpy as np


def true_membership(project_location):
	with open(project_location+"ProjectX/benchmark/community.dat") as etalon:
		lines=etalon.readlines()
	clean_lines=[]
	lines=[line.strip() for line in lines]
	for line in lines:
		if line != "":
			clean_lines.append(line)
	size=len(clean_lines)
	dictionary={}
	for i in range(size):
		[node,community]=clean_lines[i].split()
		node=int(node)-1
		community=int(community)-1
		if community not in dictionary:
			dictionary[community]=list()
		dictionary[community].append(node)

	return (dictionary,size)


def nodetocomm(node,community_pool):
	for index,comm in enumerate( community_pool ):
		if node in comm.members:
			return index



def mismatch(check_list):
	max_freq=0
	check_list=np.array(check_list)
	base_elements=np.unique(check_list)
	for i in range(len(base_elements)):
		freq=np.sum(check_list==base_elements[i])
		if freq>max_freq:
			max_freq=freq
	return len(check_list)-max_freq


def performance(dictionary,community_pool,total_node):
	total_error=0
	size_dictionary=len(dictionary)
	for i in range(size_dictionary):
		 size_member=len( dictionary[i] )
		 check_list=[]
		 for j in range(size_member):
		 	node=dictionary[i][j]
		 	comm=nodetocomm(node,community_pool)
		 	check_list.append(comm)
		 error=mismatch(check_list)
		 total_error=total_error+error
	msg="%d out of %d nodes misrepresented! Success rate %.4f percent" %( total_error,total_node, 100.0-100.0*float(total_error)/total_node )
	return msg


def performance_evaluation(community_pool,project_location):
	(dictionary,total_node)=true_membership(project_location)
	return performance(dictionary,community_pool,total_node)

#--------------------------------------------------------------------------------------------------
