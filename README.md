# Муханов М.Э. Проект приложения автоматизированного учета, проверки и маркировки МНИ

## Процесс запуска приложения:
  1. Установите python 3.10+ с официальной страницы [ссылка на python](https://www.python.org/downloads/release/python-31012/)
  2. Скачайте проект с GitHub.
![image](https://github.com/Motyaozzz/Diplom/assets/89969066/4791c48d-fda7-424f-99a9-689422935229)
  3. Создайте папку для проекта и распакуйте туда скачанный архив.
  4. В терминале перейдите в папку с проектом и разверните виртуальное окружение venv:
      - Linux:
          - `sudo apt install -y python3-venv `
          - `sudo apt install -y build-essential libssl-dev libffi-dev python3-dev`
          - `python -m venv venv`
          - `source venv/bin/activate`
      - Windows:
          - `python -m venv venv`
          - `source venv/bin/activate`
  5. Установите необходимые библиотеки из req.txt
      - `cat req.txt | xargs -n 1 pip install`
  6. Отдельно установите библиотеку pygost, либо скачайте её из GitHub в папку с проктом на вашем ПК и начинайте с 3-й команды:
      - `wget http://www.pygost.cypherpunks.ru/pygost-5.13.tar.zst`
      - `zstd -d < pygost-5.13.tar.zst | tar xf -`
      - `cd pygost-5.13`
      - `python setup.py install`
      - `cd ..`
  7. Запустите приложение из корневой директории проекта на вашем ПК:
      - `python.exe .\main.py`
