import gdown
import pickle
from flask import Flask, request, jsonify
import numpy as np

# Initialiser l'application Flask
app = Flask(__name__)

# URL du fichier Google Drive
url = "https://drive.google.com/uc?id=1DjNE93a66FWAiKbyKDOaLeqEej9hzdkd"  # ID tiré du lien partagé

# Téléchargement du fichier
output = "model.pkl"
gdown.download(url, output, quiet=False)

# Charger le modèle
with open(output, 'rb') as file:
    model = pickle.load(file)
print("Modèle chargé avec succès !")

# Route d'accueil pour vérifier que l'API fonctionne
@app.route('/', methods=['GET'])
def home():
    return "API Flask fonctionne et est prête à recevoir des prédictions !"

# Route pour effectuer des prédictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Récupérer les données JSON envoyées dans la requête
        data = request.get_json()

        # Vérifier si la clé "features" est présente
        if 'features' not in data:
            return jsonify({'error': "Les données doivent inclure une clé 'features' contenant une liste de caractéristiques."}), 400

        # Convertir les données en tableau numpy
        features = np.array(data['features']).reshape(1, -1)

        # Faire une prédiction avec le modèle
        prediction = model.predict(features)

        # Retourner la prédiction
        return jsonify({'prediction': prediction.tolist()})
    except Exception as e:
        # Gestion des erreurs
        return jsonify({'error': str(e)}), 500

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
