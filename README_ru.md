<div align="center">

# Spawn

**Лёгкая IDE для разработки на Pawn**

Разрабатывайте и управляйте серверами **open.mp** и **SA-MP** с интеграцией SAMPCTL, Git, менеджером зависимостей и редактором Pawn.

[![Платформы](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)](https://github.com/daniilkorochansky/spawn)
[![Язык](https://img.shields.io/badge/language-Python-yellow.svg)](https://www.python.org/)
[![Тесты](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml/badge.svg)](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml)
[![Сборка](https://github.com/daniilkorochansky/spawn/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/daniilkorochansky/spawn/actions/workflows/build.yml)
![Статус](https://img.shields.io/badge/status-active-success.svg)

[Скачать Spawn](https://github.com/daniilkorochansky/spawn/releases) · [Сообщить об ошибке](https://github.com/daniilkorochansky/spawn/issues) · [Участвовать в разработке](#участие-в-разработке)

[English](README.md) · [Русский](README_ru.md) · [Português](README_pt.md)

<img width="900" alt="Общий вид Spawn IDE" src="https://github.com/user-attachments/assets/505d6a46-33cc-45ae-bed3-f011474a4dc7" />

</div>

## Почему Spawn?

Spawn объединяет основные инструменты для разработки Pawn-серверов в лёгкой и портативной настольной IDE.

- **Редактор Pawn** — подсветка синтаксиса, сопоставление скобок, маркеры изменённых строк и разделение редактора.
- **Интеграция с SAMPCTL** — создание, сборка и запуск серверных проектов.
- **Менеджер зависимостей** — установка, обновление и проверка зависимостей проекта.
- **Интеграция с Git** — состояние репозитория, история коммитов и инструменты контроля версий.
- **Инструменты для работы с кодом** — предпросмотр цветов RGBA/HEX и палитра для вставки значений в код.
- **Навигация по проекту** — дерево файлов, рассчитанное на крупные проекты.
- **Встроенный вывод** — результаты сборки и консоль сервера прямо в IDE.
- **Поддержка кодировок** — автоматическое определение и настройка кодировок файлов Pawn.
- **Портативность** — запуск без традиционной установки.

## Установка

1. Откройте страницу [последнего релиза](https://github.com/daniilkorochansky/spawn/releases).
2. Скачайте и распакуйте архив.
3. Запустите `Spawn.exe`.

Для использования всех возможностей установите [Git](https://git-scm.com/downloads) и [SAMPCTL](https://github.com/Southclaws/sampctl). Их можно настроить позже в параметрах Spawn.

## Быстрый старт

### Создание проекта

1. Выберите **File → New Project…**.
2. Укажите название и расположение проекта.
3. Нажмите **Create** и следуйте инструкциям в окне командной строки SAMPCTL.
4. После завершения создания закройте окно командной строки. Spawn обнаружит новый проект.

### Сборка и запуск сервера

1. Выберите **File → Open Server Folder…** и откройте папку сервера с файлом `pawn.json`, созданным SAMPCTL.
2. Выберите **Build → Build Server**.
3. Используйте **Server → Run / Stop Server**, чтобы запустить или остановить сервер.
4. Следите за выводом во встроенной консоли.

### Управление зависимостями

Откройте **Project → Dependency Manager…**, введите название пакета и нажмите **Install**. Чтобы удалить зависимость, выберите её и нажмите **Uninstall**. Кнопка **Ensure** проверяет зависимости проекта.

### Использование Git

Щёлкните правой кнопкой мыши по корневой папке проекта и выберите **Initialize Repository**, если это ещё не Git-репозиторий. После этого можно создавать коммиты и отслеживать изменения в Spawn. Существующие репозитории обнаруживаются автоматически, если интеграция с Git включена в настройках.

### Работа с отдельными файлами

Файлы можно открывать через **File → Open File…** без открытия проекта. Подсветка синтаксиса, предпросмотр цветов, сопоставление скобок, разделение редактора и маркеры изменений остаются доступны. Для работы с деревом проекта, Git, менеджером зависимостей и инструментами SAMPCTL необходимо открыть проект.

## Кодировки файлов Pawn

Spawn определяет кодировку файлов при открытии. Для файлов `.pwn` и `.inc` её можно указать в начале файла:

```pawn
// -*- coding: cp1251 -*-
```

Если файл отображается некорректно, откройте его заново с другой кодировкой через **Edit → Encoding → Reopen**. Это меняет только отображение в редакторе и не изменяет файл на диске.

Поддерживаются UTF-8 и кодовые страницы Windows 1250–1257. Кодировку по умолчанию для новых файлов Pawn можно выбрать в настройках. Spawn может автоматически добавлять соответствующую директиву.

## Скриншоты

<details>
<summary>Показать скриншоты возможностей</summary>

### Создание проекта
<img width="900" alt="Создание проекта" src="https://github.com/user-attachments/assets/14b70c29-96b4-4d7d-94ff-6307cfa35cac" />

### Разделённый редактор
<img width="900" alt="Разделённый редактор кода" src="https://github.com/user-attachments/assets/f0caa6e9-607b-48f1-8b58-ae95ef12f7b1" />

### Предпросмотр RGBA/HEX
<img width="900" alt="Предпросмотр цветов" src="https://github.com/user-attachments/assets/ae6a367a-3b04-4a23-a6ad-71ae51b0edc8" />

### Менеджер зависимостей
<img width="900" alt="Менеджер зависимостей" src="https://github.com/user-attachments/assets/e60a1bad-9a9d-43da-938d-fa94d43401b7" />

### Git и контроль версий
<img width="900" alt="Git и контроль версий" src="https://github.com/user-attachments/assets/b6198ac3-97b4-4392-b29a-87ab6bdfc818" />

### Дерево проекта
<img width="900" alt="Дерево проекта" src="https://github.com/user-attachments/assets/c942516b-6e18-406d-b9be-cb8e24d54a94" />

</details>

## Участие в разработке

Приветствуются сообщения об ошибках, предложения по функциям и интерфейсу, изменения кода, тестирование и обратная связь.

Чтобы сообщить об ошибке из Spawn:

1. Выберите **Help → Bug Report**.
2. Скопируйте сформированный отчёт. Если поле **Log Output** пустое, опишите проблему самостоятельно.
3. Нажмите **Open GitHub Issue** и вставьте отчёт в описание задачи.

Также можно [создать issue на GitHub](https://github.com/daniilkorochansky/spawn/issues).

## Поддержать проект

Spawn — бесплатный проект с открытым исходным кодом. Поддержать его развитие можно через:

- [VK Donut](https://vk.com/spawn_ide)
- [Boosty](https://boosty.to/daniilkorochansky)

## Лицензия

Spawn распространяется по лицензии **GNU General Public License v3.0**. Подробности — в файле [LICENSE](LICENSE).

---

<details>
<summary>Настройка среды разработки</summary>

### Требования

- Python 3.13+
- wxPython
- GitPython
- Markdown
- watchdog
- platformdirs

### Клонирование и запуск

```bash
git clone https://github.com/daniilkorochansky/spawn.git
cd spawn
pip install -r requirements.txt
python main.py
```

### Запуск тестов

Установите pytest:

```bash
pip install pytest
```

Если в корне репозитория ещё нет файла `pytest.ini`, создайте его:

```ini
[pytest]
pythonpath = .
```

Затем выполните:

```bash
pytest -v
```

Перед отправкой изменений убедитесь, что все тесты проходят.

### Сборка под Windows

Spawn использует Nuitka для создания автономного исполняемого файла. Установите [Microsoft Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) с компонентами C++ и Windows SDK, затем установите Nuitka:

```bash
pip install nuitka
```

Для 64-битной сборки:

```bash
python -m nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --assume-yes-for-downloads --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```

Для 32-битной сборки добавьте `--target=x86`. Готовый файл появится в папке `dist`. Если сборка не проходит на 32-битной системе, попробуйте `--msvc=latest`; в крайнем случае — `--mingw64`.

</details>
