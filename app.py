from flask import Flask, render_template, redirect, url_for, request
from google.cloud import storage
import random
import json

def write_json_to_gcs(file_name, data):
    blob = bucket.blob(file_name)
    json_data = json.dumps(data)
    blob.upload_from_string(json_data, content_type='application/json')
    print(f"Data written to gs://{bucket_name}/{file_name}")

def read_json_from_gcs(file_name):
    blob = bucket.blob(file_name)
    json_data = blob.download_as_text()
    data = json.loads(json_data)
    return data

def load_json(path):
   with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)
   return data

def update_edges(options, selection):
    '''Update the edges list based on options and user selection'''
    # load edges
    edges = read_json_from_gcs('edges.json')

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
    write_json_to_gcs('edges.json', edges)


app = Flask(__name__)

# google cloud storage variables
bucket_name = 'ptero_cloud_storage'
client = storage.Client()
bucket = client.bucket(bucket_name)

nodes = load_json('data/nodes.json')

@app.route('/')
def home():
    return render_template('index.html', decks=random.sample(nodes, 4))

@app.route('/submit', methods=['POST'])
def submit():
    options = request.form.getlist('options')
    selection = request.form.getlist('selection')
    update_edges(options,selection)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)