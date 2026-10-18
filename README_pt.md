<div align="center">

# Spawn

**Uma IDE leve para desenvolvimento em Pawn**

Desenvolva e gerencie servidores **open.mp** e **SA-MP** com integração ao SAMPCTL, Git, gerenciamento de dependências e um editor Pawn dedicado.

[![Plataformas](https://img.shields.io/badge/plataformas-Windows%20%7C%20Linux-blue)](https://github.com/daniilkorochansky/spawn)
[![Python](https://img.shields.io/badge/linguagem-Python-yellow.svg)](https://www.python.org/)
[![Testes](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml/badge.svg)](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml)
[![Build](https://github.com/daniilkorochansky/spawn/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/daniilkorochansky/spawn/actions/workflows/build.yml)
![Status](https://img.shields.io/badge/status-ativo-success.svg)

[Baixar Spawn](https://github.com/daniilkorochansky/spawn/releases) · [Relatar um problema](https://github.com/daniilkorochansky/spawn/issues) · [Contribuir](#contribuição)

[English](README.md) · [Русский](README_ru.md) · [Português](README_pt.md)

<img width="900" alt="Visão geral do Spawn IDE" src="https://github.com/user-attachments/assets/505d6a46-33cc-45ae-bed3-f011474a4dc7" />

</div>

## Por que escolher o Spawn?

O Spawn reúne as ferramentas essenciais para desenvolvimento de servidores Pawn em uma IDE desktop leve e portátil.

- **Editor Pawn** — realce de sintaxe, correspondência de chaves, marcadores de linhas alteradas e edição dividida.
- **Integração com SAMPCTL** — crie, compile e execute projetos de servidor.
- **Gerenciador de dependências** — instale, atualize e verifique dependências do projeto.
- **Integração com Git** — status do repositório, histórico de commits e ferramentas de controle de versão.
- **Ferramentas para o código** — pré-visualização de cores RGBA/HEX e seletor de cores para inserir valores no código.
- **Navegação pelo projeto** — árvore de arquivos projetada para projetos grandes.
- **Saída integrada** — acompanhe a compilação e o console do servidor dentro da IDE.
- **Suporte a codificações** — detecção automática e configurações de codificação para arquivos Pawn.
- **Portabilidade** — use o Spawn sem uma instalação tradicional.

## Instalação

1. Acesse a [versão mais recente](https://github.com/daniilkorochansky/spawn/releases).
2. Baixe e extraia o arquivo.
3. Execute `Spawn.exe`.

Para usar todos os recursos, instale também o [Git](https://git-scm.com/downloads) e o [SAMPCTL](https://github.com/Southclaws/sampctl). Ambos podem ser configurados posteriormente nas configurações do Spawn.

## Introdução rápida

### Criar um projeto

1. Selecione **File → New Project…**.
2. Informe o nome do projeto e escolha o local.
3. Clique em **Create** e siga as instruções na janela de linha de comando do SAMPCTL.
4. Quando a criação terminar, feche a janela de comando. O Spawn detectará o novo projeto.

### Compilar e executar um servidor

1. Selecione **File → Open Server Folder…** e escolha a pasta do servidor que contém o arquivo `pawn.json` gerado pelo SAMPCTL.
2. Selecione **Build → Build Server**.
3. Use **Server → Run / Stop Server** para iniciar ou parar o servidor.
4. Acompanhe a saída no console integrado.

### Gerenciar dependências

Abra **Project → Dependency Manager…**, informe o nome do pacote e clique em **Install**. Para remover uma dependência, selecione-a e clique em **Uninstall**. Use **Ensure** para verificar as dependências.

### Usar Git

Clique com o botão direito na pasta raiz do projeto e selecione **Initialize Repository** se ela ainda não for um repositório Git. Depois, crie commits e acompanhe as alterações no Spawn. Repositórios existentes são detectados quando a integração com Git está ativada nas configurações.

### Editar arquivos individuais

Também é possível abrir arquivos por **File → Open File…** sem abrir um projeto. Recursos como realce de sintaxe, pré-visualização de cores, correspondência de chaves, edição dividida e marcadores de alterações continuam disponíveis. As ferramentas específicas do projeto — árvore do projeto, Git, gerenciador de dependências e SAMPCTL — exigem um projeto aberto.

## Codificação de arquivos Pawn

O Spawn detecta a codificação dos arquivos ao abri-los. Nos arquivos `.pwn` e `.inc`, é possível indicar explicitamente a codificação no início do arquivo:

```pawn
// -*- coding: cp1251 -*-
```

Se o arquivo for exibido incorretamente, abra-o novamente com outra codificação em **Edit → Encoding → Reopen**. Isso altera apenas a forma como o arquivo é exibido no editor; o arquivo no disco não é modificado.

As codificações compatíveis incluem UTF-8 e as páginas de código Windows 1250–1257. Nas configurações, você pode escolher a codificação padrão dos novos arquivos Pawn. O Spawn pode inserir automaticamente a diretiva correspondente.

## Capturas de tela

<details>
<summary>Ver capturas de tela dos recursos</summary>

### Criação de projeto
<img width="900" alt="Criação de projeto" src="https://github.com/user-attachments/assets/14b70c29-96b4-4d7d-94ff-6307cfa35cac" />

### Editor dividido
<img width="900" alt="Editor de código dividido" src="https://github.com/user-attachments/assets/f0caa6e9-607b-48f1-8b58-ae95ef12f7b1" />

### Pré-visualização de cores RGBA/HEX
<img width="900" alt="Pré-visualização de cores" src="https://github.com/user-attachments/assets/ae6a367a-3b04-4a23-a6ad-71ae51b0edc8" />

### Gerenciador de dependências
<img width="900" alt="Gerenciador de dependências" src="https://github.com/user-attachments/assets/e60a1bad-9a9d-43da-938d-fa94d43401b7" />

### Git e controle de versão
<img width="900" alt="Git e controle de versão" src="https://github.com/user-attachments/assets/b6198ac3-97b4-4392-b29a-87ab6bdfc818" />

### Árvore do projeto
<img width="900" alt="Árvore do projeto" src="https://github.com/user-attachments/assets/c942516b-6e18-406d-b9be-cb8e24d54a94" />

</details>

## Contribuição

São bem-vindos relatos de bugs, sugestões de recursos, ideias de UI/UX, contribuições de código, testes e feedback.

Para relatar um problema pelo Spawn:

1. Selecione **Help → Bug Report**.
2. Copie o relatório gerado. Se **Log Output** estiver vazio, descreva o problema manualmente.
3. Selecione **Open GitHub Issue** e cole o relatório na descrição do problema.

Você também pode [abrir uma issue no GitHub](https://github.com/daniilkorochansky/spawn/issues).

## Apoie o desenvolvimento

O Spawn é gratuito e de código aberto. Se quiser apoiar seu desenvolvimento, você pode contribuir por meio de:

- [Ko-fi](https://ko-fi.com/Y4L421BNPH)
- [Boosty (Rússia / internacional)](https://boosty.to/daniilkorochansky)

## Licença

O Spawn é distribuído sob a licença **GNU General Public License v3.0**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<details>
<summary>Configuração para desenvolvimento</summary>

### Requisitos

- Python 3.13+
- wxPython
- GitPython
- Markdown
- watchdog
- platformdirs
- requests

### Clonar e executar

```bash
git clone https://github.com/daniilkorochansky/spawn.git
cd spawn
pip install -r requirements.txt
python main.py
```

### Executar testes

Instale o pytest:

```bash
pip install pytest
```

Se o repositório ainda não tiver um arquivo `pytest.ini`, crie-o na pasta raiz:

```ini
[pytest]
pythonpath = .
```

Em seguida, execute:

```bash
pytest -v
```

Todos os testes devem passar antes do envio de alterações.

### Compilar no Windows

O Spawn usa o Nuitka para gerar um executável independente. Instale o [Microsoft Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) com a carga de trabalho C++ e o Windows SDK. Depois, instale o Nuitka:

```bash
pip install nuitka
```

Para uma compilação de 64 bits:

```bash
python -m nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --assume-yes-for-downloads --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```

Para uma compilação de 32 bits, adicione `--target=x86`. O executável gerado ficará na pasta `dist`. Se a compilação falhar em um sistema de 32 bits, tente `--msvc=latest`; como último recurso, tente `--mingw64`.

</details>
