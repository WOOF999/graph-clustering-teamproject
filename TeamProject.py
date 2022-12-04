import time

# elapsed time
start = time.time()

#evaluation
assignment5_output=list()
assignment6_output=list()
TeamProject_output=list()
ground_truth=list()

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
            precision = TP/len(cluster_set)
            recall = TP/len(ground_truth_set)
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

def calculate_clustering_coefficient(graph, subgraph):
    clustering_coefficient_list = list()
    for key in subgraph:
        actual_edge = 0
        temp = list()
        Vi = graph[key]
        NVi = len(Vi)
        neighbors_list = list(Vi)
        for neighbors_index1 in range(len(Vi) - 1):
            for neighbors_index2 in range(neighbors_index1, len(Vi)):
                if neighbors_list[neighbors_index1] in graph[neighbors_list[neighbors_index2]]:
                    actual_edge += 1
        if actual_edge == 0:
            continue
        temp.append(key)
        temp.append(actual_edge / (NVi * (NVi - 1) / 2))
        clustering_coefficient_list.append(temp)
    return clustering_coefficient_list


def make_seed_cluster(graph, seed):
    temp_c = list()
    temp_c.append(seed)
    temp_c.extend(list(graph[seed]))
    return temp_c


def check_neighbors(graph, seed_cluster):
    temp_c = list()
    for i in range(1, len(seed_cluster)):
        temp_c.extend(list(graph[seed_cluster[i]]))
    temp_set = set(temp_c)
    seed_cluster_set = set(seed_cluster)
    temp_set = temp_set - seed_cluster_set
    temp_c = list(set(temp_set))
    return temp_c

def find_max_edge_vertex(graph, seed_cluster, neighbors_list):
    max_edge_vertex_list = list()
    temp = list()
    for key in neighbors_list:
        max_edge_num = 0
        for seed_vertex in seed_cluster:
            if key in graph[seed_vertex]:
                max_edge_num += 1
        temp.append(key)
        temp.append(max_edge_num)
        max_edge_vertex_list.append(temp)
        temp = list()
    return max_edge_vertex_list

def check_vertex_degree(graph, max_edge_vertex):
    max_degree_list = list()
    for i in range(len(max_edge_vertex)):
        max_edge_vertex[i][1] = len(graph[max_edge_vertex[i][0]])

    max_degree_list = sorted(max_edge_vertex, key=lambda x: x[1], reverse=True)
    max_degree_num = max_degree_list[0][1]
    for i in range(len(max_degree_list)):
        if max_degree_list[i][1] < max_degree_num:
            del max_degree_list[i:len(max_degree_list)]
            break
    return max_degree_list

def calculate_density(graph, subgraph):
    vertex_num = len(subgraph)
    if vertex_num == 1:
        return 0
    edge_num = 0
    for node1 in range(vertex_num - 1):
        for node2 in range(node1 + 1, vertex_num):
            if subgraph[node2] in graph[subgraph[node1]]:
                edge_num += 1
    return 2 * edge_num / (vertex_num * (vertex_num - 1))


