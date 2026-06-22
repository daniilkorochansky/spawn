![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Language](https://img.shields.io/badge/language-Python-yellow.svg)
![Tests](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml/badge.svg)
[![build](https://github.com/daniilkorochansky/spawn/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/daniilkorochansky/spawn/actions/workflows/build.yml)
![Status](https://img.shields.io/badge/status-active-success.svg)

<div align="center">
  [<a href="https://github.com/daniilkorochansky/spawn">English</a>
  /
  <a href="https://github.com/daniilkorochansky/spawn/blob/master/README_ru.md">Русский</a>
  /
  Português]
</div>

# Spawn
<img width="180" height="180" alt="spawn_new" src="https://github.com/user-attachments/assets/18435694-229c-468d-87af-11f9ed4d243e" />

Um ambiente de desenvolvimento (IDE) rápido e moderno, criado especificamente para o desenvolvimento de servidores open.mp e SA-MP na linguagem de programação Pawn.

Ele reúne ferramentas de edição de Pawn, integração com o SAMPCTL, gerenciamento de dependências, o sistema de controle de versão Git e ferramentas de navegação pelo projeto em um único ambiente de desenvolvimento, criado levando em conta as necessidades dos desenvolvedores de servidores multijogador.

Por ser portátil, extensível e voltado para o aumento da produtividade, o Spawn ajuda a criar, gerenciar e manter projetos sem a necessidade de editores de código genéricos.

## Visão geral
<img width="1920" height="1049" alt="ui" src="https://github.com/user-attachments/assets/505d6a46-33cc-45ae-bed3-f011474a4dc7" />

## Índice
- [Características](#características)
- [Por que o Spawn IDE? (Comparação)](#por-que-o-spawn-ide-comparação)
- [Capturas de tela](#capturas-de-tela)
  - [Criação do projeto](#criação-do-projeto)
  - [Divisão do editor de código](#divisão-do-editor-de-código)
  - [Pré-visualização da cor no formato RGBA/HEX](#pré-visualização-da-cor-no-formato-rgbahex)
  - [Gerenciador de dependências](#gerenciador-de-dependências)
  - [Git e Controle de Versões (Source Control)](#git-e-controle-de-versões)
  - [Árvore do projeto](#árvore-do-projeto)
- [Instalação](#instalação)
  - [Download](#download)
  - [Ferramentas adicionais](#ferramentas-adicionais)
- [Introdução rápida](#introdução-rápida)
  - [Criação do projeto](#criação-do-projeto)
  - [Gerenciamento de dependências](#gerenciamento-de-dependências)
  - [Como usar o Git](#como-usar-o-git)
  - [Compilação e inicialização do servidor](#compilação-e-inicialização-do-servidor)
  - [Trabalho com arquivos individuais](#trabalho-com-arquivos-individuais)
  - [Determinação da codificação](#determinação-da-codificação)
- [Desenvolvimento](#desenvolvimento)
  - [Requisitos](#requisitos)
  - [Clonagem do repositório](#clonagem-do-repositório)
  - [Instalação de dependências](#instalação-de-dependências)
  - [Lançamento](#lançamento)
  - [Compilação do arquivo executável (Windows)](#compilação-do-arquivo-executável-windows)
  - [Testes](#testes)
- [Colaboradores](#colaboradores)
  - [Relatório de erros](#relatório-de-erros)
- [Doações](#doações)
- [Licença](#licença)

## Características
+ Desenvolvido especialmente para o [open.mp](https://github.com/openmultiplayer) e o desenvolvimento do SA-MP.
+ Integração embutida com o [SAMPCTL](https://github.com/Southclaws/sampctl) para criar, iniciar e gerenciar projetos.
+ Gerenciador de dependências para facilitar a instalação e atualização de pacotes e componentes de servidor.
+ Suporte integrado ao Git com indicadores de status do repositório e histórico de commits.
+ Marcadores do histórico de alterações para rastrear linhas alteradas e salvas.
+ Correspondência e destaque automáticos de chaves
+ Visualização prévia de cores para valores RGBA e HEX diretamente no editor.
+ Integração da ferramenta de seleção de cores para inserir rapidamente cores no código Pawn.
+ Modo “Editor de código dividido” para trabalhar simultaneamente com vários arquivos.
+ Árvore de projeto otimizada para projetos de grande porte.
+ Painéis integrados de saída de resultados de compilação e do console do servidor.
+ Monitoramento e atualização automáticos dos arquivos do projeto.
+ Versão portátil (não requer instalação).

## Por que o Spawn IDE? (Comparação)

O Spawn foi criado do zero para oferecer uma interface moderna e eficiente em termos de recursos aos desenvolvedores, sem a complexidade excessiva dos editores web e as restrições rígidas das ferramentas ultrapassadas.

| Características e funcionalidades | Pawno | Qawno (open.mp) | VS Code (com plug-ins) | Spawn IDE |
| :--- | :---: | :---: | :---: | :---: |
| **Uso da memória RAM** | 🟢 ~10-20 MB | 🟢 ~40-60 MB | 🔴 ~300-800+ MB (Electron) | 🟢 **~30-50 MB (Interface de usuário nativa)** |
| **Suporte multiplataforma** | 🔴 Apenas Windows | 🔴 Apenas Windows | 🟢 Linux, Windows и macOS | 🟢 **Linux и Windows (Nativo)** |
| **Git / Controle de versões** | 🔴 Ausente | 🔴 Ausente | 🟡 Por meio de plug-ins (consome muitos recursos) | 🟢 **Embutido (leve)** |
| **SAMPCTL** | 🔴 Ausente | 🔴 Ausente | 🟡 Com o auxílio de plug-ins de terceiros | 🟢 **Integração embutida** |
| **Conversão de EOL (LF/CRLF)** | 🔴 Ausente | 🔴 Ausente | 🟢 Integrado | 🟢 **Integrado** |
| **Determinação da codificação** | 🔴 Ausente | 🔴 Ausente | 🟡 Normais | 🟢 **Inteligente (conforme a regra do comentário)** |
| **Paleta de cores integrada** | 🔴 Ausente | 🟢 Direto da caixa | 🔴 É necessária uma ampliação | 🟢 **Direto da caixa** |
| **Gerenciador de pacotes (Pawndex)**| 🔴 Ausente | 🔴 Ausente | 🔴 Ausente | 🟡 **No mapa de desenvolvimento (Nativo)** |
| **IntelliSense e autocompletar** | 🔴 Ausente | 🟡 Principal (Lento) | 🟢 Bom (alta carga na CPU) | 🟡 **No mapa de desenvolvimento (rápido / baixa carga na CPU)** |
| **Divisão do editor de código** | 🔴 Ausente | 🔴 Ausente | 🟢 Integrado | 🟢 **Direto da caixa (3 ou mais abas)** |
| **Configuração e instalação** | 🟢 Portátil | 🟢 Portátil | 🔴 Configuração manual complexa | 🟢 **Portátil** |

## Capturas de tela
### Criação do projeto
<img width="1920" height="1080" alt="Project Creation" src="https://github.com/user-attachments/assets/14b70c29-96b4-4d7d-94ff-6307cfa35cac" />

### Divisão do editor de código
<img width="1920" height="1080" alt="Split Code Editor" src="https://github.com/user-attachments/assets/f0caa6e9-607b-48f1-8b58-ae95ef12f7b1" />

### Pré-visualização da cor no formato RGBA/HEX
<img width="1920" height="1080" alt="Color Preview" src="https://github.com/user-attachments/assets/ae6a367a-3b04-4a23-a6ad-71ae51b0edc8" />

### Gerenciador de dependências
<img width="1920" height="1080" alt="Dependency Manager" src="https://github.com/user-attachments/assets/e60a1bad-9a9d-43da-938d-fa94d43401b7" />

### Git e Controle de Versões
<img width="1920" height="1080" alt="Git and Source Control" src="https://github.com/user-attachments/assets/b6198ac3-97b4-4392-b29a-87ab6bdfc818" />

### Árvore do projeto
<img width="1920" height="1080" alt="Project Tree" src="https://github.com/user-attachments/assets/c942516b-6e18-406d-b9be-cb8e24d54a94" />

## Instalação
### Download
1. Baixe a versão mais recente na página “Release”.
2. Descompacte o arquivo em qualquer local.
3. Execute o ‘Spawn.exe’.

### Ferramentas adicionais
Para aproveitar todos os recursos do Spawn, você também pode instalar:
+ Git
+ [SAMPCTL](https://github.com/Southclaws/sampctl)

Essas ferramentas podem ser configuradas posteriormente nas configurações.

## Introdução rápida
### Criação do projeto
1. Selecione 'File' → 'New project...'.
2. Digite o nome do projeto e selecione sua localização.
3. Ao clicar no botão “Create”, a ferramenta de linha de comando SAMPCTL será iniciada. Para concluir a criação do projeto, siga as instruções exibidas na tela.
4. Ao concluir o processo, feche o utilitário de linha de comando SAMPCTL. O Spawn abrirá automaticamente um novo projeto.

### Gerenciamento de dependências
1. Selecione 'Project' → 'Dependency Manager...'.
2. Digite o nome do pacote no campo “Dependency”.
3. Clique em 'Install'.

+ Para remover uma dependência, selecione a desejada na lista e clique em 'Uninstall'.
+ Para verificar se todas as dependências estão corretas, clique no botão chamado 'Ensure'.

### Como usar o Git
1. Clique com o botão direito do mouse na pasta raiz na árvore do projeto → selecione “Initialize Repository”. (Caso o repositório ainda não esteja no servidor)
2. Crie seu primeiro commit.
3. Acompanhe as alterações diretamente no Spawn.

Se o repositório já estiver no servidor, o Spawn o detectará automaticamente (desde que o suporte ao Git esteja ativado nas configurações).

### Compilação e inicialização do servidor
1. Abra a pasta raiz do servidor em “File” → “Open Server Folder...” (O servidor deve conter obrigatoriamente o arquivo ‘pawn.json’ gerado por meio do [SAMPCTL](https://github.com/Southclaws/sampctl))
2. Acesse seu servidor em ‘Build’ → ‘Build Server’ ou clique no botão correspondente na barra de ferramentas.
3. Inicie seu servidor em ‘Server’ → ‘Run / Stop Server’ ou clique no botão correspondente na barra de ferramentas.
4. Acompanhe a exibição dos dados no console integrado.

Você está pronto para desenvolver servidores open.mp e SA-MP usando o Spawn.

### Trabalho com arquivos individuais
É possível usar o Spawn mesmo sem abrir o projeto.

Para editar os arquivos:
1. Selecione 'File' → 'Open File...'.
2. Selecione os arquivos.
3. Comece a editar agora mesmo.

Ao trabalhar com arquivos individuais, recursos do editor como destaque de sintaxe, visualização de cores, correspondência de chaves, visualização dividida do editor de código e marcações do histórico de alterações permanecem totalmente disponíveis.

Para utilizar os recursos específicos do projeto, como a árvore do projeto, a integração com o Git, o gerenciador de dependências e as ferramentas SAMPCTL, é necessário que o projeto esteja aberto.

### Determinação da codificação
O Spawn identifica automaticamente a codificação dos arquivos ao abri-los.

Para os arquivos de origem do Pawn (`.pwn` e `.inc`), é possível especificar explicitamente a codificação por meio da diretiva `coding` no início do arquivo:

```pawn
// -*- coding: cp1251 -*-
```

Se essa diretiva estiver presente, o Spawn utilizará a codificação especificada ao abrir e salvar o arquivo.

Se não houver uma diretiva de codificação, o Spawn tentará determinar a codificação do arquivo automaticamente.

#### Reabrir arquivos com outra codificação
Em alguns casos, a detecção automática pode identificar incorretamente a codificação do arquivo.

Se o arquivo não for exibido corretamente, é possível abri-lo novamente usando outra codificação:

`Edit → Encoding → Reopen`

*Essa operação não altera o arquivo no disco e afeta apenas a forma como o arquivo é exibido no editor.*

#### Codificações compatíveis
* UTF-8 (Unicode)
* Windows-1250 (da Europa Central)
* Windows-1251 (Alfabeto cirílico)
* Windows-1252 (da Europa Ocidental)
* Windows-1253 (Grega)
* Windows-1254 (Turco)
* Windows-1255 (Hebraico)
* Windows-1256 (Árabe)
* Windows-1257 (Báltico)

#### Codificação padrão do Pawn
Você pode definir a codificação padrão usada para os arquivos-fonte Pawn recém-criados.

Ao criar um novo arquivo com a extensão `.pwn` ou `.inc`, o Spawn pode inserir automaticamente uma diretiva de codificação de acordo com a codificação padrão selecionada.

## Desenvolvimento
### Requisitos
+ Python 3.13+
+ wxPython
+ GitPython
+ Markdown
+ watchdog
+ platformdirs
+ requests

### Clonagem do repositório
```
https://github.com/daniilkorochansky/spawn.git
```
ou
```
gh repo clone daniilkorochansky/spawn
```

### Instalação de dependências
Na pasta raiz, execute:
```
pip install -r requirements.txt
```
### Lançamento
Além disso, na pasta raiz, execute:
```
python main.py
```

### Compilação do arquivo executável (Windows)
O Spawn utiliza o Nuitka para criar compilações executáveis autônomas.

1. Instale o Microsoft Visual Studio com o conjunto de ferramentas para C++ e o Windows SDK: https://visualstudio.microsoft.com/downloads/
2. Reinicie o seu computador
3. Instale o Nuitka:
```
pip install nuitka
```
4. Abra o prompt de comando na pasta raiz e compile o arquivo executável:
```
nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```
ou (Windows x86):
```
nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --target=x86 --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```
Se isso não funcionar em um sistema de 32 bits, tente adicionar a opção: ```--msvc=latest``` (como último recurso, em vez dessa opção, adicione: ```--mingw64```)

A ordem das etapas é **importante**!

*O arquivo executável gerado estará disponível na pasta ‘dist’.*

### Testes
Você pode realizar testes para verificar o funcionamento de novos recursos ou alterações em componentes-chave do sistema.
Para executar os testes, siga estas etapas:
1. Instale o pytest
```
pip install pytest
```
2. Crie na pasta raiz um arquivo chamado ‘pytest.ini’ com o seguinte conteúdo (caso ele não exista)
```
[pytest]
pythonpath = .
```
3. Abra o prompt de comando na pasta raiz
4. Execute o seguinte comando: ```pytest -v```

Todos os testes devem ser concluídos com o resultado ‘PASSED’.
Caso contrário, você precisará localizar e corrigir o erro ou bug no seu código e, em seguida, executar os testes novamente.

## Colaboradores
O Spawn é um projeto de código aberto criado para desenvolvedores de servidores open.mp e SA-MP.

São bem-vindas todas as contribuições, incluindo:
+ Mensagens de erro
+ Sugestões sobre novas funcionalidades
+ Sugestões sobre UI/UX
+ Contribuição para o desenvolvimento do código
+ Testes e avaliações

Obrigado por ajudar a tornar o Spawn melhor para todos.

### Relatório de erros
Se você tiver encontrado um erro ou uma falha ao usar o Spawn, siga estas etapas:
1. Selecione 'Help' -> 'Bug Report'.
2. Clique no botão “Copy” (se o campo “Log Output” estiver vazio, passe diretamente para a próxima etapa).
3. Clique no botão 'Open GitHub Issue'.
4. Cole o relatório pronto na descrição e insira um título (se o campo “Log Output” estiver vazio, por favor, descreva o erro ou a falha por conta própria).

## Doações
O Spawn está sendo desenvolvido no tempo livre e sempre permanecerá gratuito e de código aberto.

Se você gosta do Spawn e deseja apoiar seu desenvolvimento futuro, pode fazer uma doação.
Cada contribuição ajuda a melhorar o IDE e a garantir o desenvolvimento contínuo do projeto.

Obrigado pelo seu apoio ❤️

[Fazer uma doação pelo Boosty](https://boosty.to/daniilkorochansky)

## Licença
O programa Spawn é distribuído sob a licença GNU General Public License v3.0.

Consulte [LICENSE](https://github.com/daniilkorochansky/spawn/blob/master/LICENSE) para mais detalhes.
