# Changelog

Todas as mudanças relevantes deste projeto serão documentadas aqui.

O formato segue uma estrutura simples baseada em versionamento semântico.

## [1.0.0] - 2026-06-07

### Adicionado

- Estrutura inicial da DocTools API com Flask.
- Documentação Swagger com Flasgger.
- Configuração por variáveis de ambiente usando python-decouple.
- Funcionalidade Compare para documentos PDF.
- Upload de arquivo original e arquivo modificado.
- Motor PDF com comparação por palavras.
- Highlight azul para palavras adicionadas.
- Sublinhado vermelho para indicar exclusões.
- Comentário de exclusão em anotação PDF.
- Summary table com add, delete e total changes.
- Retorno por download_url, json ou json_file.
- Rotina de limpeza de arquivos antigos.
- Preservação dos arquivos .gitkeep.
- Testes automatizados com pytest.
- README com instruções de instalação e uso.