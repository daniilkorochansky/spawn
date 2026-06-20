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
- [Установка](#установка)
  - [Скачивание](#скачивание)
  - [Дополнительные инструменты](#дополнительные-инструменты)
- [Быстрый старт](#быстрый-старт)
  - [Создание проекта](#создание-проекта)
  - [Управление зависимостями](#управление-зависимостями)
  - [Использование Git](#использование-git)
  - [Сборка и запуск сервера](#сборка-и-запуск-сервера)
  - [Работа с отдельными файлами](#работа-с-отдельными-файлами)
  - [Определение кодировки](#определение-кодировки)
- [Разработка](#разработка)
  - [Требования](#требования)
  - [Клонирование репозитория](#клонирование-репозитория)
  - [Установка зависимостей](#установка-зависимостей)
  - [Запуск](#запуск)
  - [Сборка исполняемого файла (Windows)](#сборка-исполняемого-файла-windows)
  - [Тесты](#тесты)
- [Участники](#участники)
  - [Отчёт об ошибках](#отчёт-об-ошибках)
- [Пожертвования](#пожертвования)
- [Лицензия](#лицензия)

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

## Установка
### Скачивание
1. Скачайте последнюю версию на странице 'Release'.
2. Распакуйте архив в любое место.
3. Запустите 'Spawn.exe'.

### Дополнительные инструменты
Чтобы воспользоваться всеми функциями Spawn, вы также можете установить:
+ Git
+ [SAMPCTL](https://github.com/Southclaws/sampctl)

Эти инструменты можно настроить позже в настройках.

## Быстрый старт
### Создание проекта
1. Выберите 'File' → 'New Project...'.
2. Введите название проекта и выберите его местоположение.
3. После нажатия кнопки 'Create' запустится инструмент командной строки SAMPCTL. Для завершения создания проекта следуйте инструкциям на экране.
4. По завершении процесса закройте утилиту командной строки SAMPCTL. Spawn автоматически откроет новый проект.

### Управление зависимостями
1. Выберите 'Project' → 'Dependency Manager...'.
2. Введите имя пакета в поле 'Dependency'.
3. Нажмите 'Install'.

+ Чтобы удалить зависимость, выберите нужную из списка и нажмите 'Uninstall'.
+ Чтобы проверить что все зависимости в порядке, нажмите кнопку под названием "Ensure'.

### Использование Git
1. Щелкните правой кнопкой мыши по корневой папке в дереве проекта → выберите 'Initialize Repository'. (Если репозиторий еще не был на сервере)
2. Создайте свой первый коммит.
3. Отслеживайте изменения прямо из Spawn.

Если репозиторий уже находится на сервере, Spawn автоматически его обнаружит (при условии, что в настройках включена поддержка Git)

### Сборка и запуск сервера
1. Откройте корневую папку с сервером 'File' → 'Open Server Folder...' (Cервер обязательно должен содержать файл 'pawn.json' сгенерированный через [SAMPCTL](https://github.com/Southclaws/sampctl))
2. Соберите ваш сервер 'Build' → 'Build Server' или нажмите на соотвествующую кнопку в панели инструментов.
3. Запустите ваш сервер 'Server' → 'Run / Stop Server' или нажмите на соотвествующую кнопку в панели инструментов.
4. Следите за выводом данных во встроеной консоли.

Вы готовы к разработке серверов open.mp и SA-MP с помощью Spawn.

### Работа с отдельными файлами
Spawn можно использовать и без открытия проекта.

Чтобы отредактировать один файл:
1. Выберите 'File' → 'Open File...'.
2. Выберите исходный файл Pawn, файл включения или файл конфигурации.
3. Начните редактировать сразу

При работе с отдельными файлами такие функции редактора, как подсветка синтаксиса, предпросмотр цветов, сопоставление фигурных скобок, разделенный вид редактора кода и метки истории изменений, остаются полностью доступными.

Для работы с функциональными возможностями, специфичными для проекта, такими как дерево проекта, интеграция с Git, менеджер зависимостей и инструменты SAMPCTL, необходимо, чтобы проект был открыт.

### Определение кодировки
Spawn автоматически определяет кодировку файла при его открытии.

В некоторых случаях автоматическое определение кодировки Windows-1251 (CP1251) может быть неточным.

Если файл отображается некорректно, его можно открыть заново с использованием другой кодировки: выберите 'Edit' → 'Encoding' → 'Reopen'.

Поддерживаемые кодировки:
+ UTF-8
+ Windows-1251 (CP1251)

*Это не приводит к изменению файла на диске и влияет только на то, как файл отображается в редакторе.*

## Разработка
### Требования
+ Python 3.13+
+ wxPython
+ GitPython
+ Markdown
+ watchdog
+ platformdirs

### Клонирование репозитория
```
https://github.com/daniilkorochansky/spawn.git
```
или
```
gh repo clone daniilkorochansky/spawn
```

### Установка зависимостей
В корневой папке, выполните:
```
pip install -r requirements.txt
```
### Запуск
Также в корневой папке, выполните:
```
python main.py
```

### Сборка исполняемого файла (Windows)
Spawn использует Nuitka для создания автономных исполняемых сборок.

1. Установите средства сборки Microsoft Visual Studio с набором инструментов для C++ и Windows SDK: https://visualstudio.microsoft.com/downloads/
2. Перезагрузите ваш компьютер
3. Установите Nuitka:
```
pip install nuitka
```
4. Откройте командную строку в корневой папке и скомпилируйте исполняемый файл:
```
nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```
или (Windows x86):
```
nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --target=x86 --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```
Если на 32-битной системе это не удается, попробуйте добавить опцию: ```--msvc=latest``` (в крайнем случае, вместо этой опции добавьте: ```--mingw64```)

Порядок действий **важен**!

*Полученный исполняемый файл будет доступен в папке 'dist'.*

### Тесты
Вы можете проводить тестирование для проверки работоспособности новых функций или изменений в ключевых компонентах системы.
Чтобы запустить тесты, выполните следующие действия:
1. Установите pytest
```
pip install pytest
```
2. Создайте в корневой папке файл с именем 'pytest.ini' со следующим содержанием (если он не существует)
```
[pytest]
pythonpath = .
```
3. Откройте командную строку в корневой папке
4. Выполните следующую команду: ```pytest -v```

Все тесты должны завершиться с результатом 'PASSED'.
В противном случае вам необходимо найти и исправить ошибку или баг в вашем коде, а затем запустить тесты снова.

## Участники
Spawn — это проект с открытым исходным кодом, созданный для разработчиков серверов open.mp и SA-MP.

Приветствуются любые вклады, в том числе:
+ Сообщения об ошибках
+ Предложения по новым функциям
+ Предложения по UI/UX
+ Вклад в разработку кода
+ Тестирование и отзывы

Спасибо, что помогаете сделать Spawn лучше для всех.

### Отчёт об ошибках
Если при использовании Spawn у вас возникла ошибка или сбой, выполните следующие действия:
1. Выберите 'Help' -> 'Bug Report'.
2. Нажмите кнопку 'Copy' (если поле 'Log Output' пустое, сразу переходите к следующему шагу).
3. Нажмите кнопку 'Open GitHub Issue'.
4. Вставьте готовый отчет в описание и введите заголовок (если поле 'Log Output' пусто, пожалуйста, опишите ошибку или баг самостоятельно).

## Пожертвования
Spawn разрабатывается в свободное время и всегда будет оставаться бесплатным и открытым.

Если вам нравится Spawn и вы хотите поддержать его дальнейшее развитие, вы можете сделать пожертвование.
Каждый вклад помогает улучшить IDE и обеспечить дальнейшее развитие проекта.

Спасибо за вашу поддержку ❤️

[Пожертвовать с VK Donut](https://vk.com/spawn_ide)

[Пожертвовать с Boosty](https://boosty.to/daniilkorochansky)

## Лицензия
Программа Spawn распространяется по лицензии GNU General Public License v3.0.

Смотрите [LICENSE](https://github.com/daniilkorochansky/spawn/blob/master/LICENSE) для подробностей.
