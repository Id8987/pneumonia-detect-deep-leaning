# PneumoScan: Détection Intelligente de Pneumonie par Radiographie Thoracique

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0%2B-green)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2%2B-orange)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

**PneumoScan** est une application web intelligente utilisant le deep learning pour détecter la pneumonie à partir de radiographies thoraciques. Développée avec Flask et TensorFlow, elle combine IA médicale et fonctionnalités professionnelles pour les professionnels de santé.

![Interface PneumoScan](screenshots/dashboard.png)

## ✨ Fonctionnalités Clés

- **🔒 Authentification Sécurisée**  
  Inscription/Connexion avec hachage des mots de passe
- **🩺 Analyse Intelligente**  
  Détection par CNN (VGG16/EfficientNet) avec taux de confiance
- **🛡 Prétraitement Avancé**
    - Amélioration CLAHE
    - Débruitage non-local
    - Génération d'images contradictoires
- **📊 Historique des Analyses**  
  Suivi complet avec pagination et statistiques
- **📄 Rapports PDF**  
  Génération automatique avec images et résultats
- **💬 Système de Feedback**  
  Évaluation et commentaires par les utilisateurs
- **🎨 Interface Professionnelle**  
  Design responsive avec thème médical

## 🚀 Installation

### Prérequis
- Python 3.9+
- SQLite3
- Git

### Étapes
```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-utilisateur/pneumoscan.git
cd pneumoscan

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
echo "SECRET_KEY=votre_cle_secrete" > .env
echo "DATABASE_URL=sqlite:///database.db" >> .env

# 5. Initialiser la base de données
flask db init
flask db migrate
flask db upgrade

# 6. Télécharger le dataset (depuis Kaggle)
# Placer les images dans 'static/uploads'

# 7. Lancer l'application
flask run
```

## 🖥 Utilisation
1. Inscrivez-vous avec vos identifiants

2. Téléversez une radiographie thoracique

3. Activez la protection anti-bruit si nécessaire

4. Consultez les résultats en temps réel

5. Explorez l'historique des analyses

6. Générez des rapports PDF détaillés

7. Donnez votre feedback sur les résultats

## 🧠 Architecture du Modèle


```python
from tensorflow.keras.applications import VGG16

base_model = VGG16(
weights='imagenet',
include_top=False,
input_shape=(224, 224, 3)
)

model = Sequential([
base_model,
GlobalAveragePooling2D(),
Dense(256, activation='relu'),
Dropout(0.5),
Dense(1, activation='sigmoid')
])
```
### Caractéristiques :

- Transfer Learning avec VGG16/EfficientNet

- Fine-tuning des dernières couches

- Early Stopping et Réduction dynamique du LR

- Métriques : Accuracy, F1-Score, AUC-ROC

## 🔧 Technologies Utilisées
| Composant |	Technologies|
|-----------|--------------|
| Backend	  | Flask, SQLAlchemy|
|Machine Learning|	TensorFlow, Keras, OpenCV|
|Base de Données|	SQLite|
|Frontend|	Bootstrap, Jinja2|
|Visualisation|	Matplotlib, ReportLab|
|Déploiement|	Docker, Gunicorn, Nginx|
## 📊 Performance
|Métrique| 	Valeur |
|--------|-------|
|Accuracy| 	83%  |

## 🙏 Remerciements
Dataset : **Chest X-Ray Images (Pneumonia)**
