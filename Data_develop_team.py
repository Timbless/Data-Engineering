# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 08:39:49 2021

@author: hulkb
"""





import networkx as nx
import matplotlib.pyplot as plt


file_name = "C:/Users/hulkb/Desktop/Academic/Data Engineering/HW 1/\
HWK 1 - FoodWebs/FoodWebs/data/Data_develop_team.txt"

DG = nx.DiGraph()

in_file=open(file_name,'r')
while True:
    next_line = in_file.readline()
    if not next_line:
        break
    next_line_fields = next_line[:].split(' ')
    node_a = next_line_fields[1]
    node_b = next_line_fields[2]
    print(node_a, node_b)
    DG.add_edge(node_a, node_b)
    
# find the highest position role in Data science team
scc=[(len(c),c) for c in sorted( nx.strongly_connected_components \
                               (DG), key=len, reverse=True)][0][1]
    
print("the highest position in Data science team:", scc)

node_set = [(len(c),c) for c in sorted( nx.strongly_connected_components \
                               (DG), key=len, reverse=True)]
    

# find all nodes in the data team
node_list = []
for i in range(len(node_set)):
    for j in node_set[i][1]:
        node_list.append(j)

print(node_list)

IN_component=[]
for n in scc:
    for s in DG.predecessors(n):
        if s in scc: 
            continue
        if not s in IN_component:
            IN_component.append(s)

print("In_component list",IN_component)

OUT_component=[]
OUT_component = list(set(node_list) - set(IN_component)- scc)


print("OUT_component list", OUT_component)


# use the Breadth First Search algorithm, find the distance form a root node at
# distance d = 0 at successive time steps to get to team final present
# the finaly result should be presented by team leader: team manager

root_node= '0'
queue=[]
queue.append('0')
DG.nodes['0']["distance"]=0
while len(queue):
    working_node=queue.pop(0)
    for n in DG.neighbors(working_node):
        if len(DG.nodes[n])==0:
            DG.nodes[n]["distance"]=DG.nodes[working_node]["distance"]+1
            queue.append(n)
for n in DG.nodes():
    print(n, DG.nodes[n]["distance"])

# remove 0, because 0 represent the data resource that data team collected 
DG.remove_node('0') 
print(DG.nodes())   
nx.draw(DG)

#plt.savefig('Data_develop_team.png')

# role list is the team member role composition
role_list = ['Business Analyst', 'Data analyst', 'Data engineer', 'Data architect', \
             'Data Scientist', 'Machine Learning engineer', 'Team manager']
    

# calculate each role's salary    
def role_salary(DG, role_list):
    node_list = []
    for i in DG.nodes():
        #this is the algorithm for salary, base salary is $60000 for each role, the higher node rank level
        # will get more money, and the more edge means whether those people work together, it also can be a criteria 
        node_list.append(60000 + (int(DG.nodes[i]["distance"])-1)*30000 + (DG.degree(i))*10000)        
    node_dict = dict(zip(role_list, node_list))
    return node_dict
    
salary_dict = role_salary(DG, role_list)

#print the salary list
print("Data team role's salary list")
print()  
for key, value in salary_dict.items():
    print(key, "salary:", value)

#the function to get number of team member who deal with data
def get_node_key(node):
    out_list=[]
    for out_edge in DG.out_edges(node):
        out_list.append(out_edge[1])
    in_list=[]
    for in_edge in DG.in_edges(node):
        in_list.append(in_edge[0])
    out_list.sort()
    out_list.append('-')
    in_list.sort()
    out_list.extend(in_list)
    return out_list


def TrophicNetwork(DG):
    trophic={}
    for n in DG.nodes():
        k=tuple(get_node_key(n))
        if k not in trophic.keys():
            trophic[k]=[]
        trophic[k].append(n)
    for specie in trophic.keys():
        if len(trophic[specie])>1:
            for n in trophic[specie][1:]:
                DG.remove_node(n)
    return DG

TrophicDG = TrophicNetwork(DG)
print()
print("the number of team member who need to deal with data:",TrophicDG.number_of_nodes())
print("the number of team role:",TrophicDG.number_of_edges())
print("the rate of team member who need to work with data:",float(TrophicDG.number_of_edges()) / TrophicDG.number_of_nodes())

#this function is to get the probability of job content of team member role percentage in a team
def compute_classes(DG):
    basal_species=[]
    top_species=[]
    intermediate_species=[]
    for n in DG.nodes():
        if DG.in_degree(n)==0:
            basal_species.append(n)
        elif DG.out_degree(n)==0:
            top_species.append(n)
        else:
            intermediate_species.append(n)
    return (basal_species,intermediate_species,top_species)

(B,I,T)=compute_classes(TrophicDG)
print()
print("the probability of people who only need to submit their work",float(len(B))/(len(B)+len(T)+len(I)))
print("the probability of people who need to work together:",float(len(I))/(len(B)+len(T)+len(I)))
print("the probability of people who have team work result",float(len(T))/(len(B)+len(T)+len(I)))

# calculate the probability between two group of team member
def InterclassLinkProportion(DG,C1,C2):
    count=0
    for n1 in C1:
        for n2 in C2:
            if DG.has_edge(n1,n2):
                count+=1
    return float(count)/DG.number_of_edges()

print()
print("the probability of team manage collects data:",InterclassLinkProportion(TrophicDG,B,T))
print("the probability of all team members collect data:",InterclassLinkProportion(TrophicDG,B,I))
print("the probability of all team members work on data modeling and machine learning",InterclassLinkProportion(TrophicDG,I,I))
print("the probability of all team members who need to supervise work:",InterclassLinkProportion(TrophicDG,I,T))

#Ratio of data entry role and senior role like data scientist and ml engineer
print()
print("Data team entry role/senior role rate:",float((len(B)+len(I)))/(len(I)+len(T)))




