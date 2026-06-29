# DocTools API

API desenvolvida em Python com Flask e Swagger para entregar ferramentas relacionadas a documentos.

Projeto criado por **zxkaren**.

## Funcionalidades

Neste momento, a API possui a funcionalidade:

* Compare: comparação de documentos PDF, Word e Excel.

Extensões implementadas:

* PDF
* DOCX
* XLSX

A estrutura está preparada para futura comparação de:

* PPTX

Arquivos binários legados não serão tratados nesta API:

* DOC
* XLS
* PPT

Esses formatos pertencem a padrões antigos/binários e ficam fora do escopo do projeto.

## Tecnologias utilizadas

* Python
* Flask
* Flasgger
* PyMuPDF
* python-docx
* openpyxl
* APScheduler
* python-decouple
* pytest

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
│   │           ├── pdf_processor.py
│   │           ├── word_processor.py
│   │           ├── excel_processor.py
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
├── tests/
│   ├── __init__.py
│   ├── test_cleanup_files.py
│   └── test_compare.py
│
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── run.py
└── VERSION
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

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Crie o arquivo `.env` com base no exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
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
docx
xlsx
pptx
```

Extensões implementadas neste momento:

```text
pdf
docx
xlsx
```

Extensão planejada para próxima implementação:

```text
pptx
```

## Modos de resposta

### download_url

Retorna apenas o link para download do arquivo processado.

### json

Retorna apenas a tabela de resumo da comparação.

### json_file

Retorna o link para download do arquivo processado e a tabela de resumo da comparação.

## Exemplo de resposta

```json
{
  "success": true,
  "message": "comparação concluída",
  "data": {
    "download_url": "/compare/download/arquivo-compared-28062026-153000.xlsx",
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

* usa o arquivo modificado como base;
* destaca em azul palavras adicionadas;
* sublinha em vermelho pontos com exclusões;
* adiciona comentário lateral com o texto excluído;
* cria uma página final com a tabela de resumo.

## Regras da comparação Word

A comparação de Word:

* aceita arquivos no formato `.docx`;
* usa o arquivo modificado como base;
* preserva o máximo possível da formatação do arquivo modificado;
* destaca em azul e sublinhado conteúdos adicionados;
* destaca em vermelho e tachado conteúdos removidos;
* cria uma página final com a tabela de resumo.

## Regras da comparação Excel

A comparação de Excel:

* aceita arquivos no formato `.xlsx`;
* usa o arquivo modificado como base;
* preserva a formatação do arquivo modificado;
* destaca células adicionadas com fundo azul claro;
* destaca células removidas com fundo vermelho claro;
* adiciona comentários nas células alteradas com os prefixos `add:` e `delete:`;
* cria uma aba `summary_table` com a tabela de resumo.

## Tabela de resumo

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

* Estrutura Flask
* Swagger
* Configuração via `.env`
* Upload de arquivos
* Comparação de PDF
* Comparação de DOCX
* Comparação de XLSX
* Geração de arquivo processado
* Retorno com `download_url`
* Retorno com `summary_table`
* Rotina de limpeza
* Testes automatizados para Compare

Próximas implementações:

* Comparação de PPTX

Fora do escopo:

* Comparação de DOC
* Comparação de XLS
* Comparação de PPT