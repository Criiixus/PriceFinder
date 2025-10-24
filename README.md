# 💸 PriceFinder

O **PriceFinder** é um projeto desenvolvido em **Python** com o objetivo de automatizar a busca de preços de produtos diretamente no **Google**.  
Ele foi criado para ajudar na rotina de quem trabalha com **e-commerce**, especialmente em plataformas como a **Tray**, onde acompanhar os valores dos concorrentes é essencial para manter a competitividade.

---

## 🚀 Funcionalidades

- 🔍 Busca automática de produtos no Google  
- 💰 Tentativa de extração dos preços exibidos nos resultados  
- 🧠 Filtragem e tratamento básico dos dados obtidos  
- 📊 Exibição dos links e preços encontrados no terminal  

---

## 🧩 Tecnologias Utilizadas

- **Python 3.10+**  
- **Requests** — para fazer as requisições HTTP  
- **BeautifulSoup (bs4)** — para análise e extração do HTML  
- **Regex** — para localizar e limpar valores numéricos dos textos  

---

## ⚙️ Como Executar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/pricefinder.git
   cd pricefinder

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**

    python -m venv .venv
    .venv\Scripts\activate  # no Windows
    source .venv/bin/activate  # no Linux/Mac


3. **Instale as dependências:**

    pip install -r requirements.txt


4. **Execute o script:**

    python main.py