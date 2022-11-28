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
with open("test.txt", 'r') as file:
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

def make_seed_cluster(seed):
    temp_c = list()
    temp_c.append(seed)
    temp_c.extend(list(G[seed]))
    return temp_c

def check_neighbors(seed_cluster):
    temp_c = list()
    for i in range(1, len(seed_cluster)):
        temp_c.extend(list(G[seed_cluster[i]]))
    temp_c = list(set(temp_c))
    temp_c.remove(seed_cluster[0])
    return temp_c


def calculate_graph_entropy(seed_cluster, neighbors):
    graph_entropy = list()
    # Vertex entropy e(v)=-pi(v)log2(pi(v))-po(v)log2(po(V))

    for i in range(len(neighbors)):
        sum_of_edges = len(G[neighbors[i]])
        sum_of_innerlinks = len(G[neighbors[i]] & set(seed_cluster))
        sum_of_outerlinks = len(G[neighbors[i]] - set(seed_cluster))
        pi = round(sum_of_innerlinks / sum_of_edges, 3)
        po = round(sum_of_outerlinks / sum_of_edges, 3)
        if po == 0:
            continue
        else:
            shan_val_in = pi * math.log2(pi)
            shan_val_out = po * math.log2(po)
            vertex_entropy = -shan_val_in-shan_val_out
            graph_entropy.append(vertex_entropy)
    for i in range(1, len(seed_cluster)):
        if G[seed_cluster[i]] < set(seed_cluster) is True:
            continue
        else:
            sum_of_edges = len(G[seed_cluster[i]])
            sum_of_innerlinks = len(G[seed_cluster[i]] & set(seed_cluster))
            sum_of_outerlinks = len(G[seed_cluster[i]] - set(seed_cluster))
            pi = sum_of_innerlinks / sum_of_edges
            po = sum_of_outerlinks / sum_of_edges
            if po == 0:
                continue
            else:
                shan_val_in = pi * math.log2(pi)
                shan_val_out = po * math.log2(po)
                vertex_entropy = -shan_val_in - shan_val_out
                graph_entropy.append(vertex_entropy)
    # Graph entropy e(G(V,E))=SUM(e(v))
    return sum(graph_entropy)

def compare_graph_entropy(init_entropy, fin_entropy):
    if init_entropy > fin_entropy:
        return 1
    else:
        return 0

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

        pass_count = 0  # entropy 값이 모두 0이 나오는 지 여부

        if len(subgraphs[i]) < 4:  # subgraph의 vertex 개수가 3개 이하면 pass
            continue

        while True:

            if len(subgraphs[i]) == 0 or pass_count == 1:  # subgraph에 남아있는 clustering 안된 vertex가 없거나 entropy 값이 모두 0이 나올 시 stop
                break

            seed_vertex = select_seed_vertex(subgraphs[i])
            seed_cluster = make_seed_cluster(seed_vertex)
            neighbors = check_neighbors(seed_cluster)
            init_entropy = calculate_graph_entropy(seed_cluster, neighbors)
            if init_entropy == 0:
                break
            entropy_history = list()
            entropy_history.append(init_entropy)

            while True:

                entropys = list()  # neighbor 하나씩 병합하며 entropy 값 확인
                for j in range(len(neighbors)):
                    temp_seed_cluster = seed_cluster
                    if neighbors[j] in temp_seed_cluster:
                        continue
                    temp_seed_cluster.append(neighbors[j])  # neighbor 중 1개 merge
                    temp_neighbors = check_neighbors(temp_seed_cluster)
                    temp_entropy = calculate_graph_entropy(temp_seed_cluster, temp_neighbors)
                    if temp_entropy > entropy_history[-1]:
                        entropys.append(100)
                    else:
                        entropys.append(temp_entropy)

                if sum(entropys) == 0:  # entropy 값이 모두 0이 나오면 stop
                    pass_count = 1
                    break

                min_entropy = min(entropys)
                entropy_history.append(min_entropy)

                if min_entropy == 100:  # 더 이상 graph entropy가 낮아지지 않을 때 클러스터로 분리 후 stop
                    final_cluster.append(seed_cluster)
                    for value in seed_cluster:
                        if value not in subgraphs[i]:
                            continue
                        else:
                            subgraphs[i].remove(value)
                    break

                entropy_history.append(min_entropy)  # entropy 내역에 저장

                for j in range(len(entropys)):  # 병합했을 때 entropy 값이 최소가 되는 neighbor 병합
                    if entropys[j] == min_entropy:
                        seed_cluster.append(neighbors[j])

    sum_of = []
    #for i in range(len(final_cluster)):
        #print(len(final_cluster[i]))
        #sum_of.append(len(final_cluster[i]))
    #print(sum(sum_of))
    #print(final_cluster)

    print(calculate_F1_score(assignment5_output))
    print(calculate_F1_score(assignment6_output))
  
    print("elapsed time : ", end='')
    print(f"{time.time() - start:.6f} sec")

    #final_cluster.sort()
    #final_cluster.sort(key=len,reverse=True)
    #make_output_txt_file()


if __name__ == "__main__":
    main()