
# Sistema de Gestão de Eventos Acadêmicos (SGEA) – Requisitos do Backend

## 1. Visão geral

O Sistema de Gestão de Eventos Acadêmicos (SGEA) é uma aplicação web voltada à gestão de eventos acadêmicos (palestras, seminários, minicursos, semanas acadêmicas etc.) de uma instituição de ensino superior.  
O backend será desenvolvido em **Django** com **Django REST Framework (DRF)**, oferecendo:

- Interface administrativa para organizadores e equipe interna.
- API REST para consumo pelo frontend web.
- Serviços de autenticação, autorização, inscrição e emissão de certificados.

Este documento resume, em linguagem técnica, os requisitos extraídos dos enunciados do projeto da disciplina de Programação para Web (Fase 1 e Fase 2), servindo como referência principal para o desenvolvimento do backend.

---

## 2. Objetivos do sistema

1. **Gerenciar usuários** (alunos, professores, organizadores) com autenticação segura.
2. **Gerenciar eventos acadêmicos**, permitindo cadastro, edição, listagem e cancelamento.
3. **Permitir inscrições em eventos** pelos usuários autenticados, respeitando regras de capacidade e datas.
4. **Registrar presenças e gerar certificados** para os participantes.
5. **Disponibilizar API REST** para consulta de eventos e realização de inscrições, integrada ao frontend.
6. **Manter trilha de auditoria** das principais ações (cadastro, edição de eventos, inscrições, geração de certificados).
7. **Garantir segurança de acesso**, validações e limites de uso da API.

---

## 3. Escopo do backend

### 3.1 Incluído no escopo

- Implementação de modelos, migrations e regras de negócio em Django.
- Implementação de views, serializers e rotas da API REST.
- Autenticação, autorização e controle de permissões.
- Camada de serviços para inscrição, confirmação de presença e geração de certificados (estrutura).
- Integração com o frontend via endpoints REST (JSON).
- Configuração de logs/auditoria e throttling da API.
- Configuração de ambiente (settings, banco, static/media, DRF).

### 3.2 Fora do escopo do backend

- Implementação do frontend (HTML, CSS, JS/Frameworks).
- Hospedagem e deploy em produção (podem ser considerados em documentação complementar).
- Geração gráfica avançada de certificados (layout complexo em PDF) – pode ser representada por um stub/estrutura mínima.
- Envio real de e-mails em produção (backends de e-mail podem ser simulados em ambiente de desenvolvimento).

---

## 4. Perfis de usuário e permissões

### 4.1 Perfis

- **Aluno**
- **Professor**
- **Organizador** (administrador do sistema de eventos)

### 4.2 Permissões gerais

#### Aluno / Professor

- Cadastrar-se no sistema.
- Autenticar-se (login/logout).
- Atualizar dados do próprio perfil.
- Listar eventos disponíveis.
- Visualizar detalhes de eventos.
- Inscrever-se em eventos (dentro das regras de negócio).
- Cancelar inscrições (respeitando prazos definidos).
- Consultar histórico de eventos e certificados emitidos para si.

#### Organizador

- Todas as ações de Aluno/Professor.
- Gerenciar eventos (criar, editar, cancelar).
- Definir vagas, datas, horários e professores responsáveis.
- Consultar e gerenciar inscrições de cada evento.
- Registrar presenças (manual ou importação em lote).
- Gerar/emitir certificados para os participantes elegíveis.
- Acessar relatórios básicos (inscrições, presença, certificados).
- Consultar registros de auditoria (logs de ações relevantes).

---

## 5. Modelo de dados (conceitual resumido)

> Este modelo será refinado na fase de modelagem física (models.py).

### 5.1 Usuário (User / CustomUser + Profile)

Campos principais:

