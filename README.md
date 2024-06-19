# Муханов М.Э. Проект приложения автоматизированного учета, проверки и маркировки МНИ

## Процесс запуска приложения:
  1. Установите python 3.10+ с официальной страницы [Текст ссылки]([https://www.example.com](https://www.python.org/downloads/release/python-31012/))
  2. Скачайте проект с GitHub.
  3. В командной строке перейдите в папку со скачанным проектом и разверните виртуальное окружение venv:
      - `sudo apt install -y python3-venv `
      - `sudo apt install -y build-essential libssl-dev libffi-dev python3-dev`
      - `python -m venv venv`
          - Для запуска venv в Windows:
            `venv\Scripts\activate.bat`
          - Для запуска venv в Windows:
            `source venv/bin/activate`
  4. Установите необходимые библиотеки из req.txt
      - `cat req.txt | xargs -n 1 pip install`
  5. Отдельно установите библиотеку pygost, либо скачайте её из GitHub в папку с проктом на вашем ПК и начинайте с 3-й команды:
      - `wget http://www.pygost.cypherpunks.ru/pygost-5.13.tar.zst`
      - `zstd -d < pygost-5.13.tar.zst | tar xf -`
      - `cd pygost-5.13`
      - `python setup.py install`
      - `cd ..`
  6. Запустите приложение из корневой директории проекта на вашем ПК:
      - `python.exe .\main.py`
