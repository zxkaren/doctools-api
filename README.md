# DocTools API

A DocTools API é uma API desenvolvida em Python com Flask e Swagger para centralizar ferramentas de processamento, análise e tratamento de documentos.

O projeto foi estruturado de forma modular para permitir a evolução contínua de novas funcionalidades documentais, mantendo separação clara entre recursos, rotas, processamentos, validações, testes e documentação.

## Funcionalidades

### Compare

Funcionalidade responsável pela comparação de documentos, permitindo identificar diferenças entre arquivos de uma mesma extensão.

Pode ser usada, por exemplo, para comparar contratos, propostas, atas, versões revisadas de documentos ou arquivos técnicos, ajudando a identificar o que foi adicionado, removido ou alterado entre duas versões.

Extensões suportadas:

- PDF
- DOCX
- XLSX
- PPTX

### Extração de Texto

Funcionalidade responsável por extrair somente o conteúdo textual de documentos, ignorando elementos que não fazem parte da leitura principal, como imagens, ícones, emojis, URLs, e-mails, números de página e legendas de figuras.

Pode ser usada, por exemplo, para limpar textos de papers, contratos, apresentações, atas, resumos, notas de imprensa e materiais técnicos. Esse conteúdo extraído pode ser reaproveitado para revisão textual, reescrita, análise, indexação ou integração futura com aplicações de leitura em voz alta, como uma `voice-reader-api`, oferecendo uma experiência próxima de audiolivro ou podcast.

Extensões suportadas:

- PDF
- DOCX
- PPTX

Formatos de saída:

- DOCX
- TXT
- JSON

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
│   │   ├── compare/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── validators.py
│   │   │   │
│   │   │   └── processors/
│   │   │       ├── __init__.py
│   │   │       ├── pdf_processor.py
│   │   │       ├── word_processor.py
│   │   │       ├── excel_processor.py
│   │   │       └── slides_processor.py
│   │   │
│   │   └── extract_text/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       ├── service.py
│   │       ├── validators.py
│   │       │
│   │       └── processors/
│   │           ├── __init__.py
│   │           ├── pdf_processor.py
│   │           ├── word_processor.py
│   │           ├── slides_processor.py
│   │           └── text_cleaner.py
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
│   ├── compare/
│   │   ├── received/
│   │   │   └── .gitkeep
│   │   ├── processed/
│   │   │   └── .gitkeep
│   │   └── temp/
│   │       └── .gitkeep
│   │
│   └── extract_text/
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
│   ├── test_compare.py
│   └── test_extract_text.py
│
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── run.py
└── VERSION

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

A DocTools API organiza suas rotas por funcionalidade. Cada grupo de rota pertence a uma feature específica do projeto.

---

## Compare

Funcionalidade responsável por comparar documentos de uma mesma extensão e identificar diferenças entre eles.

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
pptx
```

### Baixar arquivo processado pelo Compare

```text
GET /compare/download/{processed_filename}
```

Essa rota é usada para baixar arquivos processados quando a resposta da comparação retorna um `download_url`.

---

## Extração de Texto

Funcionalidade responsável por extrair apenas o conteúdo textual principal de documentos, removendo elementos que não fazem parte da leitura útil.

### Extrair texto de documentos

```text
POST /extract-text/
```

Campo obrigatório:

```text
files
```

O campo `files` aceita um ou mais arquivos na mesma requisição.

Campo opcional:

```text
output_format
```

Valores permitidos para `output_format`:

```text
docx
txt
json
```

Valor padrão:

```text
docx
```

Extensões aceitas:

```text
pdf
docx
pptx
```

Regra de processamento:

```text
1 arquivo enviado = 1 arquivo de saída gerado
```

Exemplo:

```text
3 arquivos enviados = 3 arquivos processados individualmente
```

### Baixar arquivo processado pela Extração de Texto

```text
GET /extract-text/download/{processed_filename}
```

Essa rota é usada para baixar arquivos processados quando a resposta da extração retorna um `download_url`.

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

## Regras da comparação PowerPoint

A comparação de PowerPoint:

* aceita arquivos no formato `.pptx`;
* usa o arquivo modificado como base;
* preserva visualmente os slides existentes;
* não altera textos, imagens, fontes, caixas, posições ou layout dos slides originais/modificados;
* compara os slides por similaridade de conteúdo, não apenas pela posição;
* registra as alterações identificadas no campo de anotações do respectivo slide;
* registra alterações textuais no formato `add: conteúdo incluído` e `delete: conteúdo removido`;
* registra imagens adicionadas como `add: imagem adicionada`;
* registra imagens removidas como `delete: imagem removida`;
* registra slides adicionados nas anotações do próprio slide adicionado;
* registra slides removidos nas anotações do slide final de resumo;
* contabiliza alterações por evento identificado, não por quantidade de palavras;
* cria um slide final com a tabela de resumo.

## Tabela de resumo

A tabela de resumo contém:

```text
add
delete
total_changes
```
## Regras da Extração de Texto

A extração de texto:

* aceita arquivos nos formatos `.pdf`, `.docx` e `.pptx`;
* processa um ou mais arquivos na mesma requisição;
* respeita a regra `1 arquivo enviado = 1 arquivo de saída gerado`;
* permite saída nos formatos `.docx`, `.txt` e `.json`;
* usa `.docx` como formato padrão quando `output_format` não é informado;
* extrai apenas o conteúdo textual principal do documento;
* ignora imagens, ícones, gráficos e objetos visuais;
* ignora URLs, e-mails, emojis, números de página e legendas de imagens;
* ignora cabeçalhos, rodapés e notas quando não fazem parte do corpo principal extraído;
* preserva acentuação, pontuação e quebras úteis para leitura;
* mantém o processamento dos demais arquivos quando algum arquivo falha;
* retorna o status individual de cada arquivo processado.

## Formatos de saída

A extração de texto pode gerar arquivos nos formatos:

```text
docx
txt
json
```

## Estrutura da resposta

A resposta da extração informa:

```text
output_format
total_files
processed_files
failed_files
files
```

Cada item de `files` representa o resultado individual de um arquivo enviado.

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