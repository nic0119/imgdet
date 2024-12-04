from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient
import requests
from dotenv import load_dotenv
import os

#Chargement des variables d'environnement
load_dotenv()

#Configurations Azure
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = "images"  # Nom du conteneur
COGNITIVE_SERVICE_ENDPOINT = os.getenv("COGNITIVE_SERVICE_ENDPOINT")
COGNITIVE_SERVICE_KEY = os.getenv("COGNITIVE_SERVICE_KEY")

#Initialisation Flask
app = Flask(__name__)

#Initialisation Azure Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

@app.route('/')
def index():
    return render_template('index.html', results=None)

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    if file:
        blob_name = file.filename
        blob_container_client.upload_blob(blob_name, file, overwrite=True)
        image_url = f"https://{BLOB_CONNECTION_STRING.split(';')[1].split('=')[1]}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{blob_name}"
        
        headers = {'Ocp-Apim-Subscription-Key': COGNITIVE_SERVICE_KEY}
        data = {'url': image_url}
        response = requests.post(f"{COGNITIVE_SERVICE_ENDPOINT}/vision/v3.2/analyze?visualFeatures=Tags,Description,Objects", headers=headers, json=data)

        if response.status_code == 200:
            results = response.json()
            return render_template('index.html', results=results)
        else:
            return render_template('index.html', results={"error": "Erreur lors de l'analyse."})
    return render_template('index.html', results={"error": "Aucun fichier uploadé."})

if __name__ == '__main__':
    app.run(debug=True)
