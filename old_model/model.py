from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import SingleGrid
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
from numpy import corrcoef
import networkx as nx
import random

HATER = 1
NO_HATER = 0
CONTEMPT_A = 2
CONTEMPT_B = 5
HSSENSI_A = 5
HSSENSI_B = 1

def percent_haters(model):
    agent_behs = [agent.behavior for agent in model.schedule.agents]
    x = sum(agent_behs)/len(agent_behs)
    return x

def average_sens(model):
    agent_sens = [agent.hs_sensi for agent in model.schedule.agents]
    x = sum(agent_sens)/len(agent_sens)
    return x

def average_contempt(model):
    agent_cont = [agent.contempt for agent in model.schedule.agents]
    x = sum(agent_cont)/len(agent_cont)
    return x

def cor_hate_cont(model):
    agent_behs = [agent.behavior for agent in model.schedule.agents]
    agent_cont = [agent.contempt for agent in model.schedule.agents]
    return corrcoef(agent_behs, agent_cont)[1,0]

def decomposition(i):
    j = 10
    while i > 0:
        n = random.randint(1, i)
        while n >= j:
            n = random.randint(1, i)
        yield n
        i -= n


class HateAgent(Agent):
    """Member of hate speech network"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # level of contemtuous prejudice
        self.contempt =  self.random.betavariate(CONTEMPT_A, CONTEMPT_B)
        # level of sensitivity to hate speech
        self.hs_sensi = self.random.betavariate(HSSENSI_A, HSSENSI_B)
        self.behavior = self.random.choices([NO_HATER, HATER], weights=[5,1])[0]

    def step(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        neighbors = self.model.grid.get_cell_list_contents(neighbors_nodes)
        neigh_beh = [neigh.behavior for neigh in neighbors]

        self._nextBehavior = self.behavior

        if self.contempt > self.random.uniform(0, 1):
            if sum(neigh_beh) > 4:
                self._nextBehavior = HATER
            else:
                if self.hs_sensi > self.random.uniform(0, 1):
                    self._nextBehavior = NO_HATER
                else:
                    self._nextBehavior = HATER
        else:
            self._nextBehavior = NO_HATER

        self._next_hs_sensi = self.hs_sensi
        if self.hs_sensi > 0.08:
            self._next_hs_sensi -= 0.005*sum(neigh_beh)

        self._next_contempt = self.contempt
        if self.contempt < 0.92:
            self._next_contempt += 0.001*sum(neigh_beh)

    def advance(self):
        self.behavior = self._nextBehavior
        self.hs_sensi = self._next_hs_sensi
        self.contempt = self._next_contempt



class HateModel(Model):
    """A model of hate speech network"""
    def __init__(self, width, height):
        self.num_agents = width*height
        self.num_nodes = self.num_agents
        # self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=0.1)
        self.G = nx.connected_caveman_graph(l=400, k=4)
        self.G = nx.barabasi_albert_graph(400, 10)
        # x = list(decomposition(400))
        # self.G = nx.random_partition_graph(x, 0.7, 0.1)
        self.grid = NetworkGrid(self.G)
        self.schedule = SimultaneousActivation(self)
        self.running = True

        i = 0
        # Create agents
        list_of_random_nodes = self.random.sample(self.G.nodes(), self.num_agents)

        for i in range(self.num_agents):
            a = HateAgent(i, self)
            self.grid.place_agent(a, list_of_random_nodes[i])
            self.schedule.add(a)

        # for (contents, x, y) in self.grid.coord_iter():
        #     a = HateAgent(i, self)
        #     i += 1
        #     self.grid.place_agent(a, (x, y))
        #     self.schedule.add(a)

        self.datacollector = DataCollector(
            model_reporters={"PerHate": percent_haters,
                             "AveSens": average_sens,
                             "AveCont": average_contempt,
                             "CorHatCon": cor_hate_cont},
            agent_reporters={"Hate": "behavior"}
        )

    def step(self):
        '''Advance the model by one step'''
        self.datacollector.collect(self)
        self.schedule.step()