import time
import math
import random
import sys
import numpy as np

# elapsed time
start = time.time()

# global variable
G = dict()
G_cut=dict()
subgraphs = list()
temp = list()  # save pre cluster to compare graph entropy
clusters = list()
initial_cluster = list()
#final_cluster = list()

#evaluation
assignment5_output=list()
assignment6_output=list()
TeamProject_output=list()
ground_truth=list()

# make graph
with open("gene.txt", 'r') as file:
    for line in file:
        n1, n2 = line.strip().split('\t')
        try:
            G[n1].add(n2)
        except KeyError:
            G[n1] = {n2}
        try:
            G[n2].add(n1)
        except KeyError:
            G[n2] = {n1}

#make evaluation set
with open("assignment5_output.txt", 'r') as file:
    for line in file:
        assignment5_output.append(line.split())
    for i in range(len(assignment5_output)):
        del assignment5_output[i][0]

with open("assignment6_output.txt", 'r') as file:
    for line in file:
        assignment6_output.append(line.split())
    for i in range(len(assignment6_output)):
        del assignment6_output[i][0]

with open("ground_truth.txt", 'r') as file:
    for line in file:
        ground_truth.append(line.split())

with open("TeamProject_output.txt", 'r') as file:
    for line in file:
        TeamProject_output.append(line.split())
    for i in range(len(TeamProject_output)):
        del TeamProject_output[i][0]

def calculate_F1_score(cluster):
    f1_score_list=list()
    sum_f1_score=0
    for cluster_index in range(len(cluster)):
        cluster_set=set(cluster[cluster_index])
        f1_score_list.clear()
        for ground_truth_index in range(len(ground_truth)):
            ground_truth_set=set(ground_truth[ground_truth_index])
            TP=len(ground_truth_set&cluster_set)
            if TP==0:
                continue
            FP=len(cluster_set-ground_truth_set)
            FN=len(ground_truth_set-cluster_set)
            precision=TP/(TP+FP)
            recall=TP/(TP+FN)
            f1_score=2*precision*recall/(precision+recall)
            f1_score_list.append(f1_score)
        if len(f1_score_list)==0:
            continue
        else:
            sum_f1_score+=max(f1_score_list)
    return sum_f1_score/len(cluster)

def bfs(graph, start):  # 탐색 알고리즘
    visited = list()
    queue = [start]

    while queue:
        n = queue.pop(0)
        if n not in visited:
            visited.append(n)
            queue += graph[n] - set(visited)
    return visited



def check_neighbors(node1,node2):
    temp_1 = G[node1]
    temp_2 = G[node2]

    temp_c = temp_1&temp_2
    temp_c = list(temp_c)
    return temp_c

def calculate_weight():
    weight_list=list()
    with open("gene.txt", 'r') as file:
        for line in file:
            weight=0
            temp=list()
            n1, n2 = line.strip().split('\t')
            temp.append(n1)
            temp.append(n2)
            weight=calculate_RA_index(check_neighbors(n1,n2))
            temp.append(weight)
            weight_list.append(temp)
    return weight_list

        
def cut_edge_weight1(weight_list):
    for i in range(len(weight_list)):
        if weight_list[i][2]!=1:
            try:
                G_cut[weight_list[i][0]].add(weight_list[i][1])
            except KeyError:
                G_cut[weight_list[i][0]]={weight_list[i][1]}
            try:
                G_cut[weight_list[i][1]].add(weight_list[i][0])
            except KeyError:
                G_cut[weight_list[i][1]]={weight_list[i][0]}
    return G_cut
            
            

def calculate_RA_index(neighbors):
    RA_index=0
    for i in range(len(neighbors)):
        degree=len(G[neighbors[i]])
        RA_index+=1/degree
    if RA_index==0:
        return 1
    return RA_index
    


def make_output_txt_file(final_cluster):
    cluster_f = open('TeamProject_output.txt', 'w')
    for cluster in final_cluster:
        cluster_f.write(str(len(cluster)))
        cluster_f.write(": ")
        for point in cluster:
            cluster_f.write(point)
            cluster_f.write(" ")
        cluster_f.write("\n")
    cluster_f.close()


def main():
    weight_list=list()
    weight_list=calculate_weight()
    print(cut_edge_weight1(weight_list))
    
    nodes = list(G_cut.keys())  # input data 로부터 subgraph 분류
    count = 0
    while len(nodes) > 0:
        subgraphs.append(bfs(G_cut, nodes[0]))
        for value in subgraphs[count]:
            nodes.remove(value)
        count += 1
    
    for i in range(len(subgraphs)):
        subgraphs[i] = sorted(subgraphs[i])  

    make_output_txt_file(subgraphs)
   
    #print(calculate_F1_score(assignment5_output))
    #print(calculate_F1_score(assignment6_output))
    print(calculate_F1_score(TeamProject_output))   
    print(len(ground_truth[0]))
    
    print("elapsed time : ", end='')
    print(f"{time.time() - start:.6f} sec")

    #final_cluster.sort()
    #final_cluster.sort(key=len,reverse=True)
    #make_output_txt_file()


if __name__ == "__main__":
    main()