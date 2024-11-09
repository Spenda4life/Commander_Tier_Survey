
// Get the container for the network
var container = document.getElementById('network');

// Prepare the data for nodes and edges
var max_edge_length = 1000;
var data = {
    nodes: new vis.DataSet(graphData.nodes.map(function(node) {
        return {
            id: node.id,
            label: node.commander,
            // group: node.group
        };
    })),
    edges: new vis.DataSet(
        graphData.edges
            .filter(function(edge) {
                return edge.weight !== undefined;
            })
            .map(function(edge) {
                return {
                    from: edge.source,
                    to: edge.target,
                    length: max_edge_length / (1 + Math.exp(edge.weight))
                };
            }
        )
    )
};

// Define options for the network
var options = {
    physics: {
        enabled: true,
    },
    nodes: {
        shape: 'dot',
        size: 12,
    },
    edges: {
        smooth: false,
        width: 0.1,
    }
};

// Initialize the network
var network = new vis.Network(container, data, options);
