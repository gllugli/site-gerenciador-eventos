# Documentação da API REST - SGEA

A API REST do SGEA permite a integração com frontends e outras aplicações, expondo funcionalidades de forma segura e padronizada.

## 1. Autenticação

Para acessar os endpoints protegidos, é necessário obter um token de autenticação.

### Obter Token

- **Endpoint**: `POST /api/login/`
- **Corpo da Requisição**:
  ```json
  {
      "username": "seu-email@dominio.com",
      "password": "sua-senha"
  }
  ```
- **Resposta de Sucesso (200 OK)**:
  ```json
  {
      "token": "seu_token_de_autenticacao"
  }
  ```

Após obter o token, inclua-o no cabeçalho de todas as requisições subsequentes:

`Authorization: Token seu_token_de_autenticacao`

## 2. Endpoints de Eventos

### Listar Eventos

- **Endpoint**: `GET /api/eventos/`
- **Autenticação**: Obrigatória.
- **Parâmetros de Query (Opcionais)**:
  - `search`: Filtra eventos pelo título.
- **Resposta de Sucesso (200 OK)**:
  ```json
  [
      {
          "id": 1,
          "titulo": "Semana da Computação",
          "data_inicio": "2025-10-20",
          "localizacao": "Auditório Principal",
          "organizador_nome": "Administrador Geral"
      }
  ]
  ```

### Detalhar Evento

- **Endpoint**: `GET /api/eventos/<int:pk>/`
- **Autenticação**: Obrigatória.
- **Resposta de Sucesso (200 OK)**:
  ```json
  {
      "id": 1,
      "titulo": "Semana da Computação",
      "descricao": "Palestras e workshops sobre as novas tendências de mercado.",
      "data_inicio": "2025-10-20",
      "horario_inicio": "19:00:00",
      "localizacao": "Auditório Principal",
      "quantidade_vagas": 100,
      "vagas_preenchidas": 42,
      "organizador_nome": "Administrador Geral"
  }
  ```

## 3. Endpoint de Inscrição

### Inscrever-se em um Evento

- **Endpoint**: `POST /api/eventos/<int:pk>/inscrever/`
- **Autenticação**: Obrigatória.
- **Corpo da Requisição**: Vazio.
- **Respostas**:
  - **201 Created**: Inscrição realizada com sucesso.
    ```json
    {
        "status": "Inscrição realizada com sucesso"
    }
    ```
  - **400 Bad Request**: Se o usuário já estiver inscrito, não houver vagas, ou outra regra de negócio impedir a inscrição.
    ```json
    {
        "error": "Você já está inscrito neste evento."
    }
    ```

## 4. Rate Limiting (Throttling)

Para evitar abuso, a API possui limites de requisições por usuário, definidos em `settings.py`:

- **Consulta de eventos**: 20 requisições por dia.
- **Inscrição em eventos**: 50 requisições por dia.

Se o limite for excedido, a API retornará um status `429 Too Many Requests`.
