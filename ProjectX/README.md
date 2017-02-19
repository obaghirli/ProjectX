-------------------------------------------------------------ProjectX----------------------------------------------------------
Version:-----------------------------------------------------------------------------------------------------------------------
Version No: 01   //old:00
Improvements:
1) delete row/col in update_CA() function is more memory efficient
2) find_best_pair() function is much faster
3) benchmark datasets, adjacency matrix is now int8 instead of int64.
4) del community_pool, right before its new assignment with np.deepcopy() in the __name_=__main__ function 
5) arxivhepth dataset is added
-------------------------------------------------------------------------------------------------------------------------------
Directory Setup:---------------------------------------------------------------------------------------------------------------
Download Projectx from GitHub and locate in your local machine with the exact same name
Edit "project.location" file in ProjectX directory. e.g. /home/iorkhan/Desktop/Dropbox/, DO NOT FORGET "/" at the end if linux
-------------------------------------------------------------------------------------------------------------------------------

Papers:------------------------------------------------------------------------------------------------------------------------
Primary:::"Fast algorithm for detecting community structure in networks": link: https://arxiv.org/pdf/cond-mat/0309508.pdf
Supporting:::"Finding community structure in very large networks": link: https://arxiv.org/pdf/cond-mat/0408187.pdf
Benchmark Datasets:::"Benchmark graphs for testing community detection algorithms": link: https://arxiv.org/pdf/0805.4770.pdf
-------------------------------------------------------------------------------------------------------------------------------


Linux Commands:----------------------------------------------------------------------------------------------------------------
python main.py -GN   // this will use GN Benchmark datasets and will print the graphs at the end 
python main.py -ARG  // e.g. ARG can be any of TEST or KARATE or DOLPHIN or FOOTBALL datasets, do not forget the dash(-)

python main.py -GN -nodraw  //-nodraw exits silently without graphs, if used, you will NOT get any graphs
python main.py -TEST -nodraw // this will use "TEST" dataset and will NOT print the graphs 

python main.py // exactly same as the first command, this will use GN dataset [network.dat, community.dat] by default [at location: ~/ProjectX/benchmark] and will print the graphs
-------------------------------------------------------------------------------------------------------------------------------

System Requirements:-----------------------------------------------------------------------------------------------------------
Python 2.7.x //tested on version 2.7.12
pip
matplotlib library
numpy library
scipy library
igraph library

How to install pip:
sudo apt-get update
sudo apt-get install python-pip python-dev build-essential
sudo pip install --upgrade pip

How to install matplotlib:
sudo apt-get update
sudo python -m pip install matplotlib

How to install numpy:
sudo apt-get update
sudo python -m pip install numpy

How to install scipy:
sudo apt-get update
sudo python -m pip install scipy

How to install igraph:
sudo add-apt-repository ppa:igraph/ppa
sudo apt-get update
sudo apt-get install python-igraph
------------------------------------------------------------------------------------------------------------------------------

Girvan Newman (GN) Benchmark Dataset generation:------------------------------------------------------------------------------
Note: The package comes with a sample GN dataset [network.dat, community.dat] at location: ~/ProjectX/benchmark
You do not need to generate a new dataset if you do not need a new dataset
Before you generate a new dataset, copy [network.dat, community.dat, statistics.dat] files at ~/ProjectX/benchmark to ~/ProjectX/benchmark/TEST_NETWORK/TEST directory for future references
main.py will only use datasets [network.dat, community.dat] at location: ~/ProjectX/benchmark

How to generate GN Benchmark Dataset:
The following commands will use [parameters.dat,bech_seed.dat and others] and output [network.dat,community.dat and statistics.dat]

cd ~/ProjectX/benchmark
make
./benchmark

Note: make sure that ./benchmark does not give you any WARNING. Typical warning includes "... took too long ..." if this happens, edit the parameters in parameters.dat file untill you recieve no WARNINGS  
Note: main.py uses only [network.dat] to build the graph and [community.dat] to do the performance evaluation as community.dat is the true community assignments of the benchmark dataset.
------------------------------------------------------------------------------------------------------------------------------

Software:---------------------------------------------------------------------------------------------------------------------

main.py  // core algorithm 
benchmark.py // functions to generate Adjacency Matrix from several .txt and .dat data files 
performance.py // functions to perform performance evaluation
ETA.py // functions estimating the remaining time
summary.py // functions handling most of the print statements including statistics 
draw.py // functions to plot Adjacency Matrix (scatter plot), build graph (before community detection and after community detection), plot evolution of Q factor

karate.txt  //Karate Club dataset
dolphin.txt  //Dolphin Network dataset
football.txt //American Football Association dataset 
arxivhepth.txt //Arxiv dataset, High Energy Physics +27,000 nodes, +350,000 edges
project.location //this file stores the location of "ProjectX" on your local machine, YOU HAVE TO EDIT IT and do not forget "/" at the end (for Linux)
benchmark //This directory stores all required files for GN dataset generation and performance evaluation
------------------------------------------------------------------------------------------------------------------------------

Notes on ADJACENCY MATRIX:----------------------------------------------------------------------------------------------------
ADJACENCY MATRIX matrix must be:
-square 
-symmetrical
-zero diagonal // no self-reference
-each node must have at least one connection // no isolated communities // this requirement exists for this version of the software. Can easily be modified to handle isolated communities as well  
------------------------------------------------------------------------------------------------------------------------------
