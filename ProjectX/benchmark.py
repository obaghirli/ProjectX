import numpy as np


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
	KARATE=np.zeros((34,34))

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
	FOOTBALL=np.zeros((115,115))

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
	DOLPHIN=np.zeros((62,62))

	for u in range(row):
		[fs1,sc1]=clean_lines[u,0].split()
		[fs2,sc2]=clean_lines[u,1].split()
		DOLPHIN[ int(sc1) , int(sc2) ]=1
		DOLPHIN[ int(sc2) , int(sc1) ]=1

	return DOLPHIN


def gn(project_location):
	clean_lines=[]
	with open(project_location+'ProjectX/benchmark/network.dat') as f:
		lines=f.readlines()
	lines=[x.strip() for x in lines]
	for i in range(len(lines)):
		if lines[i]!="":
			clean_lines.append(lines[i])

	clean_lines=np.array(clean_lines).reshape((len(clean_lines),1))
	(row,col)=clean_lines.shape
	size= int(clean_lines[row-1,0].split()[0])
	GN=np.zeros((size,size))
	for u in range(row):
		[s,t]=clean_lines[u,0].split()
		GN[ int(s)-1 , int(t)-1 ]=1

	return GN




