# -*- coding: utf-8 -*-
import networkx as nx
import random
import os.path
import sys

mGraph = ""

#Povprašaj po datoteki z omrežje
gFile = raw_input("Input file name:\n")

#Sanity check
while not os.path.isfile(gFile):
    print "The file does not exist. Input another filename or type 'q' to quit."
    gFile = raw_input("Input file name:\n")
    if gFile == "q":
        sys.exit()

#OK, datoteka obstaja, poizkusi jo prebrati
try:
    mGraph = nx.read_edgelist(gFile,delimiter=".") #Ta delimiter je primeren za priloženo testno datoteko, načeloma se ga izbriše
    #mGraph = nx.read_edgelist(gFile)
except:
    print "Bad file. Exiting."
    sys.exit()

# Testni graf
#mGraph = nx.gn_graph(10)
#for edge in mGraph.edges():
#    print edge



## 1: Funkcija za iskanje števila povezav za vsak node
def getNodeInputAndOutputCount(g):
    #Inicializacija slovarjev
    countedIn = {}
    countedOut = {}
    #Za vsak rob - 
    for edge in g.edges_iter():
        #če krajišča še ni v števcih vhoda ali izhoda, ga dodaj in nastavi na 0
        if  not edge[0] in countedOut:
            countedOut[edge[0]] = 0
        if  not edge[1] in countedOut:
            countedOut[edge[1]] = 0
        if  not edge[0] in countedIn:
            countedIn[edge[0]] = 0
        if  not edge[1] in countedIn:
            countedIn[edge[1]] = 0

        #Krajišču izvora roba prištej ena v števcu izhodov    
        countedOut[edge[0]] = countedOut[edge[0]] + 1
        #Krajišču ponora roba prištej ena v števcu vhodov
        countedIn[edge[1]] = countedIn[edge[1]] + 1
    #Vrni oba slovarja v obliki {Krajišče:Števec, ...}
    return (countedIn,countedOut)  

print ""
print ""
print "1: IN AND OUT DEGREES OF NODES"
print ""
#Uporabi funkcijo in poberi rezultate
(inConnections,outConnections) = getNodeInputAndOutputCount(mGraph)
#Za vsako krajišče izpiši identifikator krajišča in pripadajoče število vhodov in izhodov
for node in mGraph.nodes():
    print "Node", node
    print "In-degree:", inConnections[node],", Out-degree:",outConnections[node]


## 2: Funkcija za iskanje 3 verig
def getThreeChainCount(g):
    #Inicializacija treh slovarjev za števce, vsakemu krajišču se šteje kolikokrat je A, kolikokrat B in kolikokrat C
    countedA = {}
    countedB = {}
    countedC = {}
    
    #Nastavi začetne vrednosti
    for node in g.nodes():
        countedA[node]=0
        countedB[node]=0
        countedC[node]=0

    #Za vsako krajišče
    for node in g.nodes():
        #Za vsak rob IZ tega krajišča
        for edge_1 in g.edges(node):
            #Če ne obstaja povratna povezava (A-B,B-A)
            if not (edge_1[1],edge_1[0]) in g.edges(node):
                #Za vsak rob iz krajišča na koncu drugega roba (B-C)
                for edge_2 in g.edges(edge_1[1]):
                    #Če ne obstaja povezava C-A in če ne obstaja povezava A-C (imamo usmerjene grafe)
                    if not (edge_2[1],node) in g.edges() and not (node, edge_2[1]) in g.edges():
                        #Prvo krajišče je nastopalo kot krajišče A, krajišče na koncu roba 1 ko krajišče B in krajišče na koncu drugega roba kot krajišče C. Prištej števce, kot je prav.
                        countedA[node]=countedA[node]+1
                        countedB[edge_1[1]]=countedB[edge_1[1]]+1
                        countedC[edge_2[1]]=countedC[edge_2[1]]+1
    #Vrni števce
    return (countedA,countedB,countedC)

print ""
print ""
print "2: THREE PART CHAIN PARTICIPATION"
print ""
#Uporabi funkcijo za pridobitev števcev
(cA,cB,cC) = getThreeChainCount(mGraph)
#Za vsako krajišče izpiši krajišče ter kolikokrat nastopa v kateri vlogi
for node in mGraph.nodes():
    print "Node", node
    print "A:", cA[node],"B:", cB[node], "C:", cC[node]


