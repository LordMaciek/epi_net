from model import *
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.ModularVisualization import ModularServer

def network_portrayal(G):
    portrayal = dict()
    portrayal['nodes'] = [
        {"id": node_id,
         "size": agents[0].hate,
         "color": "black" if agents[0].behavior == 1 else "#999999"}
        for (node_id, agents) in G.nodes.data('agent')
    ]

    portrayal['egdes'] = [
        {"id": edge_id,
         "source": source,
         "target": target,
         "color": "#111111"
         } for edge_id, (source, target) in enumerate(G.edges)
    ]

    return portrayal

grid = NetworkModule(network_portrayal)


PerHate = ChartModule([{"Label": "PerHate",
                      "Color": "Black"}],
                    data_collector_name="datacollector")

chartHate = ChartModule([{"Label": "AveHate",
                      "Color": "Black"}],
                    data_collector_name="datacollector")

server = ModularServer(NormModel,
                       [grid,
                        PerHate,
                        chartHate,
                        ],
                       "Hate Speech Model",
                       {"size": 1000})
server.port = 8521