from flask import Flask, render_template, redirect, url_for, request
import random
import json

def load_json(path):
   with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)
   return data

def update_edges(options, selection):
    '''Update the edges list based on options and user selection'''
    # load edges
    edges = load_json('data/edges.json')

    # loop for each possible edge
    for i in range(4):
        for j in range(i + 1, 4):

            # get edge index from two node IDs
            index = (
                int(options[i]) * (len(nodes) - 1) 
                - (int(options[i]) * (int(options[i]) + 1) // 2) 
                + (int(options[j]) - int(options[i]) - 1)
            )

            # update edge "distance value" based on selection
            if options[i] in selection and options[j] in selection:
                edges[index] -= 1 # gets closer
            else:
                edges[index] += 1 # gets farther 

    # save edges
    with open('data/edges.json', 'w') as f:
        f.write(json.dumps(edges))


app = Flask(__name__)
nodes = load_json('data/nodes.json')
# edges = [0] * (len(nodes) * (len(nodes) - 1) // 2)

@app.route('/')
def home():
    return render_template('index.html', decks=random.sample(nodes, 4))

@app.route('/submit', methods=['POST'])
def submit():
    options = request.form.getlist('options')
    selection = request.form.getlist('selection')
    # update_edges(options,selection)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)