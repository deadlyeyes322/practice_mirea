# Как запустить парсер

### Скопируйте репозиторий

Ссылку на репозиторий получаем справа по зеленой кнопке
```
git clone <ссылка на репозиторий>
```

### Перейдите в папку с репозиторием и установите виртуальное окружение
```
cd practice_mirea
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
### Перейдите в data_pars и запустите скрипт
```
cd data_pars
python parser_class.py
```

Парсер закинет ваши данные в базу данных (файл: database.db), можете отдельно открыть его он будет называться с названием области вашего изучения
Затем эти данные вы будете открывать либо переводить в формат csv в своем анализе данных

## Анализ
Для каждой области изучения уже созданы отдельные папки
Туда поместите ваши csv файлы с информацией о вузах
Туда же вы будете сохранять ipynb файлы.
Писать код советую в google colab, так как там можно раздать доступ остальным участникам и работать совместно
