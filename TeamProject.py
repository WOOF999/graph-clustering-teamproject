import time
from collections import deque
import sys

#elapsed time
start=time.time()

#global variable
G=dict()
temp=list() #save pre cluster to compare graph entropy
initial_cluster=list() #initial size-3 cluster
final_cluster=list() 

#make graph
with open("gene.txt",'r') as file:
    for line in file:
        n1,n2=line.strip().split('\t')
        try:
            G[n1].add(n2)
        except KeyError:
            G[n1]={n2}
        try:
            G[n2].add(n1)
        except KeyError:
            G[n2]={n1}

def select_seed_vertex():
    pass

def make_seed_cluster():
    pass

def check_neighbors():
    pass

def calculate_graph_entropy():
    #Vertex entropy e(v)=-pi(v)log2(pi(v))-po(v)log2(po(V))
    #Graph entropy e(G(V,E))=SUM(e(v))
    pass

def compare_graph_entropy():
    pass

def merging_vertex(vertex):
    pass

def remove_vertex(vertex):
    pass


def make_output_txt_file():
    cluster_f=open('TeamProject_output.txt','a')
    for cluster in final_cluster:
        cluster_f.write(str(len(cluster)))
        cluster_f.write(": ")
        for point in cluster:
            cluster_f.write(point)
            cluster_f.write(" ")
        cluster_f.write("\n")
    cluster_f.close()


def main():

    print("elapsed time : ",end='')
    print(f"{time.time()-start:.6f} sec")

    

if __name__=="__main__":
    main()