## 3_1: Iskanje podomrežij
#Rekurzivna funkcija za iskanje podomrežij, za začetek glej findSubGraphs(g)
def findSubConnections(g, node, subGraph, usedNodes):
    #Dodaj to krajišče med uporavljena
    usedNodes.append(node)
    #Za vsak rob iz tega krajišča
    for edge in g.edges(node):
        #Dodaj ta rob podgrafu
        subGraph.add_edge(*edge)
        #Če konec roba še ni obiskano krajišče
        if not edge[1] in usedNodes:
            #Poišči vse povezave iz tega krajišča. Zadeva se ustavi, ko krajišče nima izhodnih povezav - je robno.
            findSubConnections(g,edge[1],subGraph, usedNodes)
        
def findSubGraphs(g):
    #Inicializacija slovarja za shranjevanje podgrafov ter vrste za shranjevanje že obiskanih vozlišč, da se v primeru cikla ne... no, zaciklamo
    arrayDict = {}
    usedNodes = []
    #Za vsako krajišče
    for node in g.nodes():
        #Dodaj ga med uporabljene
        usedNodes.append(node)
        #Ustvari prazen podgraf
        sg = nx.DiGraph()
        #Podgrafu dodaj vse povezave, ki so dosegljive s tega krajišča - rekurzivno, glej funkcijo. Argumenti so graf, trenutno krajišče, podgraf ki se mora zapolniti, ter spremenljivka uporabljenih krajišč
        findSubConnections(g,node,sg,usedNodes)
        #Če je število krajišč v podgrafu različno od celotnega števila krajišč (torej manjše), ga dodaj v slovar podgrafov. Če je enako nas ne zanima.
        if len(sg.nodes()) != len(g.nodes()):
            arrayDict[node]=sg
    #Vrni slovar podgrafov
    return arrayDict

print ""
print ""
print "3: SUBGRAPHS THAT DO NOT INCLUDE ALL NODES"
print ""
#Uporabi funkcijo
subGraphDictionary = findSubGraphs(mGraph)
#Za vsak vnos v slovarju izpiši začetno krajišče ter krajišča celotnega podgrafa
for node,subGraph in subGraphDictionary.iteritems():
    print "Starting at node", node,":",subGraph.nodes()


## 4: Izračun PageRank-a
def getPageRank(g, possibility, stepMultiplier):
    #Inicializacija števca obiskov, nastavljenega na 0 za vsako krajišče
    counter = {}
    for node in g.nodes():
        counter[node]=0
    #Naključno krajišče. Random.sample(populacija,število primerkov), vrne [krajišče], [0] spremeni to v krajišče.
    currentNode = random.sample(g.nodes(), 1)[0]
    #To krajišče je bilo obiskano, prištej mu en obisk
    counter[currentNode]= counter[currentNode]+1
    #Za število definiranih korakov
    for i in range(0,stepMultiplier*len(g.nodes())):
        #Če je poljubna vrednost večja ali enaka damferju (pri possibility=0.1 je možnost da bo večja 90%)
        if random.random()>=possibility:
            #Vsa sosedna krajišča spakiraj v eno vrsto
            neighbours = []
            for edge in g.edges(currentNode):
                #Sosednje krajišče je krajišče na koncu roba
                neighbours.append(edge[1])
            #Če sploh je kak sosed
            if len(neighbours)>0:
                #Izberi naključnega in mu prištej obisk
                currentNode = random.sample(neighbours, 1)[0]
                counter[currentNode]= counter[currentNode]+1
            else:
                #Če ni soseda se teleportiraj na poljubno mesto na grafu in mu prištej obisk
                currentNode = random.sample(g.nodes(), 1)[0]
                counter[currentNode]= counter[currentNode]+1
        else:
            #Če poljubna vrednost ni večja, se teleportiraj in krajišču prištej obisk
            currentNode = random.sample(g.nodes(), 1)[0]
            counter[currentNode]= counter[currentNode]+1
    #Vrni slovar {Krajišče:število obiskov}
    return counter


print ""
print ""
print "4: PAGE RANK CALCULATIONS"
print ""
#Uporabi funkcijo
PageRank = getPageRank(mGraph,0.1,20)
#Izpiši celotno število korakov
print "Total steps:", 20*len(mGraph.nodes())
#Izpiši krajišče: število obiskov
for key,value in PageRank.iteritems():
    print str(key)+":", "Visited:", value
