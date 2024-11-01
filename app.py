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
    G = read_graph_from_gcs('graph.pickle')

    num_opts = len(options)
    for i in range(num_opts):
        for j in range(i + 1, num_opts):
            if options[i] in selection and options[j] in selection:
                # get node id for both options and add edge between them
                node1 = get_node(G, "commander", options[i])
                node2 = get_node(G, "commander", options[j])
                G.add_edge(node1, node2)

    # write_graph_to_gcs('graph.pickle', G)
    print(f'Adding edge between {node1} and {node2}')


def get_node(G, attr_name, attr_value):
    '''Return graph node with the matching attribute'''
    for node, attr in G.nodes(data=True):
        if attr.get(attr_name) == attr_value:
            return node


app = Flask(__name__)

# google cloud storage variables
bucket_name = 'ptero_cloud_storage'
client = storage.Client()
bucket = client.bucket(bucket_name)

G = read_graph_from_gcs('graph.pickle')

@app.route('/')
def home():
    decks = [G.nodes[node] for node in random.sample(list(G.nodes), 4)]
    return render_template('index.html', decks=decks)

@app.route('/submit', methods=['POST'])
def submit():
    options = request.form.getlist('options')
    selection = request.form.getlist('selection')
    update_graph(options,selection)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)