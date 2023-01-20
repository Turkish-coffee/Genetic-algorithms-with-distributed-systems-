import socket
from multiprocessing import Process
import faceCreationGen as helper
import pickle
import os
import signal





class worker(Process):
    generation = None
    id = 1

    def __init__(self,x):
        Process.__init__(self)
        self.mutationChance = x
        self.mutationRate = f'worker P: %{self.mutationChance*100}'
        self.id = worker.id 
        print(f"worker node created :p ( mutation rate: {self.mutationRate})")
        
        worker.id += 1


    def recieveMessage(self,tcpServer):
        while True:
            data = tcpServer.recv(1000000)
            convertedData = pickle.loads(data)
            
            if convertedData == "SHUTDOWN":
                os.kill(self.pid, signal.SIGTERM)       
                
            worker.generation.SetPopulation(convertedData)
            evolved = worker.generation.Evolve(10,self.mutationChance)
            self.SendMessage(tcpServer,evolved)

    def SendMessage(self,tcpServer,dataToSend):
        convertedData = pickle.dumps(dataToSend)
        tcpServer.send(convertedData)

    def run(self):
        host = 'localhost'
        port = 2004

        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.connect((host, port))
        self.recieveMessage(tcpServer)




if __name__ == '__main__':
    import time
    worker.generation = helper.Generation(100)

    
    for i in range(20):


        c2 = worker(0.90)
        c1 = worker(0.10)

        c2.start()
        c1.start()
        
        while 1:
            if c1.is_alive() or c2.is_alive():
                continue
            else:
                break
              
    
