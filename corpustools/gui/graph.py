# Archived method for visualizing functional load
#import igraph as ig

class FLGraph:
    # Plots a graph based on the results of functional load calculation
    #   by taking a list of the phonemes that were calculated, which will be the graph's vertices,
    #   and a list of functional load values, which will be the graph's edges, from the results of
    #   the functional load dialog.
    def __init__(self, results_dict):
        self.graph = ig.Graph()
        self.segments = []
        self.fl_weights = []
        for result in results_dict:
            segment_1 = result['First segment']
            segment_2 = result['Second segment']
            fl_weight = result['Result']

            self.fl_weights.append( [segment_1, segment_2, fl_weight] )
            if not (segment_1 in self.segments):
                self.segments.append(segment_1)
            if not (segment_2 in self.segments):
                self.segments.append(segment_2)

        self.construct_graph()
        # Plots a circular graph with edges connecting all the vertices, where the width of each edge is
        #   50 * functional load
        ig.plot(self.graph, layout=self.graph.layout_circle(), vertex_label=self.graph.vs["name"],
                edge_width=[1-(50 * weight) for weight in self.graph.es["weight"]])

    def construct_graph(self):
        # Creates a graph from self.segments and self.fl_weights
        self.graph.add_vertices(len(self.segments))
        self.graph.vs["name"] = self.segments

        for weight_list in self.fl_weights:
            segment_1 = self.graph.vs.find(name=weight_list[0])
            segment_2 = self.graph.vs.find(name=weight_list[1])

            self.graph.add_edge(segment_1.index, segment_2.index, weight = weight_list[2])
