# Dockerfile

# Use uma imagem oficial do Python como uma base
FROM python:3.9-slim

# Defina a variável de ambiente
ENV PYTHONUNBUFFERED 1

# Crie um diretório para o código da aplicação
RUN mkdir /code
WORKDIR /code

# Instale as dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie o arquivo requirements.txt
COPY requirements.txt /code/

# Instale as dependências do Python
RUN pip install -r requirements.txt

# Copie o código da aplicação para o contêiner
COPY . /code/

# Exponha a porta que o servidor vai rodar
EXPOSE 8000

# Comando para rodar a aplicação com Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "your_project_name.asgi:application"]
