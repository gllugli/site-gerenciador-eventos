# Casos de Uso - SGEA

Este documento descreve os principais casos de uso do sistema sob a perspectiva dos diferentes perfis de usuário.

## 1. Visitante (Não autenticado)

- **UC01: Visualizar Landing Page**: O visitante pode acessar a página inicial do sistema para conhecer a plataforma.
- **UC02: Realizar Cadastro**: O visitante pode se cadastrar como "Aluno" ou "Professor" através de um formulário de registro.
- **UC03: Realizar Login**: O visitante pode se autenticar no sistema para acessar as áreas restritas.

## 2. Usuário Autenticado (Aluno/Professor)

- **UC04: Visualizar Dashboard**: Após o login, o usuário é direcionado para um painel principal.
- **UC05: Visualizar Eventos**: O usuário pode listar e buscar todos os eventos ativos.
- **UC06: Visualizar Detalhes de um Evento**: O usuário pode ver informações completas de um evento, como descrição, data, local e vagas disponíveis.
- **UC07: Inscrever-se em um Evento**: O usuário pode se inscrever em um evento com vagas disponíveis.
- **UC08: Cancelar Inscrição**: O usuário pode cancelar uma inscrição previamente realizada.
- **UC09: Visualizar Minhas Inscrições**: O usuário pode ver uma lista de todos os eventos em que está inscrito.
- **UC10: Confirmar Presença**: O usuário pode confirmar sua presença em um evento no qual está inscrito.
- **UC11: Baixar Certificado**: O usuário pode visualizar e baixar seus certificados de participação em formato PDF.
- **UC12: Editar Perfil**: O usuário pode atualizar suas informações cadastrais (nome, telefone, instituição).
- **UC13: Alterar Senha**: O usuário pode alterar sua senha de acesso.

## 3. Administrador (Organizador)

- **UC14: Gerenciar Usuários**: O administrador pode criar, listar, buscar, editar e excluir usuários de todos os perfis.
- **UC15: Gerenciar Eventos (CRUD)**: O administrador tem controle total sobre os eventos, podendo criar, editar, visualizar e cancelar qualquer evento.
- **UC16: Visualizar Inscrições de um Evento**: O administrador pode ver a lista de todos os inscritos em um determinado evento.
- **UC17: Visualizar Logs de Auditoria**: O administrador pode consultar um painel com os registros de ações importantes realizadas no sistema.
