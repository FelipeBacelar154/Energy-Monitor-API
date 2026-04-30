# ⚡ Energy Monitor

Solução Full Stack para monitoramento inteligente de consumo de energia elétrica em ambientes industriais. O sistema permite o cadastro de equipamentos, registro de leituras de consumo e visualização de dados por meio de dashboards dinâmicos.

---

## 🚀 Funcionalidades

- **Gestão de Equipamentos** — Cadastro, listagem e exclusão de ativos industriais
- **Telemetria de Consumo** — Registro de kWh, Voltagem e Corrente
- **Dashboard em Tempo Real** — Visualização de estatísticas gerais e custo estimado (BRL)
- **Gráficos Interativos** — Histórico de consumo por equipamento via Plotly.js
- **Relatórios PDF** — Geração de relatórios profissionais com resumo de custos e tabelas detalhadas
- **Autenticação Segura** — Login e registro com JWT (JSON Web Tokens)

---

## 🛠️ Tecnologias

| Camada | Tecnologias |
|---|---|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, SQLite, ReportLab |
| **Frontend** | HTML5, CSS3 (Dark Theme), JavaScript (Vanilla), Plotly.js |
| **Infra** | Docker, Docker Compose |

---

## 📂 Estrutura do Projeto

```
energy-monitor/
├── backend/
│   ├── app/
│   │   ├── config/       # Conexão com o banco de dados
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── routes/       # Endpoints (Auth, Equipments, Readings)
│   │   ├── services/     # Lógica de negócio (PDF, Auth)
│   │   └── main.py       # Ponto de entrada FastAPI
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
└── README.md
```

---

## 📦 Como Rodar o Projeto

### Opção 1 — Docker (Recomendado)

> Certifique-se de ter o [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução.

```bash
docker-compose up --build
```

Após o build, acesse:

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend (Swagger) | http://localhost:8000/docs |

---

### Opção 2 — Instalação Manual

#### Backend

```bash
# 1. Navegue até a pasta do backend
cd backend

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor
uvicorn app.main:app --reload
```

#### Frontend

Abra o arquivo `frontend/index.html` diretamente no navegador ou utilize a extensão **Live Server** no VS Code / Cursor.

---

## 👨‍💻 Desenvolvedor

Feito por **Felipe Bacelar**