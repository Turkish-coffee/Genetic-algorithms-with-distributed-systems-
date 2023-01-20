import socket
from threading import Thread, Lock
import pickle 
import faceCreationGen as helper
import time

ITERATIONNUMBER = 20
FITNESSTHRESHOLD = 0.95

class master(Thread):

    evolutionCount = 0
    connectedWorkers = 0
    newPopulation = []
    currentConnections = []
    generation = None
    
    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.ip  = ip
        self.port = port 
        self.conn = conn 
        print("master node created successfully !!")
        master.connectedWorkers += 1




    def recieveFromWorkers(self):
        lock = Lock()
        
        while True:

            data = self.conn.recv(1000000)
            if not data:
                exit()
            recivedData = pickle.loads(data)
            lock.acquire()
            for i in range(len(recivedData)):
                master.newPopulation.append(recivedData[i])
            lock.release()
            if len(master.newPopulation) >= workerNumber*master.generation.agentNumber:
                self.processData()


          




    def sendDataToWorkerNodes(self, rawdata):

        data = pickle.dumps(rawdata)
        for i in master.currentConnections: 
            i.send(data)

    def processData(self):
        master.evolutionCount += 1
        master.generation.SetPopulation(self.sortPopulation())
        if master.evolutionCount % 10 == 0:
            print(f"{master.evolutionCount}'th generation: current best Agent fitness score = {master.generation.best_agent.fitnessScore}.")
        if master.generation.best_agent.fitnessScore > FITNESSTHRESHOLD:
            print(f"{master.generation.best_agent.fitnessScore:.2f} fitness score has been reached at the {master.evolutionCount}'th iteration! ({FITNESSTHRESHOLD} threshold set)")

            global end
            end = time.time()
            print(f"program exited in {end - start:.2f} seconds :)")
            self.sendDataToWorkerNodes("SHUTDOWN")
            master.connectedWorkers = 0
            master.currentConnections = []
            master.evolutionCount = 0
            master.newPopulation = []
            master.generation = helper.Generation(100)
            
        else: 
            self.sendDataToWorkerNodes(master.generation.population)
            


    def sortPopulation(self):
         
        concat = {}
        for i in range (len(master.newPopulation)):
            concat[i] = master.newPopulation[i]
        
        sortedPopulation = sorted(concat.values(), key=lambda agent: agent.Fitness(),reverse= True)
        sortedPopulation = sortedPopulation[:10]
        master.newPopulation.clear()

        return sortedPopulation




    def run(self): 
        if master.connectedWorkers == workerNumber:

            time.sleep(1)
            print("processing ...")
            global start
            start = time.time()

            self.sendDataToWorkerNodes(master.generation.population)
        self.recieveFromWorkers()


if __name__ == '__main__':
    
    workerNumber = int(input("how many worker's are there ?"))
    master.generation = helper.Generation(200)
    lock = Lock()
    TCP_IP = 'localhost'
    TCP_PORT = 2004
    BUFFER_SIZE = 1000000
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpServer.bind((TCP_IP, TCP_PORT))
    threads = []

    print("Working ...")
    tcpServer.listen(workerNumber * ITERATIONNUMBER)
    for i in range(workerNumber * ITERATIONNUMBER):
        (conn, (ip, port)) = tcpServer.accept()
    
        lock.acquire()
        master.currentConnections.append(conn)
        masterThread = master(ip, port, conn)
        lock.release()
        masterThread.start()
        threads.append(masterThread)
    
    for t in threads:
        t.join()

    
