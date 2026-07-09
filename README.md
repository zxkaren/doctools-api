# DocTools API

A **DocTools API** é uma API desenvolvida em Python com Flask e Swagger para centralizar ferramentas de processamento, análise e tratamento de documentos.

O projeto foi estruturado de forma modular para permitir evolução contínua, mantendo separação clara entre rotas, serviços, processadores, validações, testes e documentação.

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

### Split PDF

Funcionalidade responsável por separar um arquivo PDF em páginas individuais ou em pacotes personalizados de páginas.

Pode ser usada, por exemplo, para dividir atas, contratos, relatórios, documentos digitalizados ou materiais extensos em arquivos menores, mantendo a ordem de páginas definida pelo usuário.

A funcionalidade aceita somente 1 PDF por requisição e pode gerar múltiplos PDFs como saída.

Extensão suportada:

- PDF

Tipos de split disponíveis:

- `one_by_one`: gera 1 PDF para cada página do documento.
- `pack`: gera PDFs personalizados com páginas ou intervalos definidos pelo usuário.

### Merge PDF

Funcionalidade responsável por unir múltiplos arquivos PDF em um único documento final.

Pode ser usada, por exemplo, para consolidar contratos, anexos, comprovantes, relatórios, atas ou documentos digitalizados que precisam ser entregues como um único arquivo.

A funcionalidade permite que os arquivos sejam unidos na ordem de upload ou em uma ordem personalizada enviada pelo usuário.

Extensão suportada:

- PDF

## Tecnologias utilizadas

- Python
- Flask
- Flasgger
- PyMuPDF
- python-docx
- openpyxl
- python-pptx
- APScheduler
- python-decouple
- pytest

## Como instalar

Clone o projeto:

```bash
git clone https://github.com/zxkaren/doctools-api.git
cd doctools-api
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
python -m venv .venv
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

### Compare

| Método | Rota | Descrição |
|---|---|---|
| POST | `/compare/` | Compara documentos identificando a extensão automaticamente. |
| POST | `/compare/{extension}` | Compara documentos usando a extensão informada na rota. |
| GET | `/compare/download/{processed_filename}` | Baixa o arquivo processado pelo Compare. |

Campos principais:

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `original` | Sim | Arquivo original. |
| `modified` | Sim | Arquivo modificado. |
| `response_mode` | Não | Define o formato de resposta. |

Valores permitidos para `response_mode`:

```text
download_url
json
json_file
```

Extensões aceitas:

```text
pdf
docx
xlsx
pptx
```

### Extração de Texto

| Método | Rota | Descrição |
|---|---|---|
| POST | `/extract-text/` | Extrai texto limpo de um ou mais documentos. |
| GET | `/extract-text/download/{processed_filename}` | Baixa o arquivo processado pela Extração de Texto. |

Campos principais:

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `files` | Sim | Um ou mais arquivos para extração de texto. |
| `output_format` | Não | Formato de saída. Valor padrão: `docx`. |

Valores permitidos para `output_format`:

```text
docx
txt
json
```

Regra de processamento:

```text
1 arquivo enviado = 1 arquivo de saída gerado
```

### Split PDF

| Método | Rota | Descrição |
|---|---|---|
| POST | `/split/pdf/` | Divide um PDF por páginas individuais ou pacotes personalizados. |
| GET | `/split/pdf/download/{processed_filename}` | Baixa um PDF gerado pelo Split PDF. |

Campos principais:

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `file` | Sim | PDF que será dividido. |
| `split_type` | Sim | Tipo de split: `one_by_one` ou `pack`. |
| `pack` | Condicional | Obrigatório quando `split_type=pack`. |
| `pages` | Condicional | Obrigatório quando `split_type=pack`. |

Exemplo para um único pack:

```text
pack: 1
pages: 1-3
```

Exemplo para múltiplos packs:

```text
pack: 1
pages: 1-3

pack: 2
pages: 4-10

