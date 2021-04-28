# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 12:42:15 2021

@author: hulkb
"""
%matplotlib inline
import networkx as nx
import matplotlib.pyplot as plt




#read the p2p model sample data file
N=nx.read_edgelist("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 4/outputsample.dat")
graphviz_pos=nx.spring_layout(N)

#draw the model image, plotting the p2p sample networks
nx.draw(N, graphviz_pos, node_size = 150, node_color='black')
#save the graph on a figure file
plt.savefig("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 4/p2psample.png", dpi=200)

#print out the nodes
print(N.nodes())

#print out the number of nodes of our graph
print(N.number_of_nodes())

#print out the number of edges of our graph
print(N.number_of_edges())

#find the degree centrality
degree_centrality=nx.degree(N)
print('Total degree centrality is',degree_centrality)

# testing node: 1 's degree centrality
print(degree_centrality['1'])

# print out each node's degree centrality
for i in N.nodes():
    print(i + "'s degree centrality is", degree_centrality[i])
    
# getting degree centrality image
l=[]
res={item[0]:item[1] for item in degree_centrality}
for n in N.nodes():
    if n not in res:
        res[n] = 0
    l.append(res[n])

nx.draw_networkx_edges(N, graphviz_pos)
for n in N.nodes():
    list_nodes=[n]
    color = str( (res[n]-min(l))/float((max(l)-min(l))) ) 
    nx.draw_networkx_nodes(N, {n:graphviz_pos[n]}, [n], node_size = 100, \
    node_color =
    color)

plt.savefig("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 4/sample_degree_200.png",dpi=200)

print()
# print the res dictionary
print(res)

# check if they satisfy degree centrality
def check_degree(res):
    for k, v in res.items():
        if res[k] == degree_centrality[k]:
            return True

print(check_degree(res))

# calculate the distance from a root node
def node_distance(G,root_node):
    queue=[]
    list_distances=[]
    queue.append(root_node)
    #deleting the old keys
    if 'distance' in G.nodes[root_node]:
        for n in G.nodes():
            del G.nodes[n]['distance']
    G.nodes[root_node]["distance"]=0
    while len(queue):
        working_node=queue.pop(0)
        for n in G.neighbors(working_node):
            if len(G.nodes[n])==0:
                G.nodes[n]["distance"]=G.nodes[working_node] \
                ["distance"]+1
                queue.append(n)
    for n in G.nodes():
        list_distances.append(((root_node,n),G.nodes[n]["distance"]))
    return list_distances

#check if this function works, use node '1'
list_distances1 = node_distance(N, '1')
print(list_distances1)

#print out the distance between root node and other nodes
def each_node_distance(G, root_node):
    list_distances = node_distance(G, root_node)
    for i in range(len(list_distances)):
        print('the distance between', list_distances[i][0][0] ,'and',list_distances[i][0][1], \
              'is', list_distances[i][1])


#a sample that if we want to know the distance between '1' and other nodes
each_node_distance(N, '1')

print()

#to get the closeness centrality
norm=0.0
diz_c={}
l_values=[]
for n in N.nodes():
    l=node_distance(N,n)
    ave_length=0
    for path in l:
        ave_length+=float(path[1])/(N.number_of_nodes()-1-0)
    norm+=1/ave_length
    diz_c[n]=1/ave_length
    l_values.append(diz_c[n])

#visualization
nx.draw_networkx_edges(N, graphviz_pos)
for n in N.nodes():
    list_nodes=[n]
    color = str((diz_c[n]-min(l_values))/(max(l_values)- \
                                          min(l_values)))
    nx.draw_networkx_nodes(N, {n:graphviz_pos[n]}, [n], node_size = \
                           100, node_color = color)
#save the image
plt.savefig("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 4/sample_closeness_200.png",dpi=200)

# to get the betweenness centrality
list_of_nodes=[n for n in N.nodes()]
num_of_nodes= N.number_of_nodes()
bc={} #we will need this dictionary later on
for i in range(num_of_nodes-1):
    for j in range(i+1,num_of_nodes):
        paths=nx.all_shortest_paths(N, source=list_of_nodes[i], \
                                    target=list_of_nodes[j])
        count=0.0
        path_diz={}
        for p in paths:
            #print p
            count += 1.0
            for n in p[1:-1]:
                if n not in path_diz:
                    path_diz[n]=0.0
                path_diz[n] += 1.0
        for n in path_diz:
            path_diz[n]=path_diz[n]/count
            if n not in bc:
                bc[n]=0.0
            bc[n] += path_diz[n]  


#visualization
l=[]
res=bc
for n in N.nodes():
    if n not in res:
        res[n]=0.0
    l.append(res[n])

nx.draw_networkx_edges(N, graphviz_pos)
for n in N.nodes():
    list_nodes=[n]
    color = str( (res[n]-min(l))/(max(l)-min(l)) ) 
    nx.draw_networkx_nodes(N, {n:graphviz_pos[n]}, [n], node_size = 100, \
                           node_color = color)

plt.savefig("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 4/sample_betweenness_200.png",dpi=200)



#networkx eigenvector centrality
centrality=nx.eigenvector_centrality_numpy(N)

#visualization
l=[]
res=centrality
for n in N.nodes():
    if n not in res:
        res[n]=0.0
    l.append(res[n])

nx.draw_networkx_edges(N, graphviz_pos)
for n in N.nodes():
    list_nodes=[n]
    color = str( (res[n]-min(l))/(max(l)-min(l)) ) 
    nx.draw_networkx_nodes(N, {n:graphviz_pos[n]}, [n], node_size = 100, \
    node_color = color)
#save the image
plt.savefig("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 4/sample_eigenvetor_200.png",dpi=200)

#get giant connected component
def giant_component_size(G_input):
    
    G=G_input.copy()
    
    components=[]

    node_list=[i for i in G.nodes()]

    while len(node_list)!=0:
        root_node=node_list[0]
        component_list=[]
        component_list.append(root_node)
        queue=[]
        queue.append(root_node)
        G.nodes[root_node]["visited"]=True
        while len(queue):
            working_node=queue.pop(0)
            for n in G.neighbors(working_node):
                #check if any node attribute exists
                if len(G.nodes[n])==0:
                    G.nodes[n]["visited"]=True
                    queue.append(n)
                    component_list.append(n)
        components.append((len(component_list),component_list))
        #remove the nodes of the component just discovered
        for i in component_list: node_list.remove(i)
    components.sort(reverse=True)

    GiantComponent=components[0][1]
    SizeGiantComponent=components[0][0]
    
    return GiantComponent,len(components)

(GCC, num_components)=giant_component_size(N)
print("Giant Connected Component:", GCC)
print("Number of components:",num_components)

# Make a copy 

import copy

#copy node list function
def breaking_graph(H,node_list):
    #define the new graph as the subgraph induced by the GCC
    n_l=copy.deepcopy(node_list)
    #iterate deleting from the GCC while the graph comprises 
    #one component (num_components=1)
    num_components=1
    count=0
    while num_components==1:
        count+=1
        #node_to_delete=random.choice(H.nodes()) #select at random an element in the node list
        #select a node according to the betweenness ranking 
        #(the last in the list)
        node_to_delete=n_l.pop() 
        H.remove_node(node_to_delete)
        #(GCC,num_components)=giant_component_size(H)
        num_components=nx.number_connected_components(H)
    return count

random_list=list(copy.deepcopy(N.nodes()))

print(random_list)

c = breaking_graph(N, random_list)
#print the copy nodes count
print('the copy nodes count is',c)
























