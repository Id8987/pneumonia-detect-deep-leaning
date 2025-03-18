# import os
# import cv2
# import numpy as np
# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from tensorflow.keras.models import load_model
#
#
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['UPLOAD_FOLDER'] = 'static/uploads'
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
#
# db = SQLAlchemy(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
#
# # Chargement du modèle
# model = load_model('models/pneumonia_model.h5', compile=False)
# IMG_SIZE = 224
#
# class AnalysisHistory(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     filename = db.Column(db.String(200))
#     result = db.Column(db.String(50))
#     confidence = db.Column(db.Float)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#
# class UserFeedback(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_history.id'))
#     comment = db.Column(db.Text)
#     rating = db.Column(db.Integer)  # 1-5 stars
#
#
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     analyses = db.relationship('AnalysisHistory', backref='user', lazy=True)
#     feedbacks = db.relationship('UserFeedback', backref='user', lazy=True)
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
# def clahe_enhancement(img):
#     lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
#     l, a, b = cv2.split(lab)
#     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#     l_clahe = clahe.apply(l)
#     return cv2.cvtColor(cv2.merge((l_clahe, a, b)), cv2.COLOR_LAB2RGB)
#
# def create_perturbation(image):
#     # Ajout de bruit gaussien
#     perturbed = cv2.GaussianBlur(image, (5,5), 0)
#     # Légère rotation
#     rows, cols = image.shape[:2]
#     M = cv2.getRotationMatrix2D((cols/2, rows/2), 5, 1)
#     return cv2.warpAffine(perturbed, M, (cols, rows))
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = generate_password_hash(request.form['password'])
#
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists!')
#             return redirect(url_for('register'))
#
#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html')
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('dashboard'))
#         flash('Invalid credentials!')
#     return render_template('login.html')
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('index'))
#
# @app.route('/dashboard')
# @login_required
# def dashboard():
#     # Récupérer les 5 dernières analyses
#
#     history = AnalysisHistory.query.filter_by(user_id=current_user.id) \
#         .order_by(AnalysisHistory.timestamp.desc()) \
#         .limit(5).all()
#
#     # Statistiques de base
#     stats = {
#         'total_scans': len(current_user.analyses),
#         'positive_percentage': round(
#             len([a for a in current_user.analyses if a.result == 'PNEUMONIA']) /
#             len(current_user.analyses) * 100, 2
#         ) if len(current_user.analyses) > 0 else 0
#     }
#     return render_template('dashboard.html')
#
# @app.route('/analysis/<int:analysis_id>')
# @login_required
# def analysis_details(analysis_id):
#     analysis = AnalysisHistory.query.get_or_404(analysis_id)
#     if analysis.user_id != current_user.id:
#         abort(403)
#     return render_template('analysis_details.html', analysis=analysis)
#
# @app.route('/export-report/<int:analysis_id>')
# @login_required
# def export_report(analysis_id):
#     # Génération PDF avec ReportLab (exemple simplifié)
#     # ... implémentation de la génération PDF ...
#     return send_file(pdf_path, as_attachment=True)
#
# @app.route('/feedback', methods=['POST'])
# @login_required
# def submit_feedback():
#     analysis_id = request.form.get('analysis_id')
#     comment = request.form.get('comment')
#     rating = request.form.get('rating')
#
#     new_feedback = UserFeedback(
#         analysis_id=analysis_id,
#         comment=comment,
#         rating=rating,
#         user_id=current_user.id
#     )
#     db.session.add(new_feedback)
#     db.session.commit()
#
#     flash('Merci pour votre feedback!', 'success')
#     return redirect(url_for('analysis_details', analysis_id=analysis_id))
# @app.route('/analyze', methods=['POST'])
# @login_required
# def analyze():
#     if 'file' not in request.files:
#         flash('No file uploaded!')
#         return redirect(url_for('dashboard'))
#
#     file = request.files['file']
#     if file.filename == '':
#         flash('No selected file!')
#         return redirect(url_for('dashboard'))
#
#     # Sauvegarde de l'image originale
#     filename = f"user_{current_user.id}_{file.filename}"
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(filepath)
#
#     # Prétraitement
#     img = cv2.imread(filepath)
#     img_processed = clahe_enhancement(img)
#     img_resized = cv2.resize(img_processed, (IMG_SIZE, IMG_SIZE)) / 255.0
#
#     # Création d'image contradictoire
#     perturbed = create_perturbation(img_processed)
#     perturbed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"perturbed_{filename}")
#     cv2.imwrite(perturbed_path, perturbed)
#
#     # Prédiction
#     prediction = model.predict(np.expand_dims(img_resized, axis=0))[0][0]
#     diagnosis = "PNEUMONIA" if prediction > 0.4 else "NORMAL"
#
#     return render_template('result.html',
#                            original=filename,
#                            perturbed=f"perturbed_{filename}",
#                            diagnosis=diagnosis,
#                            confidence=round(float(prediction), 2))
#
#
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

import os
import cv2
import io
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import tensorflow as tf
from flask_migrate import Migrate

# Configuration de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['REPORT_FOLDER'] = 'reports'

# Initialisation des extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configuration du modèle
IMG_SIZE = 224
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    analyses = db.relationship('AnalysisHistory', backref='user', lazy=True)
    feedbacks = db.relationship('UserFeedback', backref='user', lazy=True)

class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.relationship('UserFeedback', backref='analysis', uselist=False)
    denoised=db.Column(db.Boolean, default=False)


class UserFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_history.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

