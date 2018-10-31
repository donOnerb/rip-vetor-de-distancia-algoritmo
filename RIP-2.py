import socket
import sys
import threading
import time
import random


server_address = ('127.0.0.1', 10000+int(sys.argv[1]))

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Bind to the server address
sock.bind(server_address)


sourceid = int(sys.argv[1]) # identificador do nó
neighborhood = [] # vetor vizinhança
cost = [] #tabela fixa de custo
mincost = [] # tabela
nexth = [] #next hop
change = 0


def printaTabela(sourceid, mincost, nexth):
	print ("\n**********Tabela do nó %d**********\n" %(sourceid))
	print ("Para nó 0 | %d | Através de %d" %(mincost[0], nexth[0]) )
	print ("Para nó 1 | %d | Através de %d" %(mincost[1], nexth[1]) )
	print ("Para nó 2 | %d | Através de %d" %(mincost[2], nexth[2]) )
	print ("Para nó 3 | %d | Através de %d" %(mincost[3], nexth[3]) )
	print ("\n***********************************\n")

class Rtpkt:
	sourceid = -1 #identificador do nó
	destid = -1 #identificador do nó destino
	mincost = [999, 999, 999, 999] # tabela
	def __init__(self, sourceid, destid, mincost):
		self.sourceid = sourceid
		self.destid = destid
		self.mincost = mincost

	def messageforRtpkt(self, message):
		self.sourceid = int(message[0:message.find(':')])
		self.destid = int(message[message.find(':')+1:message.find('@')])
		
		self.mincost[0] = int(message[message.find('@')+1:message.find('a')])
		self.mincost[1] = int(message[message.find('a')+1:message.find('b')])
		self.mincost[2] = int(message[message.find('b')+1:message.find('c')])
		self.mincost[3] = int(message[message.find('c')+1:])
		return self

	def get_sourceid(self):
		return self.sourceid
	def get_destid(self):
		return self.destid
	def get_mincost(self):
		return self.mincost
	def convertString(self):
		message = str(self.sourceid) + ':' + str(self.destid)+ '@' +str(self.mincost[0]) + 'a' + str(self.mincost[1]) + 'b' + str(self.mincost[2]) + 'c' + str(self.mincost[3])
		return message

	

def send_table():
	global mincost, change
	sent = 0
	mincostL = [999, 999, 999, 999]
	changeL = -1
	while True:
		while changeL < change:
			mincostL = mincost
			changeL+=1
			#rotina de transmissão de tabela
			for x in neighborhood:
				#variavel a é inicializada com um objeto rtpkt em cada ciclo
				a = Rtpkt(sourceid, x, mincost)
				#é mandado a tabela para o vizinho
				print ("Enviando para o nó %d" %(x))
				while(sent == 0):
					#print (sent)
					sent = sock.sendto((a.convertString()).encode(), ('127.0.0.1', 10000 + x))
				sent = 0
				time.sleep(random.random()*5)
		time.sleep(random.random()*5)
		


def rtupdate():
	global mincost, nexth, change, cost
	#flag para verificar se algo na tabela mudou ou não
	mincostL = [999, 999, 999, 999]
	printaTabela(sourceid, mincost, nexth)
	while True:
		changeLocal = 0
		mincostL = mincost
		#espera e recebe mensagem
		print("Esperando tabela")
		rcvdpkt = Rtpkt(-1, -1, [999, 999, 999, 999])
		rcvdpkt = rcvdpkt.messageforRtpkt(sock.recv(1024).decode())
		print("Tabela Recebida")
		#pega a tabela e o id do nó destino
		mincostM = rcvdpkt.get_mincost()
		sourceidM = rcvdpkt.get_sourceid()
		print ("Recebido do nó %d" %(sourceidM))
		#compara se tem algum caminho mais rápido, se tiver seta na tabela
		#print (destid)
		for x in range(0,4):
			if (mincostM[x] + cost[sourceidM]) < mincost[x] and x != sourceidM:
				print("Tabela atualizada. Para roteador %d de [ %d | %d ] para [ %d | %d ]" %(x, mincost[x], nexth[x], mincostM[x] + cost[sourceidM], sourceidM))
				#print(rcvdpkt.convertString())
				#print("%d %d" %(mincostM[x], cost[sourceidM]))
				#print(cost)
				mincostL[x] = mincostM[x] + cost[sourceidM]
				changeLocal = 1
				nexth[x] = sourceidM
		#se teve alteração é mandado a tabela para os vizinhos
		if changeLocal == 1:
			mincost = mincostL
			time.sleep(random.random()*5)
			change+=1
		printaTabela(sourceid, mincost, nexth)



def main(sourceidR):
	global sourceid, neighborhood, mincost, nexth, cost
	#rotina principal, adicionamento de threads
	if sourceidR == 0:
		sourceid = 0
		neighborhood  = [1, 2, 3] 
		mincost = [0, 1, 3, 7]
		cost = [0, 1, 3, 7]
		nexth = [0, 1, 2, 3]
	elif sourceidR == 1:
		sourceid = 1
		neighborhood  = [0, 2] 
		mincost = [1, 0, 1, 999]
		cost = [1, 0, 1, 999]
		nexth = [0, 1, 2, -1]
	elif sourceidR == 2:
		sourceid = 2
		neighborhood  = [0, 1, 3] 
		mincost = [3, 1, 0, 2]
		cost = [3, 1, 0, 2]
		nexth = [0, 1, 2, 3]
	elif sourceidR == 3:
		sourceid = 3
		neighborhood  = [0, 2] 
		mincost = [7, 999, 2, 0]
		cost = [7, 999, 2, 0]
		nexth = [0, -1, 2, 3]

	t_sender = threading.Thread(target=send_table, args=())
	t_receiver = threading.Thread(target=rtupdate, args=())

	t_sender.start()
	t_receiver.start()
	t_sender.join()
	t_receiver.join()

main(int(sys.argv[1]))