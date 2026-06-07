# DocTools API

API desenvolvida em Python com Flask e Swagger para entregar ferramentas relacionadas a documentos.

Projeto criado por **zxkaren**.

## Funcionalidades

Neste momento, a API possui a funcionalidade:

- Compare: comparação de documentos PDF

A estrutura já está preparada para futuras comparações de:

- DOC
- DOCX
- XLSX
- PPT
- PPTX

Esses motores serão implementados nas próximas etapas.

## Tecnologias utilizadas

- Python
- Flask
- Flasgger
- PyMuPDF
- APScheduler
- python-decouple
- pytest

## Estrutura do projeto

```text
doctools-api/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── responses.py
│   │   ├── file_manager.py
│   │   └── validators.py
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   │
│   │   └── compare/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       ├── service.py
│   │       ├── validators.py
│   │       │
│   │       └── processors/
│   │           ├── __init__.py
│   │           ├── word_processor.py
│   │           ├── excel_processor.py
│   │           ├── pdf_processor.py
│   │           └── slides_processor.py
│   │
│   ├── jobs/
│   │   ├── __init__.py
│   │   └── cleanup_files.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── dates.py
│       ├── filenames.py
│       └── logs.py
│
├── storage/
│   └── compare/
│       ├── received/
│       │   └── .gitkeep
│       ├── processed/
│       │   └── .gitkeep
│       └── temp/
│           └── .gitkeep
│
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Como instalar

Clone o projeto:

```bash
git clone https://github.com/zxkaren/doctools-api.git
cd doctools-api
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Crie o arquivo `.env` com base no exemplo:

```bash
cp .env.example .env
```

Ajuste os valores do `.env` conforme seu ambiente local.

## Como executar

Execute a API:

```bash
python run.py
```

A aplicação será iniciada em:

```text
http://127.0.0.1:5000
```

A documentação Swagger estará disponível em:

```text
http://127.0.0.1:5000/docs/
```

## Rotas disponíveis

### Comparar documentos identificando a extensão automaticamente

```text
POST /compare/
```

Campos obrigatórios:

```text
original
modified
```

Campo opcional:

```text
response_mode
```

Valores permitidos para `response_mode`:

```text
download_url
json
json_file
```

### Comparar documentos escolhendo a extensão na rota

```text
POST /compare/{extension}
```

Extensões aceitas:

```text
pdf
doc
docx
xlsx
ppt
pptx
```

Neste momento, apenas `pdf` está implementado.

## Exemplo de resposta

```json
{
  "success": true,
  "message": "comparação concluída",
  "data": {
    "download_url": "/compare/download/arquivo-compared-07062026-153000.pdf",
    "summary_table": {
      "add": 10,
      "delete": 3,
      "total_changes": 13
    }
  }
}
```

## Regras da comparação PDF

A comparação de PDF:

- usa o arquivo modificado como base;
- destaca em azul palavras adicionadas;
- sublinha em vermelho pontos com exclusões;
- adiciona comentário lateral com o texto excluído;
- cria uma página final com a tabela de resumo.

A tabela de resumo contém:

```text
add
delete
total_changes
```

## Segurança

O arquivo `.env` não deve ser publicado no GitHub.

Arquivos enviados e processados também não devem ser versionados.

As pastas de storage são mantidas no repositório apenas por meio de arquivos `.gitkeep`.

## Limpeza de arquivos

A API possui uma rotina agendada para limpar arquivos antigos das pastas:

```text
storage/compare/received/
storage/compare/processed/
storage/compare/temp/
```

A rotina preserva os arquivos `.gitkeep`.

## Status do projeto

Implementado:

- Estrutura Flask
- Swagger
- Configuração via `.env`
- Upload de arquivos
- Comparação de PDF
- Geração de arquivo processado
- Retorno com `download_url`
- Retorno com `summary_table`
- Rotina de limpeza

Próximas implementações:

- Comparação de DOC
- Comparação de DOCX
- Comparação de XLSX
- Comparação de PPT
- Comparação de PPTX
- Testes automatizados