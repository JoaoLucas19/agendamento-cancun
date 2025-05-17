from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from flask_mail import Mail, Message
import os
from functools import wraps
import pdfkit
from io import BytesIO
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chacara.db')

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_USE_UNICODE'] = True

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Modelo do Usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

# Decorador para rotas que requerem admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Modelo de Contrato
class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_signature = db.Column(db.Text)
    client_signature_date = db.Column(db.DateTime)
    admin_signature = db.Column(db.Text)
    admin_signature_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, signed, completed

# Modelo de Reserva
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    contract = db.relationship('Contract', backref='reservation', uselist=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')

        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'danger')
            return redirect(url_for('register'))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone
        )
        db.session.add(user)
        db.session.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos!', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')
@login_required
@admin_required
def admin():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin.html', reservations=reservations)

@app.route('/admin/approve/<int:id>')
@login_required
@admin_required
def approve_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    reservation.status = 'approved'
    db.session.commit()
    flash('Reserva aprovada com sucesso!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:id>')
@login_required
@admin_required
def reject_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    reservation.status = 'rejected'
    db.session.commit()
    flash('Reserva rejeitada com sucesso!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:id>')
@login_required
@admin_required
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    
    # Se existir um contrato, delete primeiro
    if reservation.contract:
        db.session.delete(reservation.contract)
    
    # Delete a reserva
    db.session.delete(reservation)
    db.session.commit()
    
    flash('Reserva excluída com sucesso!', 'success')
    return redirect(url_for('admin'))

@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    if request.method == 'POST':
        check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d')
        check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d')
        guests = int(request.form.get('guests'))
        notes = request.form.get('notes')

        # Validações
        if check_in >= check_out:
            flash('Data de check-out deve ser posterior ao check-in!', 'danger')
            return redirect(url_for('reserve'))

        if guests < 10 or guests > 100:
            flash('O número de convidados deve ser entre 10 e 100 pessoas!', 'danger')
            return redirect(url_for('reserve'))

        # Verificar disponibilidade
        conflicting_reservations = Reservation.query.filter(
            db.and_(
                Reservation.status != 'rejected',
                db.or_(
                    db.and_(
                        Reservation.check_in <= check_in,
                        Reservation.check_out >= check_in
                    ),
                    db.and_(
                        Reservation.check_in <= check_out,
                        Reservation.check_out >= check_out
                    ),
                    db.and_(
                        Reservation.check_in >= check_in,
                        Reservation.check_out <= check_out
                    )
                )
            )
        ).first()

        if conflicting_reservations:
            flash('Período indisponível para reserva! Por favor, escolha outras datas.', 'danger')
            return redirect(url_for('reserve'))

        # Criar reserva
        reservation = Reservation(
            user_id=current_user.id,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            notes=notes
        )
        db.session.add(reservation)
        db.session.commit()

        # Criar contrato
        contract = Contract(reservation_id=reservation.id)
        db.session.add(contract)
        db.session.commit()

        flash('Reserva solicitada com sucesso! Por favor, assine o contrato.', 'success')
        return redirect(url_for('view_contract', reservation_id=reservation.id))

    return render_template('reserve.html')

@app.route('/contract/<int:reservation_id>')
@login_required
def view_contract(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if not reservation.contract:
        contract = Contract(reservation_id=reservation.id)
        db.session.add(contract)
        db.session.commit()
    
    if current_user.id != reservation.user_id and not current_user.is_admin:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('contract.html', reservation=reservation, timedelta=timedelta)

def send_contract_email(reservation, contract_pdf):
    """Envia o contrato assinado por email para o cliente."""
    try:
        msg = Message(
            subject='Reserva Aprovada - Chácara Cancún',
            sender=('Chácara Cancún', app.config['MAIL_DEFAULT_SENDER']),
            recipients=[reservation.user.email],
            charset='utf-8'
        )
        
        # Renderiza o template do email com encode utf-8
        msg.html = render_template(
            'email/reservation_approved.html',
            user=reservation.user,
            reservation=reservation
        ).encode('utf-8').decode('utf-8')
        
        # Anexa o PDF do contrato
        msg.attach(
            'contrato_chacara_cancun_{}.pdf'.format(reservation.id),
            'application/pdf',
            contract_pdf
        )
        
        mail.send(msg)
        print("Email enviado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        import traceback
        traceback.print_exc()  # Isso vai imprimir o stack trace completo
        return False

@app.route('/contract/sign/<int:reservation_id>', methods=['POST'])
@login_required
def sign_contract(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    contract = reservation.contract

    if not contract:
        flash('Contrato não encontrado!', 'danger')
        return redirect(url_for('index'))

    signature = request.form.get('signature')
    
    if current_user.id == reservation.user_id:
        contract.client_signature = signature
        contract.client_signature_date = datetime.now(timezone.utc)
        flash('Contrato assinado com sucesso! Aguardando aprovação do administrador.', 'success')
    elif current_user.is_admin:
        contract.admin_signature = signature
        contract.admin_signature_date = datetime.now(timezone.utc)
        contract.status = 'completed'
        reservation.status = 'approved'
        
        # Gera o PDF do contrato
        try:
            html_content = render_template(
                'contract_pdf.html',
                reservation=reservation,
                contract=contract,
                timedelta=timedelta
            )
            
            config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
            pdf = pdfkit.from_string(html_content, False, options={
                'page-size': 'A4',
                'margin-top': '2.5cm',
                'margin-right': '2.5cm',
                'margin-bottom': '2.5cm',
                'margin-left': '2.5cm',
                'encoding': 'UTF-8',
                'no-outline': None
            }, configuration=config)
            
            # Envia o email com o contrato
            if send_contract_email(reservation, pdf):
                flash('Contrato aprovado e enviado por email com sucesso!', 'success')
            else:
                flash('Contrato aprovado, mas houve um erro ao enviar o email.', 'warning')
        except Exception as e:
            flash(f'Contrato aprovado, mas houve um erro ao gerar o PDF: {str(e)}', 'warning')
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/contract/download/<int:reservation_id>')
@login_required
def download_contract(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    contract = reservation.contract

    # Verifica se o contrato está assinado
    if not contract or contract.status != 'completed':
        flash('O contrato precisa estar assinado por ambas as partes para download.', 'warning')
        return redirect(url_for('view_contract', reservation_id=reservation_id))

    # Verifica se o usuário tem permissão para baixar
    if current_user.id != reservation.user_id and not current_user.is_admin:
        flash('Você não tem permissão para baixar este contrato.', 'danger')
        return redirect(url_for('index'))

    try:
        # Gera o HTML do contrato
        html_content = render_template(
            'contract_pdf.html',
            reservation=reservation,
            contract=contract,
            timedelta=timedelta
        )
        
        # Configuração do wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        
        # Opções do PDF
        options = {
            'page-size': 'A4',
            'margin-top': '2.5cm',
            'margin-right': '2.5cm',
            'margin-bottom': '2.5cm',
            'margin-left': '2.5cm',
            'encoding': 'UTF-8',
            'no-outline': None
        }
        
        # Gera o PDF em memória
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)
        
        return send_file(
            BytesIO(pdf),
            download_name=f'contrato_chacara_cancun_{reservation.id}.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Erro ao gerar o PDF: {str(e)}', 'error')
        return redirect(url_for('view_contract', reservation_id=reservation_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar usuário admin se não existir
        admin_email = "admin@chacaracancun.com"
        if not User.query.filter_by(email=admin_email).first():
            admin_user = User(
                name="Administrador",
                email=admin_email,
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
            print("Email: admin@chacaracancun.com")
            print("Senha: admin123")
    app.run(debug=True) 