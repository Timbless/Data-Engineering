# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:00:15 2021

@author: hulkb
"""

# the topic I choose is to find the network of salmon import and export around the world in 2018
# 0303 fish--- data source from comtrade database, data selection: import, export. year: 2018
# 030311 pacific salmon, sockeye salmon
# 030312 frozen pacific salmon
# 030313 frozen atlantic salmon
# 030319 pacific salmon, other than sockeye salmon
# 030322 atlantic salmon

#read the data
import pandas as pd

df = pd.read_csv('C:/Users/hulkb/Desktop/Academic/Data Engineering/HW2/download/comtrade_0303_2018.csv')

df1 = df[['Year', 'Reporter Code', 'Trade Flow Code', 'Partner Code', \
          'Classification', 'Commodity Code', 'Qty Unit Code', 'Customs',\
              'Netweight (kg)', 'Trade Value (US$)', 'Aggregate Level']]

df1.rename(columns= {'Customs':'Supplementary Quantity', 'Aggregate Level':'Estimation Code'}, inplace = True)

print(df1)


print(df1.columns)

columns_list = list(df1.columns)

#find which column has the missing value
for i in columns_list:
    if df1[i].isnull().values.any() == True:
        print('column: ' + i + ' has missing values')

#check how many missing value we have in those columns
print(df1['Supplementary Quantity'].isnull().values.sum())
#check the critira, then fix the column we need to deal with missing value  
print(df1['Netweight (kg)'].isnull().values.sum())

# filling missing value with 0
df1['Netweight (kg)'] = df1['Netweight (kg)'].fillna(0)

#save the final dataframe we modified
df1.to_csv(r'C:/Users/hulkb/Desktop/Academic/Data Engineering/HW2/download/final_version_data_2018.csv', index = False)

print(df1.describe())


#building the fish import and export network
import networkx as nx
import matplotlib.pyplot as plt

#the function I used from HW2 reading
def net_symmetrisation(wtn_file, exclude_countries):
    DG = nx.DiGraph()
   
    Reporter_pos = 1
    Flow_code_pos = 2
    Partner_pos = 3
    Value_pos = 9
   
    dic_trade_flows = {}
    hfile = open(wtn_file, 'r')
   
    header = hfile.readline()
    lines = hfile.readlines()
   
    for l in lines:
        l_split = l.split(',')
        # the following is to prevent parsing lines without data
        if len(l_split) < 2:
            continue
        reporter = int(l_split[Reporter_pos])
        partner = int(l_split[Partner_pos])
        flow_code = int(l_split[Flow_code_pos])
        value = float(l_split[Value_pos])

        if ((reporter in exclude_countries) or (partner in exclude_countries) or \
           (reporter == partner)):
            continue

        if flow_code == 1 and value > 0.0:
            # 1=Import, 2=Export
            if (partner, reporter, 2) in dic_trade_flows:
                DG[partner][reporter]['weight'] = (DG[partner][reporter]['weight'] + value) / 2.0
            else:
                DG.add_edge(partner, reporter, weight=value)
                dic_trade_flows[(partner, reporter, 1)] = value
               
        elif flow_code == 2 and value > 0.0:
            # 1=Import, 2=Export
            if (reporter, partner, 1) in dic_trade_flows:
                DG[reporter][partner]['weight'] = (DG[reporter][partner]['weight'] + value) / 2.0
            else:
                DG.add_edge(reporter, partner, weight=value)
                dic_trade_flows[( reporter, partner, 2)] = value
        else:
            print('trade flow not present\n')
    hfile.close()
   
    return DG

#there is no exclude country 
exclude_countries = []

#get the network nodes and edges
DG = net_symmetrisation('C:/Users/hulkb/Desktop/Academic/Data Engineering/HW2/download/final_version_data_2018.csv', exclude_countries)
print('number of nodes: ', DG.number_of_nodes())
print('number of edges: ', DG.number_of_edges())

#draw the network figure
nx.draw(DG)
#save the figure
plt.savefig('fish_network.png')

# weighted case
W = 0
W_rep =0
for n in DG.nodes():
    for e in DG.out_edges(n, data=True):
        W += e[2]['weight']
        if DG.has_edge(e[1], e[0]):
            W_rep += min(DG[e[0]][e[1]]['weight'], DG[e[1]][e[0]]['weight'])
print(W, W_rep, W_rep/W)  #get Reciprocity without weight

# weighted case
W = 0
W_rep =0
for n in DG.nodes():
    for e in DG.out_edges(n, data=True):
       W += e[2]['weight']
       if DG.has_edge(e[1], e[0]):
           W_rep += min(DG[e[0]][e[1]]['weight'], DG[e[1]][e[0]]['weight'])
print(W,  W_rep,  W_rep/W) #get Reciprocity with weight



# average degrees K_nn distribution
list_Knn=[]
for n in DG.nodes():
    degree = 0.0
    count = 0
    for nn in DG.neighbors(n):
        count += 1
        degree = degree + DG.degree(nn)
        temp  = degree / len(list(DG.neighbors(n)))
    list_Knn.append(temp)

#plot the histogram    
#plt.hist(list_Knn,bins=12)

#basic Pearson correlation coefficient for the comtrade data
r1 = nx.degree_assortativity_coefficient(DG)
#print correlation coefficient
print(r1) # -1


fish_data = pd.read_csv('C:/Users/hulkb/Desktop/Academic/Data Engineering/HW2/download/comtrade_0303_2018.csv')
print(fish_data.sample(10))

dic_product_netowrk = {}
commodity_codes=['030311','030312','030313','030319','030322']
for c in commodity_codes:
    dic_product_netowrk[c]=net_symmetrisation("C:/Users/hulkb/Desktop/Academic/Data Engineering/HW2/download/comtrade_"+ c +"_update.csv", \
    exclude_countries)
   
DG_aggregate=net_symmetrisation( "C:/Users/hulkb/Desktop/Academic/Data Engineering/HW2/download/final_version_data_2018.csv",exclude_countries)

#get weight on each edges
w_tot = 0
for u,v,d in DG_aggregate.edges(data=True):  # data=True
    w_tot += d['weight']   
for u,v,d in DG_aggregate.edges(data=True):
    d['weight'] = d['weight'] / w_tot

#rescale the weighted ajacency product 
for c in commodity_codes:
    w_tot = 0.0
    for u,v,d in dic_product_netowrk[c].edges(data=True):
        w_tot += d['weight']
    for u,v,d in dic_product_netowrk[c].edges(data=True):
        d['weight'] = d['weight'] / w_tot

print(len(DG_aggregate.nodes()))  # 158
DG_aggregate.number_of_nodes()    # 158 



#use mean function from statistics
from statistics import mean

# this process is to generate the table with the quantities
density_aggregate = DG_aggregate.number_of_edges() / \
    (DG_aggregate.number_of_nodes() * DG_aggregate.number_of_nodes() - 1.0)
w_agg = []
NS_in = []
NS_out = []
for u,v,d in DG_aggregate.edges(data=True):
    w_agg.append(d['weight'])
for n in DG_aggregate.nodes():
    if DG_aggregate.in_degree(n) > 0:
        NS_in.append(DG_aggregate.in_degree(n, weight='weight') / DG_aggregate.in_degree(n))
    if DG_aggregate.out_degree(n) > 0:
        NS_out.append(DG_aggregate.out_degree(n, weight='weight') / DG_aggregate.out_degree(n))

for c in commodity_codes:
    density_commodity = dic_product_netowrk[c].number_of_edges() / \
    (dic_product_netowrk[c].number_of_nodes() * dic_product_netowrk[c].number_of_nodes() - 1.0)
    w_c = []
    NS_c_in = []
    NS_c_out = []
    for u,v,d in dic_product_netowrk[c].edges(data=True):
        w_c.append(d['weight'])
    for n in dic_product_netowrk[c].nodes():
        if dic_product_netowrk[c].in_degree(n) > 0:
            NS_c_in.append(dic_product_netowrk[c].in_degree(n, weight='weight') / dic_product_netowrk[c].in_degree(n))
        if dic_product_netowrk[c].out_degree(n) > 0:
            NS_c_out.append(dic_product_netowrk[c].out_degree(n, weight='weight') / dic_product_netowrk[c].out_degree(n))
   # print the table
    print(c, str(round(density_commodity/density_aggregate, 4)) + ' & ' + str(round(mean(w_c)/mean(w_agg), 4)) \
          + ' & ' + str(round(mean(NS_c_in)/mean(NS_in),4)) + ' & ' + str(round(mean(NS_c_out)/mean(NS_out), 4)) )


































