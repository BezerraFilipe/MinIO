Com certeza\! Transformarei as orientações fornecidas em um documento README completo e bem estruturado para o seu projeto FastAPI com MinIO S3 usando Docker Compose.

-----

# 🚀 FastAPI com MinIO S3 e Docker Compose

Este projeto demonstra como configurar e executar uma aplicação **FastAPI** que interage com um serviço **MinIO S3** local, tudo orquestrado via **Docker Compose**.

-----

## 📂 Estrutura do Projeto

A organização dos arquivos é fundamental para a clareza e manutenção do projeto. Siga a estrutura abaixo:

```
.
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── minio_data/  (diretório para persistir os dados do MinIO)
```

-----

## 🛠️ Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas em seu sistema:

  * **Docker Desktop** (inclui Docker Engine e Docker Compose)

-----

## 📦 Componentes do Projeto

### 1\. Aplicação FastAPI (`api/main.py`)

Este é o coração da sua API, desenvolvida com **FastAPI**. Ele inclui rotas para:

  * Verificar o status (`/`)
  * Fazer upload de arquivos para o MinIO (`/uploadfile/`)
  * Listar objetos em um bucket do MinIO (`/list_objects/`)
  * Baixar arquivos do MinIO (`/download_file/{object_name}`)

A aplicação se conecta ao MinIO usando a biblioteca `minio` para Python.

### 2\. `Dockerfile` da Aplicação FastAPI (`api/Dockerfile`)

Este Dockerfile define como a imagem Docker da sua aplicação FastAPI será construída. Ele:

  * Usa uma imagem **Python 3.9-slim-buster** como base.
  * Define o diretório de trabalho (`/app`).
  * Instala as dependências listadas em `requirements.txt`.
  * Copia o código da aplicação.
  * Expõe a porta `8000`.
  * Define o comando de inicialização usando **Uvicorn**.

<!-- end list -->

```dockerfile
# Usa uma imagem oficial do Python como base
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da sua aplicação
COPY . .

# Expõe a porta que a aplicação FastAPI irá rodar
EXPOSE 8000

# Comando para iniciar a aplicação FastAPI com Uvicorn
# O host 0.0.0.0 é necessário para que a aplicação seja acessível de fora do contêiner
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3\. Dependências Python (`api/requirements.txt`)

Lista as bibliotecas Python necessárias para a sua API:

```
fastapi
uvicorn[standard]
minio
python-dotenv # Opcional, para carregar variáveis de ambiente localmente
```

### 4\. Orquestração com Docker Compose (`docker-compose.yml`)

Este arquivo é o blueprint para orquestrar os serviços MinIO e FastAPI. Ele:

  * Define o serviço **MinIO** usando a imagem oficial, mapeando portas (`9000` para API, `9001` para console) e configurando variáveis de ambiente (credenciais `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`).
  * Configura um **volume persistente** (`./minio_data:/data`) para o MinIO, garantindo que seus dados não sejam perdidos ao reiniciar os contêineres.
  * Inclui um **healthcheck** para o MinIO, assegurando que ele esteja pronto antes que a API tente se conectar.
  * Define o serviço **FastAPI**, construindo-o a partir do Dockerfile local (`./api`).
  * Mapeia a porta `8000` da API para o host.
  * Configura variáveis de ambiente (`MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, etc.) para que a API possa se conectar ao MinIO. Note que o `MINIO_ENDPOINT` usa o nome do serviço MinIO (`minio:9000`), que é resolvido automaticamente pelo Docker Compose.
  * Utiliza `depends_on: minio: condition: service_healthy` para garantir que a API só inicie após o MinIO estar operacional.
  * Monta o código da sua API (`./api:/app`) para facilitar o desenvolvimento (hot-reloading).

<!-- end list -->

```yaml
version: '3.8'

services:
  # Serviço MinIO
  minio:
    image: minio/minio:latest # Usa a imagem oficial mais recente do MinIO
    ports:
      - "9000:9000" # Porta da API MinIO
      - "9001:9001" # Porta do Console MinIO
    environment:
      # Credenciais de acesso para o MinIO
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
      # Comando para iniciar o MinIO
    command: server /data --console-address ":9001"
    volumes:
      # Monta um volume para persistir os dados do MinIO
      - ./minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # Serviço da Aplicação FastAPI
  api:
    build: ./api # Constrói a imagem a partir do Dockerfile no diretório 'api'
    ports:
      - "8000:8000" # Mapeia a porta 8000 do contêiner para a porta 8000 do host
    environment:
      # Variáveis de ambiente para a API FastAPI se conectar ao MinIO
      # O hostname 'minio' é resolvível automaticamente pelo Docker Compose
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
      MINIO_BUCKET: mybucket
      MINIO_SECURE: "False" # Use "True" se o MinIO estiver configurado para HTTPS
    depends_on:
      # Garante que o MinIO esteja pronto antes de iniciar a API
      minio:
        condition: service_healthy
    volumes:
      # Monta o código da sua API para facilitar o desenvolvimento (hot-reloading)
      - ./api:/app
```

-----

## ▶️ Como Rodar o Projeto

Siga estes passos para colocar sua aplicação no ar:

1.  **Clone o repositório** (se aplicável) ou crie a estrutura de arquivos conforme a seção "Estrutura do Projeto".

2.  **Navegue até o diretório raiz** do projeto onde o `docker-compose.yml` está localizado:

    ```bash
    cd seu-projeto-fastapi-minio
    ```

3.  **Inicie os serviços** usando Docker Compose. O comando `--build` garantirá que as imagens sejam construídas (ou reconstruídas) com as configurações mais recentes.

    ```bash
    docker compose up --build
    ```

    Isso construirá a imagem da sua API, fará o download da imagem do MinIO e iniciará ambos os serviços, garantindo a ordem de inicialização correta.

-----

## 🌐 Acessando a Aplicação e o Console MinIO

Uma vez que os contêineres estejam em execução:

  * **API FastAPI:**

      * **Endpoint Principal:** `http://localhost:8000`
      * **Documentação Interativa (Swagger UI):** `http://localhost:8000/docs`
      * 
  * **Console MinIO:**

      * **URL:** `http://localhost:9001`
      * **Usuário:** `minioadmin`
      * **Senha:** `minioadmin`
      * 
Você pode usar o console do MinIO para visualizar os buckets e objetos armazenados, além de testar as operações de upload e download via sua API.

-----

## 🛑 Parando os Serviços

Para parar e remover os contêineres, redes e volumes criados pelo Docker Compose (os dados persistidos em `minio_data/` não serão removidos):

```bash
docker compose down
```

Para remover os volumes persistentes também (o que apagará seus dados do MinIO):

```bash
docker compose down --volumes
```

-----

## 🔧 Personalização

  * **Credenciais MinIO:** Modifique as variáveis `MINIO_ROOT_USER` e `MINIO_ROOT_PASSWORD` no `docker-compose.yml` e as variáveis de ambiente correspondentes na seção `api` para alterar as credenciais.
  * **Nome do Bucket:** Altere `MINIO_BUCKET` no `docker-compose.yml` e em `api/main.py` para usar um nome de bucket diferente.
  * **Portas:** Ajuste os mapeamentos de portas em `ports:` no `docker-compose.yml` se as portas padrão (`8000`, `9000`, `9001`) estiverem em conflito ou se você desejar usar portas diferentes.

-----

Sinta-se à vontade para explorar e estender esta base para suas necessidades específicas\! Se tiver alguma dúvida, abra uma issue ou entre em contato.