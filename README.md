# Архиватор и распаковщик
Утилита для создания и распаковки архивов с поддержкой форматов Zstandard (.zstd) и BZ2 (.bz2). Поддерживает как отдельные файлы, так и директории.
Возможности:
- Создание архивов в форматах .zstd и .bz2
- Распаковка архивов .zstd и .bz2
- Автоматическое определение типа архива по расширению
- Поддержка как файлов, так и директорий
- Замер времени выполнения операций (benchmark mode)
- Автоматическое распознавание tar-архивов

# Использование и ключи
1) -b, --benchmark - включить режим замера времени (опционально)
2) create - команда создания архива
3) extract - команда распаковки архива

# Синтаксис
python main.py [-b] <command> [аргументы]
# Команды
- Создание архива
  python main.py create [-b] <исходный_файл_или_папка> <выходной_архив>
- Распаковка архива
  python main.py extract [-b] <архив> <целевая_папка>

# Поддерживаемые форматы
- Форматы Zstandard, BZ2
- Расширения .zstd, .bz2	

# Создание архива
- Если исходный путь - директория, она сначала упаковывается в tar, затем сжимается
- Если исходный путь - файл, он сжимается напрямую
- Формат определяется по расширению выходного файла
# Распаковка
- Автоматически определяется, является ли архив tar-контейнером
- Если это tar-архив - извлекается содержимое
- Если это одиночный файл - сохраняется с исходным именем

# Примеры использования
# 1. Сжатие и распаковка файла (bz2)
Команды:
- python main.py -b create 1.txt output/1.bz2 
- python main.py -b extract output/1.bz2 output
<img width="1433" height="846" alt="image" src="https://github.com/user-attachments/assets/6bc25a81-462d-48b9-8724-b016fe2229f8" />

# 2. Сжатие и распаковка файла (Zstandard)
Команды:
- python main.py -b create 2.txt output/2.zstd
- python main.py -b extract output/2.zstd output
<img width="1443" height="954" alt="image" src="https://github.com/user-attachments/assets/cced8f6a-40d8-4885-91f3-a1a3436fcb35" />

# 3. Сжатие и распаковка директории (bz2)
Команды:
- python main.py -b create dir output/first_dir.bz2
- python main.py -b extract output/first_dir.bz2 output
<img width="1408" height="953" alt="image" src="https://github.com/user-attachments/assets/385ed038-d2aa-469a-ae27-422c7c26fa16" />

# 4. Сжатие и распаковка директории (Zstandard)
Команды:
- python main.py -b create dir output/second_dir.zstd
- python main.py -b extract output/second_dir.zstd output
<img width="1540" height="943" alt="image" src="https://github.com/user-attachments/assets/0b480e50-1ab6-495b-aad9-959683e5e456" />