- `first_name` (obrigatório)
- `last_name` (obrigatório)
- `email` (obrigatório, único – utilizado como login)
- `password` (hash)
- `phone` (opcional ou obrigatório, conforme decisão)
- `institution` (instituição de ensino)
- `profile_type` (ALUNO, PROFESSOR, ORGANIZADOR – choices)
- `is_active` (boolean)
- `date_joined` (datetime)

Regras principais:

- Senha com política mínima (ex.: ≥ 8 caracteres, contendo letras e números).
- Possibilidade de confirmação de e-mail antes da ativação de acesso (pelo menos previsto em nível de requisito).
- E-mail único por usuário.

### 5.2 Evento (Event)

Campos:

- `title` (título do evento)
- `event_type` (palestra, seminário, minicurso, etc. – choices)
- `description` (descrição detalhada)
- `start_date` (data de início)
- `end_date` (data de término)
- `start_time` (horário de início)
- `end_time` (horário de término)
- `location` (local, sala, auditório, link, etc.)
- `capacity` (número máximo de vagas)
- `organizer` (FK para User com perfil ORGANIZADOR)
- `responsible_professor` (FK para User com perfil PROFESSOR)
- `banner` (imagem opcional)
- `is_active` (para cancelamento lógico)
- `created_at` / `updated_at`

Regras:

- Datas e horários devem ser coerentes (start ≤ end).
- Não permitir criação/edição com datas já passadas (regras podem ser definidas em detalhe).
- `capacity` ≥ 0.
- Todo evento deve ter um `responsible_professor` definido.
- Cancelamento de evento deve refletir nas inscrições (ver regras de negócio).

### 5.3 Inscrição (Enrollment / EventRegistration)

Campos:

- `event` (FK Event)
- `user` (FK User)
- `status` (INSCRITO, CANCELADO, PRESENCA_CONFIRMADA – choices)
- `created_at` (data/hora da inscrição)
- `canceled_at` (data/hora do cancelamento, opcional)
- `presence_confirmed_at` (data/hora de confirmação de presença, opcional)

Regras:

- Restrição de unicidade: um usuário só pode ter uma inscrição por evento (`UniqueConstraint(event, user)`).
- Não permitir inscrição se:
  - o evento estiver lotado (`inscritos >= capacity`), ou
  - o evento estiver inativo/cancelado, ou
  - a data de inscrição estiver fora do período permitido.
- Regras de cancelamento (prazo limite, se definido).

### 5.4 Certificado (Certificate)

Campos:

- `event` (FK Event)
- `user` (FK User)
- `issued_at` (data/hora de emissão)
- `verification_code` (código único para verificação do certificado)
- `file` (arquivo PDF ou similar – opcional, dependendo da implementação)

Regras:

- Certificado só pode ser emitido se:
  - o usuário tiver status de presença confirmada no evento.
- `verification_code` deve ser único e imutável após emissão.
- Possibilidade de consulta de certificado por código (endpoint público ou protegido, a definir).

### 5.5 Log/Auditoria (AuditLog)

Campos:

- `user` (FK User, opcional em ações anônimas – ex.: acesso público à API, se houver)
- `action` (ex.: USER_CREATE, USER_UPDATE, EVENT_CREATE, EVENT_UPDATE, EVENT_DELETE, ENROLLMENT_CREATE, ENROLLMENT_CANCEL, CERTIFICATE_ISSUE, API_EVENT_LIST, API_EVENT_ENROLL etc.)
- `object_type` (nome da entidade, ex.: "Event", "User", "Certificate")
- `object_id` (ID do objeto afetado)
- `timestamp` (data/hora da ação)
- `ip_address` (IP de origem, quando possível)
- `extra_data` (JSON com detalhes adicionais da ação)

Regras:

- Registrar, no mínimo, ações de criação/alteração/remoção de eventos, inscrições, usuários e certificados.
- Logs devem ser apenas leitura na interface administrativa (não podem ser alterados via painel).

---

## 6. Requisitos funcionais

### 6.1 Autenticação e controle de acesso

