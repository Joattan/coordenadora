# DOCUMENTAÇÃO TÉCNICA: PROJETO ESTUDOS_UFG (ODORATA)

## 1. VISÃO GERAL DO PROJETO
O projeto **estudos_ufg** é uma plataforma web robusta desenvolvida para a **Odorata**, focada no recrutamento, gestão e capacitação de Coordenadoras de Campo. O sistema funciona como um portal bifásico: uma área pública para captação de novas candidatas e uma área restrita (Guia da Coordenadora) contendo ferramentas de simulação de ganhos, indicadores de performance e uma assistente virtual inteligente baseada em IA.

**Tecnologias Principais:**
- **Framework:** Django 6.0.4 (Python 3.12+)
- **Banco de Dados:** SQLite3 (Desenvolvimento/Produção Leve)
- **IA:** Integração com Groq Cloud (Modelo Llama 3.3 70B) e Google Generative AI.
- **Frontend:** HTML5, CSS3 (Vanilla com foco em UX Premium), JavaScript (ES6+) e jQuery.
- **Deploy:** Configurado para ambientes como Hugging Face Spaces e Render (via WhiteNoise).

---

## 2. ARQUITETURA E ESTRUTURA
O projeto segue o padrão **MTV (Model-Template-View)** do Django, com uma separação clara de responsabilidades em dois aplicativos principais:

### Estrutura de Diretórios:
```text
estudos_ufg/
├── config/              # Configurações globais do projeto (settings, urls, wsgi)
├── core/                # App principal: Home, IA Dora, Simulador de Ganhos
├── coordenadoras/       # App de gestão: Cadastro de candidatas e Painel Admin
├── staticfiles/         # Arquivos estáticos coletados para produção
├── media/               # Uploads de documentos e fotos das candidatas
└── db.sqlite3           # Banco de dados relacional
```

### Divisão de Apps:
1.  **Core:** Responsável pela experiência da usuária logada. Contém a lógica matemática complexa de bônus da Odorata e a integração com o LLM para a assistente "Dora".
2.  **Coordenadoras:** Foca no ciclo de vida da candidata. Gerencia desde o formulário de inscrição (com validações de CPF e CEP) até o workflow de aprovação por um administrador.

---

## 3. MODELS (Banco de Dados)
A entidade central do sistema é o modelo `CandidataCoordenadora`, localizado no app `coordenadoras`.

### Model: CandidataCoordenadora
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `cpf` | CharField | Identificador único (14 chars com máscara). |
| `nome_completo`| CharField | Nome da candidata. |
| `status` | CharField | PENDENTE, AJUSTE, APROVADO, REPROVADO. |
| `media_ganhos` | DecimalField| Ganhos em empresas anteriores. |
| `foto` | ImageField | Foto de perfil da candidata. |
| `documentos_*` | FileField | RG/CNH, CPF, Endereço e Ganhos (upload obrigatório). |

**Regras de Negócio embutidas:** Ao ser marcada como `APROVADO` na view `admin_atualizar_status`, o sistema cria automaticamente um `User` no Django Auth, utilizando o CPF como login e os 6 primeiros dígitos como senha inicial.

---

## 4. VIEWS E URLS
O projeto utiliza um mix eficiente de **Function-Based Views (FBV)** para lógica rápida e **Class-Based Views (CBV)** para operações de CRUD.

### Principais Endpoints:
-   `/coordenadoras/cadastro/` (`CadastroCandidataView` - CBV): Formulário público com upload de arquivos.
-   `/chat/` (`chat_agente` - FBV): Endpoint de processamento da IA Dora. Utiliza `csrf_exempt` para comunicação via JSON/AJAX.
-   `/admin-dashboard/` (`admin_dashboard` - FBV): Painel administrativo customizado com links rápidos e métricas.
-   `/coordenadoras/api/cep/`: Microserviço interno que consome a API ViaCEP para preenchimento automático.

---

## 5. TEMPLATES E FRONTEND
Os templates utilizam o motor nativo do Django. Embora não utilizem uma `base.html` global em todos os arquivos (alguns são autônomos para garantir performance e estilos únicos), eles compartilham uma identidade visual premium baseada nas cores da Odorata (Laranja e Preto).

-   **Componentes Reutilizáveis:** CSS isolado em `guia.css` e `agente_especialista.css`.
-   **Formulários:** Utiliza `ModelForm` (`CandidataRegistrationForm`) para garantir que as validações do banco sejam replicadas no frontend.
-   **Bibliotecas:** 
    -   **jQuery Mask:** Garante que CPF e CEP sejam enviados no formato correto.
    -   **FontAwesome:** Ícones para a interface administrativa e simulador.

---

## 6. AUTENTICAÇÃO E PAINEL ADMIN
O sistema utiliza o `django.contrib.auth` para segurança.

-   **Login:** Customizado em `core/login.html`.
-   **Permissões:** A view `AdminStaffRequiredMixin` protege as rotas de listagem e detalhamento de candidatas, permitindo acesso apenas a usuários com `is_staff=True`.
-   **Admin Customizado:** Além do Django Admin padrão, existe uma interface de gestão no app `coordenadoras` para que gestores regionais possam revisar documentos (`admin_detail.html`) e emitir pareceres.

---

## 7. CÁLCULOS E LÓGICA DE NEGÓCIO
Este é o "coração" do projeto. A lógica de ganhos da Odorata 2026 está implementada em dois lugares para redundância e experiência do usuário:

1.  **Lógica em Python (`core/views.py` -> `calcular_ganhos_odorata`):** Utilizada pela IA Dora para fornecer respostas precisas via chat.
2.  **Lógica em JavaScript (`core/templates/core/index.html`):** Utilizada no Simulador Interativo para feedback em tempo real.

### Algoritmo de Ganhos (Resumo):
- **Taxa por Cadastro:** R$ 25 (5-9 cads) ou R$ 50 (10+ cads).
- **Bateu Levou:** Premiação fixa por faixa de pedidos (ex: 30 pedidos = R$ 300).
- **Comissão sobre Faturamento:** Escalonada de 3% a 11% conforme volume de vendas.

---

## 8. IA DORA (AGENTE INTELIGENTE)
A assistente Dora utiliza a API do **Groq** com o modelo `llama-3.3-70b-versatile`. 

**Diferencial Técnico:** A view `chat_agente` realiza um **processamento prévio (Regex)** para extrair números da conversa e injeta esses dados reais na função Python de cálculo. O resultado é então passado no `System Prompt` para que a IA responda com autoridade matemática, evitando alucinações de valores.

---

## 9. CONFIGURAÇÕES E DEPENDÊNCIAS
O arquivo `settings.py` está configurado para segurança e portabilidade:
-   **WhiteNoise:** Gerencia arquivos estáticos sem necessidade de Nginx/Apache em PaaS.
-   **CSRF_TRUSTED_ORIGINS:** Configurado para domínios `.hf.space` e `.onrender.com`.
-   **Pillow:** Essencial para o processamento de fotos e documentos.

**Principais Dependências (`requirements.txt`):**
- `django>=4.0.0`
- `groq`
- `google-generativeai`
- `python-dotenv` (Gestão de chaves de API em `.env`)

---
*Documentação gerada automaticamente para o projeto estudos_ufg.*
