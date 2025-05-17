# Sistema de Agendamento - Chácara Cancún 🏡

Um sistema completo de agendamento e gerenciamento de reservas desenvolvido com Flask para a Chácara Cancún. O sistema permite que os clientes façam reservas online e inclui um painel administrativo completo para gerenciamento.

## 🚀 Funcionalidades

### Para Clientes
- ✅ Registro e login de usuários
- 📅 Sistema de reservas com verificação de disponibilidade
- 📝 Assinatura digital de contratos
- 📧 Recebimento de confirmações por email
- 👥 Gestão do número de convidados

### Para Administradores
- 📊 Painel administrativo completo
- ✍️ Sistema de aprovação de reservas
- 📄 Geração e gestão de contratos
- 📨 Envio automático de emails
- 🗑️ Gestão e exclusão de reservas

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python/Flask
- **Banco de Dados:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Frameworks/Bibliotecas:**
  - Bootstrap 5
  - Flask-SQLAlchemy
  - Flask-Login
  - Flask-Mail
  - PDFKit
  - SweetAlert2

## 📋 Pré-requisitos

- Python 3.8+
- wkhtmltopdf (para geração de PDFs)
- Conta Gmail (para envio de emails)

## 🔧 Instalação

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/agendamento-cancun.git
cd agendamento-cancun
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente em um arquivo `.env`:
```env
FLASK_APP=app.py
FLASK_ENV=development
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

5. Inicialize o banco de dados
```bash
flask db upgrade
```

6. Execute o aplicativo
```bash
flask run
```

## 📝 Uso

### Acesso ao Sistema
- **URL:** `http://localhost:5000`
- **Admin:** admin@chacaracancun.com
- **Senha:** admin123

### Fluxo de Reserva
1. Cliente se registra/faz login
2. Seleciona data e número de convidados
3. Assina o contrato digitalmente
4. Administrador aprova e assina
5. Cliente recebe confirmação por email

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Próximas Melhorias

- [ ] Sistema de pagamentos integrado
- [ ] Galeria de fotos da chácara
- [ ] Sistema de avaliações
- [ ] Calendário visual de disponibilidade
- [ ] Notificações por WhatsApp
- [ ] App mobile

## 📞 Contato

Se você tiver alguma dúvida ou sugestão, não hesite em entrar em contato:

- **Email:** contato@chacaradelazer.com
- **WhatsApp:** (63) 98119-8884
- **Instagram:** @chacaracancunpmw

---
Desenvolvido com ❤️ por [João Lucas]. 
