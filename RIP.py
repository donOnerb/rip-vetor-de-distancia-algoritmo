
import threading
import time
import random

nodes = []

#tranferencia de tabela
def tolayer2(rcvdpkt):
	print ("Enviando do nó %d para o nó %d" %(rcvdpkt.get_sourceid(), rcvdpkt.get_destid()))
	nodes[rcvdpkt.get_destid()].rtupdate(rcvdpkt)


def printaTabela(sourceid, mincost):
	print ("\n**********Tabela do nó %d**********\n" %(sourceid))
	print ("Para nó 0 | %d | Através de j" %(mincost[0]))
	print ("Para nó 1 | %d | Através de j" %(mincost[1]))
	print ("Para nó 2 | %d | Através de j" %(mincost[2]))
	print ("Para nó 3 | %d | Através de j" %(mincost[3]))
	print ("\n***********************************\n")


class Rtpkt:
	sourceid = -1 #identificador do nó
	destid = -1 #identificador do nó destino
	mincost = [999, 999, 999, 999] # tabela

	def __init__(self, sourceid, destid, mincost):
		self.sourceid = sourceid
		self.destid = destid
		self.mincost = mincost

	def get_sourceid(self):
		return self.sourceid

	def get_destid(self):
		return self.destid

	def get_mincost(self):
		return self.mincost

class Node:
	sourceid = -1 # identificador do nó
	neighborhood = [] # vetor vizinhança
	mincost = [999, 999, 999, 999] # tabela

	def __init__(self, sourceid, neighborhood, mincost):
		#inicialização
		self.sourceid=sourceid
		self.neighborhood=neighborhood
		self.mincost=mincost

	def send_table(self):
		#rotina de transmissão de tabela
		printaTabela(self.sourceid, self.mincost)
		for x in self.neighborhood:
			#variavel a é inicializada com um objeto rtpkt em cada ciclo
			a = Rtpkt(self.sourceid, x, self.mincost)
			#é mandado a tabela para o vizinho
			tolayer2(a)

	def rtupdate(self, rcvdpkt):
		#flag para verificar se algo na tabela mudou ou não
		change = 0
		#pega a tabela e o id do nó destino
		mincost = rcvdpkt.get_mincost()
		sourceid = rcvdpkt.get_sourceid()
		#compara se tem algum caminho mais rápido, se tiver seta na tabela
		#print (destid)
		for x in range(0,4):
			if (mincost[x] + self.mincost[sourceid]) < self.mincost[x] and x != sourceid:
				self.mincost[x] = mincost[x] + self.mincost[sourceid]
				change = 1

		#se teve alteração é mandado a tabela para os vizinhos
		if change == 1:
			time.sleep(random.random()*5)
			self.send_table()


def execute(sourceid, neighborhood, mincost):
	
	nodes[sourceid] = Node(sourceid, neighborhood, mincost)
	printaTabela(sourceid, mincost)
	time.sleep(random.random()*5)
	nodes[sourceid].send_table()



#rotina principal, adicionando threads
nodes = [Node(-1,[],[]), Node(-1,[],[]), Node(-1,[],[]), Node(-1,[],[])]
t_0 = threading.Thread(target= execute, args = (0, [1, 2, 3], [0, 1, 3, 7]))
t_1 = threading.Thread(target= execute, args = (1, [0, 2], [1, 0, 1, 999]))
t_2 = threading.Thread(target= execute, args = (2, [0, 1, 3], [3, 1, 0, 2]))
t_3 = threading.Thread(target= execute, args = (3, [0, 2], [7, 999, 2, 0]))

t_0.start()
time.sleep(0.1)
t_1.start()
time.sleep(0.1)
t_2.start()
time.sleep(0.1)
t_3.start()
time.sleep(0.1)
t_0.join()
t_1.join()
t_2.join()
t_3.join()