pack: 3
pages: 11,12,15-18
```

Exemplo compatível com Swagger:

```text
pack: 1,2,3
pages: 1-3;4-10;11,12,15-18
```

### Merge PDF

| Método | Rota | Descrição |
|---|---|---|
| POST | `/merge/pdf/` | Une múltiplos arquivos PDF em um único documento. |
| GET | `/merge/pdf/download/{processed_filename}` | Baixa o PDF unificado. |

Campos principais:

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `file` | Sim | Arquivos PDF que serão unidos. Envie o campo `file` múltiplas vezes. |
| `order` | Não | Ordem personalizada dos arquivos. Aceita CSV ou campos repetidos no `form-data`. |

Exemplo usando ordem de upload:

```text
file: contrato.pdf
file: anexo.pdf
file: comprovante.pdf
```

Exemplo usando ordem personalizada:

```text
file: contrato.pdf
file: anexo.pdf
file: comprovante.pdf
order: 3,1,2
```

Nesse caso, o PDF final será gerado na seguinte ordem:

```text
1. comprovante.pdf
2. contrato.pdf
3. anexo.pdf
```

Observação: para upload de múltiplos arquivos no mesmo campo `file`, recomenda-se testar via Postman, frontend ou integração própria. O Swagger/Flasgger pode ter limitações visuais para esse tipo de envio.

## Regras de processamento

### Compare PDF

- usa o arquivo modificado como base;
- destaca em azul palavras adicionadas;
- sublinha em vermelho pontos com exclusões;
- adiciona comentário lateral com o texto excluído;
- cria uma página final com a tabela de resumo.

### Compare Word

- aceita arquivos `.docx`;
- usa o arquivo modificado como base;
- preserva o máximo possível da formatação;
- destaca conteúdos adicionados e removidos;
- cria uma página final com a tabela de resumo.

### Compare Excel

- aceita arquivos `.xlsx`;
- usa o arquivo modificado como base;
- preserva a formatação;
- destaca células adicionadas e removidas;
- adiciona comentários nas células alteradas;
- cria uma aba `summary_table`.

### Compare PowerPoint

- aceita arquivos `.pptx`;
- usa o arquivo modificado como base;
- preserva visualmente os slides existentes;
- compara slides por similaridade de conteúdo;
- registra alterações no campo de anotações;
- cria um slide final com a tabela de resumo.

### Extração de Texto

- aceita arquivos `.pdf`, `.docx` e `.pptx`;
- processa um ou mais arquivos na mesma requisição;
- gera uma saída individual para cada arquivo enviado;
- permite saída em `.docx`, `.txt` e `.json`;
- ignora imagens, ícones, gráficos, URLs, e-mails, emojis, números de página e legendas;
- retorna o status individual de cada arquivo processado.

### Split PDF

- aceita somente arquivos `.pdf`;
- aceita somente 1 PDF por requisição;
- permite separar página por página com `one_by_one`;
- permite gerar pacotes personalizados com `pack`;
- aceita páginas soltas e intervalos;
- valida páginas inexistentes, repetidas ou duplicadas entre packs;
- retorna uma URL de download para cada PDF gerado.

### Merge PDF

- aceita somente arquivos `.pdf`;
- exige no mínimo 2 PDFs por requisição;
- une os arquivos na ordem de upload quando `order` não é informado;
- une os arquivos na ordem personalizada quando `order` é informado;
- valida ordem incompleta, posições inexistentes e posições repetidas;
- gera um único PDF final;
- retorna uma URL para download do arquivo unificado.

## Tabela de resumo

As funcionalidades de comparação retornam uma tabela de resumo contendo:

```text
add
delete
total_changes
```

## Limpeza de arquivos

A API possui rotina agendada para limpar arquivos antigos das pastas de storage das funcionalidades:

```text
compare
extract_text
split_pdf
merge_pdf
```

A rotina preserva os arquivos `.gitkeep`.

## Segurança

O arquivo `.env` não deve ser publicado no GitHub.

Arquivos enviados e processados também não devem ser versionados.

As pastas de storage são mantidas no repositório apenas por meio de arquivos `.gitkeep`.

## Testes

Execute a suíte de testes com:

```bash
pytest -v
```

Execução validada na versão atual:

```text
30 passed
```

## Versão atual

```text
1.6.0
```