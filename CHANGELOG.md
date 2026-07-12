# Changelog

Todas as mudanças relevantes deste projeto serão documentadas aqui.

O formato segue uma estrutura simples baseada em versionamento semântico.

## [1.7.1] - 2026-07-12

### Fixed

- Adicionada ao repositório a estrutura de storage da funcionalidade OCR PDF com as pastas `received`, `processed` e `temp`.
- Incluída a funcionalidade OCR PDF na rotina automática de exclusão de arquivos expirados.
- Corrigido o scheduler para executar a limpeza geral de todas as funcionalidades, em vez de limpar somente os arquivos da funcionalidade Compare.
- Corrigida a inicialização da aplicação para garantir a criação das pastas de storage de Compare, Extract Text, Split PDF, Merge PDF e OCR PDF.

### Changed

- Ampliados os testes automatizados da rotina de limpeza para contemplar Compare, Extract Text, Split PDF, Merge PDF e OCR PDF.
- Adicionado teste da função centralizadora `cleanup_all_feature_files`.

### Validation

- Suíte específica da rotina de limpeza executada com sucesso: `6 passed`.
- Suíte automatizada completa executada com sucesso: `50 passed`.

## [1.7.0] - 2026-07-11

### Added

- Implementada funcionalidade de OCR PDF.
- Adicionado endpoint `POST /ocr/pdf/` para aplicar OCR em um ou mais arquivos PDF.
- Adicionada rota `GET /ocr/pdf/download/{processed_filename}` para download dos PDFs processados com OCR.
- Adicionado suporte ao processamento de múltiplos documentos PDF na mesma requisição.
- Adicionado suporte aos modos de OCR `apply` e `force`.
- Adicionado suporte aos idiomas `pt_br`, `pt_pt`, `en_us` e `es_es`, mapeados para os idiomas disponíveis no Tesseract.
- Adicionado suporte aos perfis de qualidade `standard`, `enhanced`, `aggressive` e `ebook`.
- Adicionado perfil `ebook` para apostilas, e-books e materiais de estudo com layout visual.
- Criado storage isolado para `ocr_pdf` com pastas `received`, `processed` e `temp`.
- Criados testes automatizados para validação de arquivos PDF, modos de OCR, idiomas, perfis de qualidade e montagem dos comandos do OCRmyPDF.

### Changed

- Docker atualizado para incluir suporte a OCR com `ocrmypdf`, `tesseract`, `ghostscript`, `qpdf` e `unpaper`.
- Incluídos pacotes de idioma do Tesseract para português, inglês e espanhol.
- Registrado blueprint da feature `ocr_pdf` na aplicação Flask.
- Atualizada configuração `.env.example` com as variáveis da feature `ocr_pdf`.
- Atualizado Swagger para documentar a nova funcionalidade OCR PDF.
- Ajustado perfil `aggressive` para evitar rotação automática indevida e remover opção incompatível `--remove-background`.
- Adicionado limite `--max-image-mpixels 1000` para suportar PDFs com imagens grandes durante o OCR.

### Validation

- Teste manual realizado via Postman com PDF de apostila contendo imagens, blocos coloridos e texto em layout visual.
- Validação manual dos perfis `standard`, `enhanced`, `aggressive` e `ebook`.
- Perfil `ebook` validado como melhor opção para apostilas e materiais de estudo com layout visual.
- Suíte automatizada executada com sucesso: `45 passed`.

## [1.6.0] - 2026-07-09

### Added

- Implementada funcionalidade de Merge PDF.
- Adicionado endpoint `POST /merge/pdf/` para unir múltiplos arquivos PDF em um único documento.
- Adicionada rota `GET /merge/pdf/download/{processed_filename}` para download do PDF unificado.
- Adicionado suporte à ordenação personalizada dos arquivos via campo `order`.
- Adicionado suporte a ordenação por CSV, como `3,1,2`.
- Adicionado suporte a ordenação por campos repetidos no `form-data`.
- Criado storage isolado para `merge_pdf` com pastas `received`, `processed` e `temp`.
- Criados testes automatizados para validação do fluxo de merge, download, ordenação e erros de entrada.
- Incluída limpeza automática dos arquivos da feature `merge_pdf`.

### Changed

- Atualizado limite máximo de requisição para `300 MB` via `MAX_CONTENT_LENGTH=314572800`.
- Registrado blueprint da feature `merge_pdf` na aplicação Flask.
- Atualizada configuração `.env.example` com as variáveis da feature `merge_pdf`.

### Validation

- Teste manual realizado via Postman com múltiplos PDFs.
- Suíte automatizada executada com sucesso: `30 passed`.

## [1.5.0] - 2026-07-06

