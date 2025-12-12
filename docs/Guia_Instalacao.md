# Guia de Instalação – SGEA

## 1. Pré-requisitos
- Python 3.10 ou superior
- Pip
- Ambiente virtual (venv)

## 2. Passos para instalação

1. Clone o repositório do projeto
2. Crie e ative um ambiente virtual
3. Instale as dependências:
   pip install -r requirements.txt
4. Execute as migrações:
   python manage.py migrate
5. Crie um superusuário (opcional):
   python manage.py createsuperuser
6. Execute o servidor:
   python manage.py runserver

## 3. Acesso
- Aplicação: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin
