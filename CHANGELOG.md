# Changelog

Todas as mudanças relevantes deste projeto serão documentadas aqui.

O formato segue uma estrutura simples baseada em versionamento semântico.

## [1.4.0] - 2026-07-05

### Added
- Added text extraction feature through the new `/extract-text/` endpoint.
- Added support for extracting clean text from PDF, DOCX and PPTX files.
- Added support for individual output generation following the rule: one input file generates one output file.
- Added output formats for extracted text: DOCX, TXT and JSON.
- Added text cleaning rules to remove URLs, emails, emojis, page numbers and image captions.
- Added recursive extraction for nested DOCX tables and grouped PPTX shapes.
- Added automated tests for text extraction, default output format, invalid extensions, invalid output formats and text cleaning rules.

### Changed
- Updated Swagger configuration to include the new text extraction feature.
- Updated Swagger version loading to read the project version from the `VERSION` file.
- Updated cleanup routine to include `storage/extract_text` folders.

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