### Adicionado
- Funcionalidade Split PDF por meio do novo endpoint `/split/pdf/`.
- Suporte para separar um PDF em páginas individuais usando `one_by_one`.
- Suporte para separar um PDF em pacotes personalizados de páginas usando `pack`.
- Suporte para intervalos de páginas nos packs, como `1-3` e `4-10`.
- Suporte para campos `pack` e `pages` repetidos em `form-data`, facilitando integrações com frontend e Postman.
- Suporte no Swagger para informar múltiplos packs usando packs separados por vírgula e grupos de páginas separados por ponto e vírgula.
- Geração de URLs de download para cada PDF criado.
- Pastas isoladas para armazenamento dos arquivos da funcionalidade Split PDF em `storage/split_pdf`.
- Testes automatizados para split página por página, split por pack, intervalos de páginas, campos repetidos, formato compatível com Swagger, download e erros de validação.

### Alterado
- Configuração do Swagger atualizada para incluir a nova funcionalidade Split PDF.
- Rotina de limpeza atualizada para contemplar as pastas de `storage/split_pdf`.
- Versão do projeto atualizada para `1.5.0`.

## [1.4.0] - 2026-07-05

### Adicionado
- Funcionalidade de extração de texto por meio do novo endpoint `/extract-text/`.
- Suporte para extração de texto limpo de arquivos PDF, DOCX e PPTX.
- Suporte para geração individual de saída seguindo a regra: um arquivo de entrada gera um arquivo de saída.
- Suporte aos formatos de saída para texto extraído: DOCX, TXT e JSON.
- Regras de limpeza textual para remover URLs, e-mails, emojis, números de página e legendas de imagens.
- Extração recursiva para tabelas aninhadas em DOCX e formas agrupadas em PPTX.
- Testes automatizados para extração de texto, formato padrão de saída, extensões inválidas, formatos de saída inválidos e regras de limpeza textual.

### Alterado
- Configuração do Swagger atualizada para incluir a nova funcionalidade de extração de texto.
- Carregamento da versão no Swagger atualizado para ler a versão do projeto a partir do arquivo `VERSION`.
- Rotina de limpeza atualizada para contemplar as pastas de `storage/extract_text`.

## [1.3.0] - 2026-07-05

### Added
- Implementado suporte à comparação de arquivos PowerPoint no formato `.pptx`.
- Adicionada geração de anotações por slide com alterações identificadas em textos, imagens e slides.
- Adicionada tabela de resumo final para comparações PPTX com `add`, `delete` e `total_changes`.
- Adicionado teste automatizado para comparação de arquivos PPTX.

### Changed
- Atualizada documentação do Compare para incluir suporte a PowerPoint.
- Atualizado Swagger para listar `.pptx` como extensão implementada.
- Atualizada configuração de extensões implementadas para incluir `.pptx`.

### Notes
- Arquivos `.ppt` continuam fora do escopo por serem formato binário legado.
- A comparação PPTX preserva visualmente os slides existentes e registra diferenças no campo de anotações.

## [1.2.0] - 2026-06-28

### Adicionado

* Funcionalidade Compare para documentos Excel no formato `.xlsx`.
* Motor de comparação Excel com marcação visual de alterações por célula.
* Destaque azul claro para células adicionadas.
* Destaque vermelho claro para células removidas.
* Comentários em células alteradas com prefixos `add:` e `delete:`.
* Geração de aba `summary_table` com total de adições, exclusões e alterações.
* Suporte ao download do arquivo Excel processado.
* Testes automatizados para comparação de documentos Excel.

### Alterado

* Fluxo da funcionalidade Compare atualizado para rotear arquivos `.xlsx`.
* Arquivo `.env.example` atualizado para indicar suporte implementado a `xlsx`.
* Testes da funcionalidade Compare atualizados para contemplar arquivos Excel.

## [1.1.0] - 2026-06-28

### Adicionado

* Funcionalidade Compare para documentos Word no formato `.docx`.
* Motor de comparação Word com marcação visual de alterações.
* Destaque azul e sublinhado para conteúdos adicionados em documentos Word.
* Destaque vermelho e tachado para conteúdos removidos em documentos Word.
* Geração de tabela de resumo com total de adições, exclusões e alterações em documentos Word.
* Suporte ao download do arquivo Word processado.
* Testes automatizados para comparação de documentos Word.

### Alterado

* Fluxo da funcionalidade Compare atualizado para rotear o processamento conforme a extensão do arquivo.
* Serviço de comparação atualizado para suportar múltiplos processadores de documentos.
* Validação de extensões atualizada para contemplar arquivos `.docx`.

## [1.0.0] - 2026-06-07

### Adicionado

* Estrutura inicial da DocTools API com Flask.
* Documentação Swagger com Flasgger.
* Configuração por variáveis de ambiente usando python-decouple.
* Funcionalidade Compare para documentos PDF.
* Upload de arquivo original e arquivo modificado.
* Motor PDF com comparação por palavras.
* Highlight azul para palavras adicionadas.
* Sublinhado vermelho para indicar exclusões.
* Comentário de exclusão em anotação PDF.
* Summary table com add, delete e total changes.
* Retorno por download_url, json ou json_file.
* Rotina de limpeza de arquivos antigos.
* Preservação dos arquivos .gitkeep.
* Testes automatizados com pytest.
* README com instruções de instalação e uso.