def denoise_image(image):
    """Applique un débruitage non-local avec OpenCV"""
    return cv2.fastNlMeansDenoisingColored(
        src=image,
        h=10,               # Paramètre de force du débruitage
        hColor=10,
        templateWindowSize=7,
        searchWindowSize=21
    )
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Fonctions de traitement d'image
def clahe_enhancement(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l_clahe = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l_clahe, a, b)), cv2.COLOR_LAB2RGB)

def create_perturbation(image):
    perturbed = cv2.GaussianBlur(image, (5,5), 0)
    rows, cols = image.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 5, 1)
    return cv2.warpAffine(perturbed, M, (cols, rows))

# Chargement du modèle
def load_model():
    model = tf.keras.models.load_model('models/pneumonia_model.h5', compile=False)
    # model.layers[0].input_shape = [(None, IMG_SIZE, IMG_SIZE, 3)]
    return model

model = load_model()

# Routes de l'application
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            flash('Nom d\'utilisateur déjà existant!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Identifiants invalides!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    history = AnalysisHistory.query.filter_by(user_id=current_user.id).order_by(AnalysisHistory.timestamp.desc()).limit(5).all()

    stats = {
        'total_scans': len(current_user.analyses),
        'positive_percentage': round(
            len([a for a in current_user.analyses if a.result == 'PNEUMONIA']) /
            len(current_user.analyses) * 100, 2
        ) if len(current_user.analyses) > 0 else 0
    }

    return render_template('dashboard.html', history=history, stats=stats)

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    if 'file' not in request.files:
        flash('Aucun fichier téléversé!')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné!')
        return redirect(url_for('dashboard'))

    filename = f"user_{current_user.id}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    img = cv2.imread(filepath)
    img_processed = clahe_enhancement(img)
    if 'denoise' in request.form:
        img_processed = denoise_image(img_processed)
        denoised_tag = "_denoised"
    else:
        denoised_tag=""
    # filename = f"user_{current_user.id}_{denoised_tag}_{file.filename}"


    img_resized = cv2.resize(img_processed, (IMG_SIZE, IMG_SIZE)) / 255.0

    perturbed = create_perturbation(img_processed)
    perturbed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"perturbed_{filename}")
    cv2.imwrite(perturbed_path, perturbed)

    prediction = model.predict(np.expand_dims(img_resized, axis=0))[0][0]
    diagnosis = "PNEUMONIA" if prediction > 0.4 else "NORMAL"

    new_analysis = AnalysisHistory(
        user_id=current_user.id,
        filename=filename,
        result=diagnosis,
        confidence=float(prediction),
        denoised=('denoise' in request.form)
    )
    db.session.add(new_analysis)
    db.session.commit()

    return render_template('result.html',
                           original=filename,
                           perturbed=f"perturbed_{filename}",
                           diagnosis=diagnosis,
                           confidence=round(float(prediction), 2),
                           analysis_id=new_analysis.id,
                           analysis=new_analysis
                           )

@app.route('/analysis/<int:analysis_id>')
@login_required
def analysis_details(analysis_id):
    analysis = AnalysisHistory.query.get_or_404(analysis_id)
    if analysis.user_id != current_user.id:
        abort(403)
    return render_template('analysis_details.html', analysis=analysis)

def generate_pdf_report(analysis):
    try:
        filename = f"report_{analysis.id}.pdf"
        filepath = os.path.join(app.config['REPORT_FOLDER'], filename)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # En-tête
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "Rapport d'Analyse PneumoScan")
        c.setFont("Helvetica", 12)
        c.drawString(50, 775, f"Date : {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}")

        # Résultats
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 740, "Résultat de l'Analyse :")
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Diagnostic : {analysis.result}")
        c.drawString(50, 700, f"Confiance : {analysis.confidence * 100:.2f}%")

        # Images
        img_original = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'], analysis.filename))
        img_perturbed = ImageReader(os.path.join(app.config['UPLOAD_FOLDER'], f"perturbed_{analysis.filename}"))

        c.drawImage(img_original, 50, 500, width=200, height=150)
        c.drawImage(img_perturbed, 50, 320, width=200, height=150)

        c.drawString(50, 480, "Image Originale")
        c.drawString(50, 300, "Image Perturbée")

        # Pied de page
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, "Ce rapport est généré automatiquement par PneumoScan - Ne pas utiliser comme diagnostic médical définitif")

        c.showPage()
        c.save()

        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())

        return filepath
    except Exception as e:
        app.logger.error(f"Erreur génération PDF : {str(e)}")
        abort(500)

@app.route('/export-report/<int:analysis_id>')
@login_required
def export_report(analysis_id):
    analysis = AnalysisHistory.query.get(analysis_id)

    if not analysis or analysis.user_id != current_user.id:
        abort(404)

    try:
        pdf_path = generate_pdf_report(analysis)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"rapport_pneumoscan_{analysis.id}.pdf",
            mimetype='application/pdf'
        )
    except FileNotFoundError:
        abort(404)

@app.route('/history')
@login_required
def full_history():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    analyses = AnalysisHistory.query.filter_by(user_id=current_user.id) \
        .order_by(AnalysisHistory.timestamp.desc()) \
        .paginate(page=page, per_page=per_page)

    return render_template('full_history.html', analyses=analyses)
@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    analysis_id = request.form.get('analysis_id')
    comment = request.form.get('comment')
    rating = request.form.get('rating')

    new_feedback = UserFeedback(
        analysis_id=analysis_id,
        comment=comment,
        rating=rating,
        user_id=current_user.id
    )
    db.session.add(new_feedback)
    db.session.commit()

    flash('Merci pour votre feedback!', 'success')
    return redirect(url_for('analysis_details', analysis_id=analysis_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()


    app.run(debug=True)