def make_output_txt_file(final_cluster):
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

    final_cluster = list()

    # graph 생성
    G = dict()
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

    # input data 로부터 subgraph 분류
    subgraphs = list()
    nodes = list(G.keys())
    count = 0
    while len(nodes) > 0:
        subgraphs.append(bfs(G, nodes[0]))
        for value in subgraphs[count]:
            nodes.remove(value)
        count += 1
    for i in range(len(subgraphs)):
        subgraphs[i] = sorted(subgraphs[i])

    # subgraph 선택 후 clustering 작업 수행
    for i in range(len(subgraphs)):

        # clustering coefficient 측정
        clustering_coefficient_list = list()
        clustering_coefficient_list = calculate_clustering_coefficient(G, subgraphs[i])

        # clustering coefficient가 측정되지 않을 경우 final cluster로 분리 후 다음 subgraph로 이동
        if len(clustering_coefficient_list) == 0:
            final_cluster.append(subgraphs[i])
            continue

        while True:

            # 후보 node가 더 이상 없을 시 stop
            if len(subgraphs[i]) == 0:
                break

            # clustering coefficient 측정
            clustering_coefficient_list = list()
            clustering_coefficient_list = calculate_clustering_coefficient(G, subgraphs[i])

            # clustering coefficient가 측정되지 않을 경우 final cluster로 분리 후 다음 subgraph로 이동
            if len(clustering_coefficient_list) == 0:
                final_cluster.append(subgraphs[i])
                break

            # max clustering coefficient 측정
            value_list = list()
            for j in range(len(clustering_coefficient_list)):
                value_list.append(clustering_coefficient_list[j][1])
            max_clustering_coefficient = max(value_list)

            # clustering coefficient 값이 최대치인 node들 골라내기
            seed_list = list()
            for j in range(len(clustering_coefficient_list)):
                if clustering_coefficient_list[j][1] == max_clustering_coefficient:
                    seed_list.append(clustering_coefficient_list[j][0])

            # 골라진 seed node들로 cluster 만들기
            for j in range(len(seed_list)):

                # 만약 해당 seed node가 만들어진 cluster 안에 포함되어 있다면 다음 seed node로 넘어가기
                temp_list = list()
                for k in range(len(final_cluster)):
                    temp_list.extend(final_cluster[k])
                if seed_list[j] in temp_list:
                    continue

                # seed cluster 생성
                seed_cluster = list()
                seed_cluster = make_seed_cluster(G, seed_list[j])

                # density 저장
                pre_density = calculate_density(G, seed_cluster)

                # iterative part
                while True:

                    # seed cluster의 neighbor들 골라내기
                    neighbors = list()
                    neighbors = check_neighbors(G, seed_cluster)

                    # neighbor가 하나도 없을 경우 stop
                    if len(neighbors) == 0:
                        break

                    # neighbor들 중 seed cluster와 연결된 edge가 가장 많은 neighbor 골라내기
                    max_edge_list = list()
                    max_edge_list = find_max_edge_vertex(G, seed_cluster, neighbors)

                    # 병합 과정
                    # max edge를 가진 node가 하나만 있을 경우
                    if len(max_edge_list) == 1:
                        seed_cluster.append(max_edge_list[0][0])

                        # density 측정
                        density = calculate_density(G, seed_cluster)

                        # density가 증가하지 않을 시 stop
                        if density < pre_density:
                            seed_cluster.remove(max_edge_list[0][0])
                            break
                        # 증가할 시 density 저장 후 continue
                        else:
                            pre_density = density
                    # max edge를 가진 node가 여러 개일 경우
                    else:
                        # max edge를 가진 node들의 degree 측정
                        max_degree_list = list()
                        max_degree_list = check_vertex_degree(G, max_edge_list)

                        # degree가 가장 큰 node가 하나만 있을 경우
                        if len(max_degree_list) == 1:
                            seed_cluster.append(max_degree_list[0][0])

                            # density 측정
                            density = calculate_density(G, seed_cluster)

                            # density가 증가하지 않을 시 stop
                            if density < pre_density:
                                seed_cluster.remove(max_degree_list[0][0])
                                break
                            # 증가할 시 density 저장 후 continue
                            else:
                                pre_density = density
                        # degree가 가장 큰 node가 여러 개일 경우
                        else:
                            for k in range(len(max_degree_list)):
                                seed_cluster.append(max_degree_list[k][0])

                            # density 측정
                            density = calculate_density(G, seed_cluster)

                            # density가 증가하지 않을 시 stop
                            if density < pre_density:
                                for k in range(len(max_degree_list)):
                                    seed_cluster.remove(max_degree_list[k][0])
                                break
                            # 증가할 시 density 저장 후 continue
                            else:
                                pre_density = density

                # 병합이 끝났을 시 final cluster로 분리 후 선택된 subgraph의 후보 노드에서 제외
                final_cluster.append(seed_cluster)
                for k in range(len(final_cluster[-1])):
                    if final_cluster[-1][k] not in subgraphs[i]:
                        continue
                    subgraphs[i].remove(final_cluster[-1][k])

    for i in range(len(final_cluster)):
        print(calculate_density(G, final_cluster[i]))
        if calculate_density(G, final_cluster[i]) == 1:
            count += 1

    # output 파일 추출
    make_output_txt_file(final_cluster)

    # make evaluation set
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

    # f score 계산
    print(calculate_F1_score(assignment5_output))
    print(calculate_F1_score(assignment6_output))
    print(calculate_F1_score(TeamProject_output))

    # elapsed 시간 측정
    print("elapsed time : ", end='')
    print(f"{time.time() - start:.6f} sec")

if __name__ == "__main__":
    main()
