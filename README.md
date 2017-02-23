# ProjectX
## Description 
ProjectX is part of a larger project. ProjectX uses several real world and artificial network datasets, and execute community detection algorithm 
[Fast algorithm for detecting community structure in networks by M.E.J Newman](https://arxiv.org/pdf/cond-mat/0309508.pdf) on them.
Sample datasets are Karate club, Football club, GN benchmark datasets, Dolphin network, Arxiv.org High Energy Physics (untill 2003) datasets.
The input of the program is one of these datasets passed as an argument to main.py function using the terminal. 
The output of the program is the community pool, which holds community objects and each community object holds its members assigned to it.
The program prints the original network and detected communities at the end by default. You can suppress graphs by passing -nodraw argument.
You can also pass one of the datasets of particular interest the same way. e.g python main.py -dolphin -nodraw -mproc 2 .
This command will choose Dolphin network dataset and suppress graphics at the end. If -mproc agrument with a corresponding value is passed, 
then you get the advantage of Multiprocessing, value being the number of requested cpu. This is recommended for large datasets.  
## Version
**Version No: _03**   /  previous releases: _00, _01, _02

**Version_00: Original submission**

**Version_01: Improvements**
* deleting row/col from a matrix in update_CA() function is much more memory efficient
* find_best_pair() function is much faster.
* benchmark datasets, adjacency matrix is now int8 instead of int64 for less memory consumption.
* deleting community_pool, right before its new assignment with np.deepcopy() in the main part of the main.py function 
* arxivhepth dataset is added

**Version_02: Improvements**
* multiprocessing is enabled for the find_best_pair() function which is the most computationally expensive part of the algorithm

**Version_03: Improvements**
* update_CA() function uses logical masks for matrix/array operations, less looping, optimized for sparse matrices
* find_candidate_pairs() functions is written to take load from find_best_pair() function, uses logical masking, and optimized for sparse matrices
* find_best_pair() is now more multiprocessing friendly
* community_pool is not stored im memory, rather joins.txt file is generated to dump best pairs and used to build community_pool at the end, after memory is relieved, decreases peak memory consumption, no need to duplicate large arrays. For large datasets, this improves the execution time of the core algorithm
* ETA(Estimate Time) function was over estimating remaining time for large datasets, is now fixed, and works accurately
* Information on data characteristics is now printed on screen, including: total node number, total edge number, average degree  

## Download and Directory Setup
Download Projectx from [GitHub](https://github.com/orkhanbaghirli/ProjectX.git) and locate in your local machine with the exact same name [ProjectX].
Edit "project.location" file in ProjectX directory and pass the location of ProjectX directory on your local machine. e.g.: 
```
/home/iorkhan/Desktop/Dropbox/    DO NOT FORGET "/" at the end if linux is your environment.
```
## Papers for the original implementation of the algorithm used in this project
* Primary:::[Fast algorithm for detecting community structure in networks](https://arxiv.org/pdf/cond-mat/0309508.pdf)
* Supporting:::[Finding community structure in very large networks](https://arxiv.org/pdf/cond-mat/0408187.pdf)
* Benchmark Datasets:::[Benchmark graphs for testing community detection algorithms](https://arxiv.org/pdf/0805.4770.pdf)


## Linux Commands
```
python main.py -GN   // this will use GN Benchmark datasets and will print the graphs at the end 
python main.py -ARG  // e.g. ARG can be any of TEST or KARATE or DOLPHIN or FOOTBALL or ARXIVHEPTH datasets, do not forget the dash(-)

python main.py -GN -nodraw  //-nodraw exits silently without graphs, if used, you will NOT get any graphs
python main.py -TEST -nodraw // this will use "TEST" dataset and will NOT print the graphs 

python main.py // exactly same as the first command, this will use GN dataset [network.dat, community.dat] by default [at location: ~/ProjectX/benchmark] and will print the graphs

python main.py -GN -mproc 4 // enables multiprocessing with 4 cpu

```

## Installation and System Requirements
* Python 2.7.x //tested on version 2.7.12
* pip
* matplotlib library
* numpy library
* scipy library
* igraph library

How to install pip:
```
sudo apt-get update
sudo apt-get install python-pip python-dev build-essential
sudo pip install --upgrade pip
```
How to install matplotlib:
```
sudo apt-get update
sudo python -m pip install matplotlib
```
How to install numpy:
```
sudo apt-get update
sudo python -m pip install numpy
```
How to install scipy:
```
sudo apt-get update
sudo python -m pip install scipy
```
How to install igraph:
```
sudo add-apt-repository ppa:igraph/ppa
sudo apt-get update
sudo apt-get install python-igraph
```

## Girvan Newman (GN) Benchmark Dataset Generation
Note: The package comes with a sample GN dataset [network.dat, community.dat] at location: ~/ProjectX/benchmark.
You do not need to generate a new dataset if you do not need a new dataset.
Before you generate a new dataset, copy [network.dat, community.dat, statistics.dat] files at ~/ProjectX/benchmark to ~/ProjectX/benchmark/TEST_NETWORK/TEST directory for future references.
main.py will only use datasets [network.dat, community.dat] at location: ~/ProjectX/benchmark.

How to generate GN Benchmark Dataset:
The following commands will use [parameters.dat,bech_seed.dat and others] and generate [network.dat,community.dat and statistics.dat].
```
cd ~/ProjectX/benchmark
make
./benchmark

```
Note: make sure that ./benchmark does not give you any WARNING. Typical warning includes "... took too long ..." if this happens, edit the parameters in parameters.dat file untill you recieve no WARNINGS.  
Note: main.py uses only [network.dat] to build the graph and [community.dat] to do the performance evaluation as community.dat is the true community assignments of the benchmark dataset.


## Filesystem

* main.py  // core algorithm 
* benchmark.py // functions to generate Adjacency Matrix from several .txt and .dat data files 
* performance.py // functions to perform performance evaluation
* ETA.py // functions estimating the remaining time
* summary.py // functions handling most of the print statements including statistics 
* draw.py // functions to plot Adjacency Matrix (scatter plot), build graph (before community detection and after community detection), plot evolution of Q factor
* multiprocess.py // functions to check the availability of multiprocessing, enable multiprocessing and handle the values returned by the multiprocessed functions. 

* karate.txt  //Karate Club dataset
* dolphin.txt  //Dolphin Network dataset
* football.txt //American Football Association dataset 
* arxivhepth.txt //Arxiv dataset, High Energy Physics +27,000 nodes, +350,000 edges
* project.location //this file stores the location of "ProjectX" on your local machine, YOU HAVE TO EDIT IT and do not forget "/" at the end (for Linux)
* benchmark //This directory stores all required files for GN dataset generation and performance evaluation
* joins.txt file is generated during community detection and is vital part of it. It stores best pairs, and is used to replay the joins, to build the communities at the end of the program flow. 

## Notes on ADJACENCY MATRIX
ADJACENCY MATRIX matrix must be:
* square 
* symmetrical
* zero diagonal | no self-reference
* each node must have at least one connection | no isolated communities | this requirement exists for this version of the software. Can easily be modified to handle isolated communities as well  