- RF01 – O sistema deve permitir login por e-mail e senha.
- RF02 – O sistema deve permitir logout de usuários autenticados.
- RF03 – O sistema deve permitir recuperação de senha (fluxo de redefinição, mesmo que simplificado em ambiente de desenvolvimento).
- RF04 – O backend deve expor endpoints de autenticação para o frontend (por exemplo, token-based via DRF).
- RF05 – A API deve bloquear acesso a endpoints protegidos para usuários não autenticados ou sem permissão adequada.

### 6.2 Cadastro e gestão de usuários

- RF06 – O sistema deve permitir o cadastro de novos usuários (Alunos, Professores) via formulário ou endpoint REST.
- RF07 – Organizador pode cadastrar usuários (inclusive outros organizadores) via painel administrativo ou endpoints protegidos.
- RF08 – Usuários devem poder atualizar seus dados pessoais (nome, telefone, instituição etc.).
- RF09 – Perfis de usuário (ALUNO, PROFESSOR, ORGANIZADOR) determinam suas permissões de acesso.
- RF10 – O sistema deve validar a unicidade do e-mail no cadastro.

### 6.3 Gestão de eventos

- RF11 – Organizadores podem cadastrar novos eventos com todos os campos obrigatórios.
- RF12 – Organizadores podem editar eventos existentes, desde que o evento não esteja encerrado ou com inscrições bloqueadas por regra.
- RF13 – Organizadores podem cancelar eventos. O cancelamento deve:
  - atualizar o status do evento (`is_active = False`),
  - impedir novas inscrições,
  - registrar log de auditoria.
- RF14 – Usuários (alunos/professores) devem poder listar eventos disponíveis, com filtros básicos:
  - por tipo de evento,
  - por período (próximos eventos),
  - por palavra-chave no título/descrição.
- RF15 – O sistema deve disponibilizar detalhes de um evento específico via endpoint REST.

### 6.4 Inscrições em eventos

- RF16 – Usuários autenticados (Alunos/Professores) podem inscrever-se em eventos ativos, desde que haja vagas.
- RF17 – A tentativa de inscrição em evento lotado deve retornar erro adequado.
- RF18 – Usuários podem cancelar sua inscrição dentro de prazo permitido (se houver essa regra definida).
- RF19 – Organizadores podem visualizar a lista de inscritos de cada evento.
- RF20 – É obrigatório garantir que um usuário tenha, no máximo, uma inscrição por evento (controle pelo modelo de dados).

### 6.5 Registro de presença e certificados

- RF21 – Organizadores podem registrar presença dos inscritos em um evento (individualmente ou via mecanismo em lote).
- RF22 – O sistema deve gerar registros de certificado para participantes com presença confirmada.
- RF23 – O sistema deve permitir a consulta dos certificados emitidos por usuário.
- RF24 – O sistema deve permitir a consulta/validação de certificado por código de verificação.

### 6.6 API REST (integração com o frontend)

- RF25 – O backend deve disponibilizar endpoint para listagem de eventos (para uso pelo frontend).
- RF26 – O backend deve disponibilizar endpoint para detalhes de evento.
- RF27 – O backend deve disponibilizar endpoint para inscrição em evento.
- RF28 – O backend deve disponibilizar endpoint para cancelamento de inscrição.
- RF29 – O backend deve disponibilizar endpoints para login/logout, criação e atualização de usuários.
- RF30 – Endpoints sensíveis devem exigir autenticação e permissão adequada.
- RF31 – A API deve retornar dados em formato JSON.

### 6.7 Auditoria

- RF32 – O sistema deve registrar em log as ações sensíveis:
  - criação, alteração e cancelamento de eventos;
  - criação e cancelamento de inscrições;
  - emissão de certificados;
  - operações administrativas relevantes.
- RF33 – Logs devem ser acessíveis para consulta por organizadores ou administradores, via interface administrativa ou endpoint protegido.

