import matplotlib.pyplot as plt
import networkx as nx

import DataLoader as dl

class NetworkAnalysis:
    def __init__(self, graph_file=None):
        self.graph = None
        if graph_file is not None:
            self.load_graph(graph_file)

    def load_graph(self, graph_file):
        # Load the graph from a file
        self.graph = nx.read_gpickle(graph_file)
    
    def save_graph(self, graph_file):
        # Save the graph to a file
        nx.write_gpickle(self.graph, graph_file)

    def get_degree_distribution(self):
        # Plot a histogram of the degree distribution of the nodes
        degrees = [self.graph.degree(node) for node in self.graph.nodes()]
        plt.hist(degrees, bins=range(max(degrees) + 2))
        plt.xlabel("Degree")
        plt.ylabel("Count")
        plt.title("Degree Distribution of Nodes")
        plt.show()
        return degrees

    def get_top_nodes_by_centrality(self, centrality_measure, n=10):
        # Calculate the centrality of the nodes using the specified measure
        centrality = centrality_measure(self.graph)

        # Sort the nodes by centrality and return the top n
        sorted_nodes = sorted(centrality, key=centrality.get, reverse=True)
        top_n = [(node, centrality[node]) for node in sorted_nodes[:n]]

        return top_n
