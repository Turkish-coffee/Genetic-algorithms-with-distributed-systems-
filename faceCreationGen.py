import numpy as np
import matplotlib.pyplot as plt

eyes = [2.25, 3.75, 5, 5, 4]
nose = [3, 3, 6]
mouth = [2.5, 3, 3.5, 1.15, 1, 1.15, 8]

TargetGene = np.array(eyes + nose + mouth)


class Agent():
    def __init__(self, id, genomeSize=15):
        self.id = id
        self.genomeSize = genomeSize
        self.genome = self.CreateGene()

    def CreateGene(self):
        return np.random.rand(self.genomeSize) * 10

    def SetGene(self, newGene):
        self.genome = newGene

    def Fitness(self):
        error = (TargetGene - self.genome)
        self.fitnessScore =  1 / (1 + np.dot(error, error))
        return self.fitnessScore


class Generation():
    def __init__(self, agentNumber):
        self.agentNumber = agentNumber
        self.population = {}
        for i in range(agentNumber):
            self.population[i] = Agent(i)
        self.UpdateProbabilities()
        self.Evolve(1)

    def SetPopulation(self,populationToSet):
        for i in range (len(populationToSet)):
            self.population[i] = populationToSet[i]
        self.UpdateProbabilities()
        self.UpdateBestAgent()

    def UpdateProbabilities(self):
        self.success = {}
        for i in range(self.agentNumber):
            self.success[i] = self.population[i].Fitness()
        total_success = sum(self.success.values())

        self.reproduction_probability = {}
        for i in range(self.agentNumber):
            self.reproduction_probability[i] = self.success[i] / total_success

    def Selection(self):
        productionProbability = [self.reproduction_probability[i] for i in range(self.agentNumber)]
        # 2 = kac tane agent sectigi
        select = np.random.choice(self.agentNumber, 2, replace=False, p=productionProbability)
        return select

    def Crossover(self, selectedParents):
        parent0 = self.population[selectedParents[0]].genome
        parent1 = self.population[selectedParents[1]].genome

        # 15 = agent genom size
        cut = np.random.randint(15)
        child_gene = np.hstack((parent0[:cut], parent1[cut:]))
        return child_gene

    def Mutation(self, child_gene):
        if np.random.rand() < self.mutationChance:
            mutation_point = np.random.randint(len(child_gene))
            child_gene[mutation_point] = np.random.rand() * 10
        return child_gene

    def CreateNewChild(self):
        parents = self.Selection()
        child_gene = self.Crossover(parents)
        child_gene = self.Mutation(child_gene)
        return child_gene

    def CreateNewPopulation(self):
        sorted_by_success = sorted(self.success.items(), key=lambda sortValue : sortValue[1])
        self.best_agent = self.population[sorted_by_success[-1][0]]

        #// operatoru islemin tam sayi sonucunu alir
        for i in range(self.agentNumber // 2):
            child_gene = self.CreateNewChild()
            agent_id = sorted_by_success[i][0]
            self.population[agent_id].SetGene(child_gene)

        self.UpdateProbabilities()

    def UpdateBestAgent(self):
        sorted_by_success = sorted(self.success.items(), key=lambda sortValue : sortValue[1])
        self.best_agent = self.population[sorted_by_success[-1][0]]
    
    def Evolve(self, evolutionCount=10,mutationChance = 0.25):
        self.mutationChance = mutationChance
        for i in range(evolutionCount):
            self.CreateNewPopulation()
        return self.population
