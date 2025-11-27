# SGEA – Sistema de Gestão de Eventos Acadêmicos

O **SGEA** é um sistema desenvolvido em **Django** para gerenciar eventos acadêmicos, permitindo que estudantes, professores e organizadores realizem inscrições, controlem presença, emitam certificados e consultem auditorias. O sistema também oferece uma **API REST** para integração com o frontend.

---

## 📌 Funcionalidades Principais

### Usuários
- Cadastro e autenticação de usuários (Aluno, Professor, Organizador)
- Perfis com permissões distintas
- Confirmação de e-mail após cadastro
- Login via sessão (web) e via token (API)

### Eventos
- Cadastro, edição e exclusão de eventos (somente organizador)
- Definição de professor responsável
- Controle de vagas
- Validação de datas e horários
- Upload de banner do evento

### Inscrições
- Inscrição e cancelamento (alunos e professores)
- Impedimento de inscrições duplicadas ou acima do limite
- Marcação de presença pelo organizador

### Certificados
- Emissão automática após o encerramento do evento
- Disponibilização para download pelo participante
- Associação aos eventos e usuários

### API REST
- Autenticação via token
- Consulta de eventos
- Inscrição via API
- Configuração de limites de requisição (throttling)
- Registro de auditoria das ações via API

### Auditoria
- Registro completo de ações do sistema, incluindo:
  - Criação/alteração de eventos
  - Inscrições
  - Geração/consulta de certificados
  - Consultas à API
- Tela exclusiva para organizadores visualizarem logs filtrados por usuário e período

---

## 🗂️ Tecnologias Utilizadas
- Python 3.x
- Django
- Django REST Framework (DRF)
- SQLite ou PostgreSQL
- Bootstrap / HTML / CSS (se usar templates Django)
- Docker (opcional)

---

## 📁 Estrutura Inicial do Projeto

```
/sgea
    /accounts
    /eventos
    /certificados
    /api
    /static
    /media
README.md
requirements.txt
manage.py
```

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/usuario/sgea.git
cd sgea
```

### 2. Criar e ativar um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar o arquivo `.env`
Crie um arquivo `.env` na raiz do projeto com, por exemplo:

```env
SECRET_KEY=suachavesecreta
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.seuservidor.com
EMAIL_PORT=587
EMAIL_HOST_USER=seuemail
EMAIL_HOST_PASSWORD=suasenha
EMAIL_USE_TLS=True
```

### 5. Rodar migrações
```bash
python manage.py migrate
```

### 6. Criar superusuário
```bash
python manage.py createsuperuser
```

### 7. Rodar servidor
```bash
python manage.py runserver
```

---

## 🔧 Carga Inicial de Dados (Opcional)

O sistema pode carregar usuários e eventos iniciais com:

```bash
python manage.py loaddata initial_data.json
```

---

## 📌 Endpoints da API (Resumo)

### Autenticação
- `POST /api/auth/login/` – retorna token de acesso

### Eventos
- `GET /api/eventos/` – lista de eventos
- `GET /api/eventos/<id>/` – detalhes
- `POST /api/eventos/<id>/inscrever/` – inscrição

### Certificados
- `GET /api/certificados/` – lista certificados do usuário autenticado

---

## 🧪 Guia de Testes Essenciais

- Criar usuário → confirmar e-mail → login
- Criar evento com professor responsável
- Tentar criar evento com data retroativa (deve falhar)
- Inscrever aluno até esgotar vagas
- Tentar inscrição duplicada (deve falhar)
- Marcar presença
- Gerar certificados
- Fazer requisições via API com throttling
- Consultar auditoria

---

## 📄 Licença

Este projeto é distribuído para fins acadêmicos.
Caso utilize como base para outros projetos, cite a fonte.
