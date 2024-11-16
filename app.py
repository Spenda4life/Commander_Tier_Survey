from flask import Flask, render_template, redirect, url_for, request, jsonify
from google.cloud import storage
import random
import networkx as nx
import pickle
import math


def write_graph_to_gcs(graph):
    blob = bucket.blob(file_name)
    data = pickle.dumps(graph)
    blob.upload_from_string(data=data)
    print(f"Data written to gs://{bucket_name}/{file_name}")


def read_graph_from_gcs():
    blob = bucket.blob(file_name)
    data = blob.download_as_string()
    graph = pickle.loads(data)
    return graph


def update_graph(options,selection):
    '''Update network graph based on user selection'''

    # global G

    if all([not x for x in selection]): # checks for list of empty strings
        print(f'No selections were made. Graph was not updated.')
    else:
        G = read_graph_from_gcs()

        # loop through all combinations of options
        number_of_options = len(options)
        for i in range(number_of_options):
            for j in range(i + 1, number_of_options):

                # get node id for both options
                node1 = get_node(G, "commander", options[i])
                node2 = get_node(G, "commander", options[j])

                # if both options have been selected, increase weight
                increment = 2
                if options[i] in selection and options[j] in selection:
                    if G.has_edge(node1, node2):
                        G[node1][node2]['weight'] += increment
                        print(f'Increasing weight between {options[i]} (Node: {node1}) and {options[j]} (Node: {node2}) to {G[node1][node2]["weight"]}')
                    else:
                        G.add_edge(node1, node2, weight=increment)
                        print(f'Adding edge between {options[i]} (Node: {node1}) and {options[j]} (Node: {node2}) with weight {increment}')

                # if only one is selected, decrease weight
                decrement = -1
                if (options[i] in selection) ^ (options[j] in selection):
                    if G.has_edge(node1, node2):
                        G[node1][node2]['weight'] += decrement
                        print(f'Decreasing weight between {options[i]} (Node: {node1}) and {options[j]} (Node: {node2}) to {G[node1][node2]["weight"]}')
                    else:
                        G.add_edge(node1, node2, weight=decrement)
                        print(f'Adding edge between {options[i]} (Node: {node1}) and {options[j]} (Node: {node2}) with weight {decrement}')

        write_graph_to_gcs(G)


def get_node(G, attr_name, attr_value):
    '''Return graph node with the matching attribute'''
    for node, attr in G.nodes(data=True):
        if attr.get(attr_name) == attr_value:
            return node


def get_options_by_owner(G):
    owners = []
    decks = []
    while len(decks) < 4:
        random_deck = random.choice(list(G.nodes(data=True)))
        commander = random_deck[1]['commander']
        owner = commander.split('(')[1].strip(')')
        if owner not in owners:
            owners.append(owner)
            decks.append(random_deck[1])
    return decks


def louvian_partition(G):
    # convert edge weights to an edge strength using sigmoid function
    k = -.125
    for _,_,data in G.edges(data=True):
        data["strength"] =1 / (1 + math.exp(k * data["weight"]))

    # determine louvian partition
    partition = nx.community.louvain_communities(G, weight="strength")
    return partition


def get_options_by_community(G):

    # get louvian partition
    partition = louvian_partition(G)
    
    # select 4 random nodes from a random partition
    valid_partitions = [community for community in partition if len(community) >= 4]
    if valid_partitions:
        random_part = random.choice(valid_partitions)
        nodes = random.sample(sorted(random_part), 4)
    else:
        nodes = random.sample(sorted(G.nodes), 4)

    nodes_as_dict = [G.nodes(data=True)[node] for node in nodes]
    return nodes_as_dict


# google cloud storage variables
bucket_name = 'ptero_cloud_storage'
file_name = 'decks_graph.pickle'
client = storage.Client()
bucket = client.bucket(bucket_name)

app = Flask(__name__)


@app.route('/')
def home():
    G = read_graph_from_gcs()
    # decks = get_options_by_owner(G)
    decks = get_options_by_community(G)
    return render_template('index.html', decks=decks)


@app.route('/graph')
def display_graph():
    return render_template('network_graph.html')


@app.route('/communities')
def communities():
    return render_template('communities.html')


@app.route('/submit', methods=['POST'])
def submit():
    options = request.form.getlist('options')
    selection = request.form.getlist('selection')
    print(f'Options: {options}\nSelection: {selection}')
    update_graph(options,selection)
    return redirect(url_for('home'))


@app.route('/get_graph')
def get_graph():
    G = read_graph_from_gcs()
    graph_data = nx.node_link_data(G, edges="edges")
    return jsonify(graph_data)


@app.route('/get_communities')
def get_communities():
    G = read_graph_from_gcs()
    partition = louvian_partition(G)
    result = [[G.nodes(data=True)[node] for node in community] for community in partition]
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)