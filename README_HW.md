# Инструкция по запуску

Был использован Python 3.8.10

Для создания и активации виртуального окружения необходимо из корня проекта выполнить следующие команды:
```commandline
python3.8 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для получения основных рекомендаций использовался ноутбук `Week4Seminar.ipynb` с данными из каталога `botify/data/data_contextual`. Файл с рекомендациями: `botify/data/tracks_hw.json`. Формирование топа треков для каждого из рекомендеров проводилось в ноутбуке `HomeWork.ipynb` с данными из каталога `botify/data/data_all_recommenders`, там же отображены все проведенные A/B эксперименты.

Запуск сервиса и проведение итогового A/B эксперимента (аналогично семинарам):
1. Запустить сервис botify (`botify/README.md`)
2. Запустить симуляцию (`sim/README.md`)  
*Пример моей команды*
```sh
python sim/run.py --episodes 20000 --config config/env.yml multi --processes 2
```
3. Сохранить результаты симуляции в файл  
*Пример собранных данных `botify/data/data_contextual/data_comparison_with_contextual.json`*
4. Получить результаты эксперимента можно во 2-3 разделе ноутбука `HomeWork.ipynb` или же в `Week1Seminar.ipynb`. 
