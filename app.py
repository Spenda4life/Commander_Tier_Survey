from flask import Flask, render_template, redirect, url_for, request
from google.cloud import storage
import random
import networkx as nx
import pickle


def write_graph_to_gcs(file_name, graph):
    blob = bucket.blob(file_name)
    data = pickle.dumps(graph)
    blob.upload_from_string(data=data)
    print(f"Data written to gs://{bucket_name}/{file_name}")


def read_graph_from_gcs(file_name):
    blob = bucket.blob(file_name)
    data = blob.download_as_string()
    graph = pickle.loads(data)
    return graph


def update_graph(options,selection):
    '''Update network graph based on user selection'''

    number_of_selections = len(selection)

    if number_of_selections > 0:
        G = read_graph_from_gcs('graph.pickle')

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

        write_graph_to_gcs('graph.pickle', G)
    else:
        print(f'{number_of_selections} selections were made. Graph was not updated.')


def get_node(G, attr_name, attr_value):
    '''Return graph node with the matching attribute'''
    for node, attr in G.nodes(data=True):
        if attr.get(attr_name) == attr_value:
            return node


def get_deck_options(G):
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


# google cloud storage variables
bucket_name = 'ptero_cloud_storage'
client = storage.Client()
bucket = client.bucket(bucket_name)

G = read_graph_from_gcs('graph.pickle')
print(f'Successfully loaded {G}')

app = Flask(__name__)

@app.route('/')
def home():
    decks = get_deck_options(G)
    return render_template('index.html', decks=decks)

@app.route('/submit', methods=['POST'])
def submit():
    options = request.form.getlist('options')
    selection = request.form.getlist('selection')
    print(f'Options: {options}\nSelection: {selection}')
    update_graph(options,selection)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)