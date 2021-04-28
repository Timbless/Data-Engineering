import time
import requests
import math
import os


################# 采集数据
#下载单个公司的历史股票价格
def down_load_file(symbol):
    api_key = "TYU0ESSU0DBT790M"
    #symbol = "IBM"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&datatype=csv"
    res = requests.get(url)
    file_name = symbol + ".csv"
    if not os.path.exists("data/mydata"):
        os.mkdir("data/mydata")
    with open("data/mydata/"+file_name, "wb") as code:
        code.write(res.content)
    time.sleep(15)

# 下载清单列表里 全部公司的股票价格
def down_load_all_files():
    with open("listing_status.csv") as f:
        f.readline()
        counter = 0
        while True:
            line = f.readline()
            arr = line.split(",")
            symbol = arr[0]
            try:
                down_load_file(symbol)
            except:
                print("error")
                time.sleep(5)

#从本地查询某公司的历史股票价格  包括 日期,和close价格
def get_his_prices(symbol):
    with open("data/mydata/"+symbol+".csv") as f:
        f.readline()

        lines = f.readlines()
        prices = []
        for line in lines:
            arr = line.split(",")
            date = arr[0]
            close = float(arr[4])
            price_new = {}
            price_new['close'] = close
            price_new['date'] = date
            prices.append(price_new)
    return prices

# data = get_his_prices("DDD")
# print(data)
# 获取全部历史股票价格
def get_list_stocks():
    hfile = open("./data/listing_status.csv", 'r')
    # we choose to get only companies with a market capitalisation
    # greater than 50B$
    cap_threshold = 50.0

    list_stocks = []
    nextline = hfile.readline()
    counter = 0
    while True:
        nextline = hfile.readline()
        if not nextline:
            break
        line = nextline.split(',')
        symble = line[0][1:-1]
        # if "^" not in symble:
        #     if is_market_cap_lg_50b(symble) :
        #         list_stocks.append((line[0][1:-1], line[1][1:-1], \
        #                             line[5][1:-1], line[6][1:-1]))
        #         print(symble)
        list_stocks.append((line[0], line[1],line[2], line[3]))
        counter +=1
        # if counter>=130:
        #     break
        #print(symble+"--")
    hfile.close()

    return list_stocks

list_stocks = get_list_stocks()


diz_sectors={}
for s in list_stocks:
    diz_sectors[s[0]]=s[2]

list_ranking=[]
for s in set(diz_sectors.values()):
    list_ranking.append((list(diz_sectors.values()).count(s),s))

list_ranking.sort(reverse=True)

list_colors=['0.0', '0.2', '0.4', '0.6','0.7', '0.8', '0.9']


diz_colors={}

#association color and more represented sectors
for s in list_ranking:
    if s[1]=='n/a':
        diz_colors[s[1]]='white'
        continue
    if list_colors==[]:
        diz_colors[s[1]]='white'
        continue
    diz_colors[s[1]]=list_colors.pop(0)


diz_comp={}
for s in list_stocks:
    #stock = yf.Share(s[0])
    symbol = s[0]
    diz_comp[symbol] = get_his_prices(symbol)
    #
    #diz_comp[s[0]]=stock.get_historical(start_period, end_period)

#create dictionaries of time series for each company
diz_historical={}
for k in diz_comp.keys():
    if diz_comp[k]==[]:
        continue
    diz_historical[k]={}
    comp = diz_comp[k]
    if comp is None:
        continue
    for e in comp:
        if 'close' not in e:
            continue

        diz_historical[k][e['date']]=e['close']

for k in diz_historical.keys():
    print(k,len(diz_historical[k]))


reference_company='AA'
diz_returns={}
d=list(diz_historical[reference_company].keys())
d.sort()
# print(len(d),d)

for c in diz_historical.keys():
    #check if the company has the whole set of dates
    if len(diz_historical[c].keys())<len(d): continue
    if '2020-11-23' not in diz_historical[c]:
        continue
    diz_returns[c]={}
    for i in range(1,len(d)):
        #price returns
        diz_returns[c][d[i]]=math.log( \
        float(diz_historical[c][d[i]])) \
        -math.log(float(diz_historical[c][d[i-1]]))

print(diz_returns[reference_company])

#mean
def mean(X):
    m=0.0
    for i in X:
        m=m+i
    return m/len(X)

#covariance
def covariance(X,Y):
    c=0.0
    m_X=mean(X)
    m_Y=mean(Y)
    for i in range(len(X)):
        c=c+(X[i]-m_X)*(Y[i]-m_Y)
    return c/len(X)

#pearson correlation coefficient
def pearson(X,Y):
    return covariance(X,Y)/(covariance(X,X)**0.5 * \
                            covariance(Y,Y)**0.5)


def stocks_corr_coeff(h1,h2):
    l1=[]
    l2=[]
    intersec_dates=set(h1.keys()).intersection(set(h2.keys()))
    for d in intersec_dates:
        l1.append(float(h1[d]))
        l2.append(float(h2[d]))
    return pearson(l1,l2)

#correlation with the same company has to be 1!
# print(stocks_corr_coeff(diz_returns[reference_company], \
#                         diz_returns[reference_company]))




import math
import networkx as nx

corr_network=nx.Graph()

num_companies=len(diz_returns.keys())
for i1 in range(num_companies-1):
    for i2 in range(i1+1,num_companies):
        stock1=list(diz_returns.keys())[i1]
        stock2=list(diz_returns.keys())[i2]
        #metric distance
        metric_distance=math.sqrt(abs(2*(1.0-stocks_corr_coeff(diz_returns[stock1],diz_returns[stock2]))))
        #building the network
        corr_network.add_edge(stock1, stock2, weight=metric_distance)
#
# print("number of nodes:",corr_network.number_of_nodes())
# print("number of edges:",corr_network.number_of_edges())





tree_seed=reference_company
N_new=[]
E_new=[]
N_new.append(tree_seed)
while len(N_new)<corr_network.number_of_nodes():
    min_weight=10000000.0
    for n in N_new:
        for n_adj in corr_network.neighbors(n):
            if not n_adj in N_new:
                if corr_network[n][n_adj]['weight']<min_weight:
                    min_weight=corr_network[n][n_adj]['weight']
                    min_weight_edge=(n,n_adj)
                    n_adj_ext=n_adj
    E_new.append(min_weight_edge)
    N_new.append(n_adj_ext)

#generate the tree from the edge list
tree_graph=nx.Graph()
tree_graph.add_edges_from(E_new)

#setting the color attributes for the network nodes
for n in tree_graph.nodes():
    tree_graph.nodes[n]['color']=diz_colors[diz_sectors[n]]


from pygraphviz import *

from networkx.drawing.nx_agraph import graphviz_layout
import pylab as plt

pos = graphviz_layout(tree_graph)


plt.figure(figsize=(20,20))
nx.draw_networkx_edges(tree_graph,pos,width=2, \
                       edge_color='black', alpha=0.5, style="solid")
nx.draw_networkx_labels(tree_graph,pos)
for n in tree_graph.nodes():
    nx.draw_networkx_nodes(tree_graph, pos, [n], node_size = 600, \
    alpha=0.5, node_color = tree_graph.nodes[n]['color'], \
    with_labels=True)

plt.axis('off')

plt.savefig('./data/stock_tree.png',dpi=600)

