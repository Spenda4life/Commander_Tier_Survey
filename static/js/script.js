{/* <script>

        // Parse the graph data passed from Flask
        var graphData = {{ graph | tojson | safe }};

        // Create a Vis.js Network
        var container = document.getElementById('network');
        var data = {
            nodes: new vis.DataSet(graphData.nodes.map(function(node) {
                return {
                    id: node.id,
                    label: node.commander
                }
            })),
            edges: new vis.DataSet(graphData.edges.map(function(edge) {
                return {
                    from: edge.source,
                    to: edge.target,
                    weight: edge.weight
                };
            }))
        };

        var options = {
            physics: {
                enabled: true  // Disable physics simulation
            },
            nodes: {
                shape: 'dot',
                size: 10,
                hover: {
                    font: {
                        size: 12,
                        face: 'Verdana',
                        color: '#054d73'
                    }
                }
            },
            edges: {
                smooth: false,
                width: 0.25
            }
        };
        
        var network = new vis.Network(container, data, options);

    </script> */}

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
    edges: new vis.DataSet(graphData.edges.map(function(edge) {
        return {
            from: edge.source,
            to: edge.target,
            weight: edge.weight
        };
    }))
};

// Define options for the network
var options = {
    physics: {
        enabled: true  // Enable or disable physics simulation as needed
    },
    nodes: {
        shape: 'dot',
        size: 10,
        hover: {
            font: {
                size: 12,
                face: 'Verdana',
                color: '#054d73'
            }
        }
    },
    edges: {
        smooth: false,
        width: 0.25
    }
};

// Initialize the network
var network = new vis.Network(container, data, options);
