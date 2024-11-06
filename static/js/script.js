// Get the container for the network
var container = document.getElementById('network');


// Prepare the data for nodes and edges
var data = {
    nodes: new vis.DataSet(graphData.nodes.map(function(node) {
        return {
            id: node.id,
            label: node.commander
        };
    })),
    edges: new vis.DataSet(
        graphData.edges
        .filter(function(edge) {
            return edge.weight > 0;  // Filter out edges with weight <= 0
        })
        .map(function(edge) {
            return {
                from: edge.source,
                to: edge.target,
                weight: edge.weight
            };
        })
    )
};


// Define options for the network
var options = {
    physics: {
        enabled: true,
        barnesHut: {
            gravitationalConstant: -2000,    // Controls attraction between nodes
            springLength: 150,               // Ideal distance between nodes
            springConstant: 0.04,            // Determines "stiffness" of edges
        },
    },
    nodes: {
        shape: 'dot',
        size: 10,
        font: {
            size: 12,
            face: 'Verdana',
            color: '#054d73'
        }
    },
    edges: {
        smooth: false,
        width: 0.25
    }
};


// Initialize the network
var network = new vis.Network(container, data, options);
