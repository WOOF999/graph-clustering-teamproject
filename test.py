import time
import math
import random
import sys
import numpy as np

# elapsed time
start = time.time()

# global variable
G = dict()
subgraphs = list()
temp = list()  # save pre cluster to compare graph entropy
clusters = list()
initial_cluster = list()
final_cluster = list()

#evaluation
assignment5_output=list()
assignment6_output=list()
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

def calculate_F1_score(cluster):
    f1_score_list=list()
    sum_f1_score=0
    for cluster_index in range(len(cluster)):
        cluster_set=set(cluster[cluster_index])
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

def select_seed_vertex(graph):  # seed vertex random select
    return graph[random.randint(0, len(graph)-1)]

def calculate_clustering_coefficient(subgraph):
    clustering_coefficient_list=list()
    for key in subgraph:
        actual_edge=0
        temp=list()
        Vi=G[key]
        NVi=len(Vi)
        neighbors_list=list(Vi)
        for neighbors_index1 in range(len(Vi)-1):
            for neighbors_index2 in range(neighbors_index1,len(Vi)):
                if neighbors_list[neighbors_index1] in G[neighbors_list[neighbors_index2]]:
                    actual_edge+=1
        if actual_edge==0:
            continue
        temp.append(key)
        temp.append(actual_edge/(NVi*(NVi-1)/2))
        clustering_coefficient_list.append(temp)
    #return max(clustering_coefficient_list,key = lambda x:x[1])
    return clustering_coefficient_list   

def make_seed_cluster(seed):
    temp_c = list()
    temp_c.append(seed)
    temp_c.extend(list(G[seed]))
    return temp_c

def check_neighbors(seed_cluster):
    temp_c = list()
    for i in range(1, len(seed_cluster)):
        temp_c.extend(list(G[seed_cluster[i]]))
    temp_set=set(temp_c)
    seed_cluster_set=set(seed_cluster)
    temp_set=temp_set-seed_cluster_set
    temp_c=list(set(temp_set))
    return temp_c

def merging_vertex(seed_cluster,vertex_list):
    cluster=seed_cluster
    for i in range(len(vertex_list)):
        cluster.append(vertex_list[i][0])
    return cluster

def find_max_edge_vertex(seed_cluster,neighbors_list):
    max_edge_vertex_list=list()
    temp=list()
    for key in neighbors_list:
        max_edge_num=0
        for seed_vertex in seed_cluster:
            if key in G[seed_vertex]:
                max_edge_num+=1
        temp.append(key)
        temp.append(max_edge_num)
        max_edge_vertex_list.append(temp)
        temp=list()
    return max_edge_vertex_list

def check_max_edge_list(max_edge_vertex):
    max_edge_list=sorted(max_edge_vertex, key = lambda x:x[1],reverse=True)
    max_edge_num=max_edge_list[0][1]
    for i in range(len(max_edge_list)):
        if max_edge_list[i][1]<max_edge_num:
            del max_edge_list[i:len(max_edge_list)]
            break
    return max_edge_list
        


def check_vertex_degree(max_edge_vertex):
    max_degree_list=list()
    for i in range(len(max_edge_vertex)):
        max_edge_vertex[i][1]=len(G[max_edge_vertex[i][0]])

    max_degree_list=sorted(max_edge_vertex, key = lambda x:x[1],reverse=True)
    max_degree_num=max_degree_list[0][1]
    for i in range(len(max_degree_list)):
        if max_degree_list[i][1]<max_degree_num:
            del max_degree_list[i:len(max_degree_list)]
            break
    return max_degree_list

def calculate_density(subGraph):
    vertex_num=len(subGraph)
    if vertex_num==1:
        return 0
    edge_num=0
    for node1 in range(vertex_num-1):
        for node2 in range(node1+1,vertex_num):
            if subGraph[node2] in G[subGraph[node1]]:
                edge_num+=1
    return 2*edge_num/(vertex_num*(vertex_num-1))    

def make_output_txt_file():
    cluster_f = open('TeamProject_output.txt', 'a')
    for cluster in final_cluster:
        cluster_f.write(str(len(cluster)))
        cluster_f.write(": ")
        for point in cluster:
            cluster_f.write(point)
            cluster_f.write(" ")
        cluster_f.write("\n")
    cluster_f.close()


def main():
    print(len(G))
    nodes = list(G.keys())  # input data 로부터 subgraph 분류
    count = 0
    while len(nodes) > 0:
        subgraphs.append(bfs(G, nodes[0]))
        for value in subgraphs[count]:
            nodes.remove(value)
        count += 1
    for i in range(len(subgraphs)):
        subgraphs[i] = sorted(subgraphs[i])

    for i in range(len(subgraphs)):  # subgraph 별로 clustering 진행
        clustering_coefficient_list = calculate_clustering_coefficient(subgraphs[i])
        clustering_coefficient_list = sorted(clustering_coefficient_list, key = lambda x:x[1],reverse=True)
        max_coefficient=clustering_coefficient_list[0][1]
        for k in range(len(clustering_coefficient_list)):
            if clustering_coefficient_list[k][1]<max_coefficient:
                del clustering_coefficient_list[k:len(clustering_coefficient_list)]
                break

        for index in range(len(clustering_coefficient_list)):
            if index==198:
                print("test")
            seed_vertex=clustering_coefficient_list[index][0]
            count=0
            for cluster_index in range(len(final_cluster)):
                if seed_vertex in final_cluster[cluster_index]:
                    count+=1
            if len(clustering_coefficient_list)-index==count:
                break
            else:
                index+=count
            seed_vertex=clustering_coefficient_list[index][0]
            seed_cluster = make_seed_cluster(seed_vertex)    
            neighbors = check_neighbors(seed_cluster)
            if len(neighbors)==0:
                final_cluster.append(seed_cluster)
                break
            max_edge_list = find_max_edge_vertex(seed_cluster,neighbors)
            max_edge_list = check_max_edge_list(max_edge_list)
            vertex_list = check_vertex_degree(max_edge_list)
            seed_cluster=merging_vertex(seed_cluster,vertex_list)
            curr_density=calculate_density(seed_cluster)
            pre_density=10
            
            while curr_density<pre_density:
                pre_density=curr_density
                count=0
                for cluster_index in range(len(final_cluster)):
                    if seed_vertex in final_cluster[cluster_index]:
                        count+=1
                if len(clustering_coefficient_list)-index==count:
                    break
                else:
                    index+=count
                seed_vertex=clustering_coefficient_list[index][0]
                seed_cluster = make_seed_cluster(seed_vertex)
                neighbors = check_neighbors(seed_cluster)
                max_edge_list = find_max_edge_vertex(seed_cluster,neighbors)
                max_edge_list = check_max_edge_list(max_edge_list)
                vertex_list = check_vertex_degree(max_edge_list)
                seed_cluster=merging_vertex(seed_cluster,vertex_list)
                curr_density=calculate_density(seed_cluster)
            seed_set=set(seed_cluster)
            final_cluster.append(list(seed_set))
            print(".....make final cluster.....")


    print(final_cluster)
    

    #print(calculate_F1_score(assignment5_output))
    #print(calculate_F1_score(assignment6_output))
    #print(calculate_F1_score(final_cluster))

    print("elapsed time : ", end='')
    print(f"{time.time() - start:.6f} sec")

    #final_cluster.sort()
    #final_cluster.sort(key=len,reverse=True)
    #make_output_txt_file()


if __name__ == "__main__":
    main()