---

## 7. Requisitos não funcionais

### 7.1 Segurança

- RNF01 – Senhas nunca devem ser armazenadas em texto plano (uso do sistema de hashing do Django).
- RNF02 – Endpoints protegidos devem utilizar autenticação por token/session conforme configuração do DRF.
- RNF03 – Dados sensíveis devem ser validados e sanitizados no backend.
- RNF04 – Acesso à interface administrativa do Django deve ser restrito a usuários autorizados.

### 7.2 Desempenho e escalabilidade

- RNF05 – A API deve responder em tempo adequado para a carga esperada da disciplina (turma de alunos).
- RNF06 – Deve haver uso de mecanismos de paginação nos endpoints de listagem (eventos, inscrições etc.) quando necessário.

### 7.3 Usabilidade (do ponto de vista da API/admin)

- RNF07 – As mensagens de erro da API devem ser claras e padronizadas (HTTP status + corpo JSON com detalhes).
- RNF08 – A interface de administração (Django Admin) deve ser configurada para facilitar a gestão de eventos e inscrições.

### 7.4 Manutenibilidade

- RNF09 – O código deve ser organizado em apps coerentes (ex.: `accounts`, `events`, `certificates`, `audit` ou equivalente).
- RNF10 – Devem ser utilizados padrões do Django/DRF (views, serializers, permissions, validators).
- RNF11 – Deve existir um arquivo `README.md` explicando como subir o projeto localmente.

---

## 8. Regras de negócio (resumo)

1. **Perfil do usuário**
   - Usuários possuem um único perfil principal (ALUNO, PROFESSOR ou ORGANIZADOR).
   - Organizador possui acesso ampliado para gestão de eventos, inscrições e certificados.

2. **Inscrições**
   - Um usuário não pode se inscrever duas vezes no mesmo evento.
   - Não é possível inscrever-se em evento com inscrições encerradas ou lotado.
   - Cancelamentos podem ser restritos a um período anterior ao início do evento (regra a ser definida).

3. **Capacidade de eventos**
   - O número de inscritos confirmados não pode ultrapassar a capacidade definida (`capacity`).
   - Alterações na capacidade devem respeitar o número de inscritos já existentes.

4. **Presença e certificação**
   - Certificados só são emitidos para usuários com presença confirmada.
   - Cada certificado é único para a combinação usuário + evento.
   - Cada certificado possui um código de verificação único.

5. **Cancelamento de eventos**
   - Ao cancelar um evento, novas inscrições devem ser bloqueadas.
   - Inscrições existentes devem ter status ajustado (por exemplo, marcado como cancelado pelo sistema), conforme decisão de regra.

6. **Auditoria**
   - Toda ação crítica gera um registro de auditoria.
   - Registros de auditoria não podem ser alterados manualmente via interface do sistema.

---

## 9. Integração com o frontend

- O backend fornecerá endpoints REST que serão consumidos pelo frontend (SPA ou páginas tradicionais).
- Requisitos principais de integração:
  - Autenticação via API (ex.: envio de token em cabeçalho Authorization).
  - Endpoints para listagem e detalhes de eventos.
  - Endpoints para gestão de inscrição (criar/cancelar).
  - Endpoints para consulta de certificados e dados do usuário.
- As URLs e contratos (formato dos JSONs) devem ser documentados posteriormente em um **documento de especificação da API** (OpenAPI/Swagger/opcional).

---

## 10. Considerações finais

Este documento serve como base para:

- Implementação dos modelos (`models.py`).
- Definição das rotas e views (web e API).
- Configuração das permissões e autenticação no DRF.
- Planejamento dos testes de funcionalidade básica.

A partir destes requisitos, o próximo passo é:

1. Finalizar o modelo de dados lógico/físico.
2. Implementar os modelos em Django.
3. Definir as primeiras rotas de autenticação e gestão de eventos.
