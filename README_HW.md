# Инструкция по запуску

Был использован Python 3.8.10

Для создания и активации виртуального окружения необходимо из корня проекта выполнить следующие команды:
```commandline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для получения основных рекомендаций: 
 - Запустить ноутбук `Week4Seminar.ipynb` 
 - Предварительно [скачать данные](https://drive.google.com/drive/folders/16v0CwfAFmIcgAMLJbPk7jClOM0fMsHk-?usp=share_link) и разместить в каталоге `botify/data/data_contextual` 
 - Итоговый файл с рекомендациями: `botify/data/tracks_hw.json`

Для формирование топа треков для каждого из рекомендеров: 
- Запустить ноутбук `HomeWork.ipynb` (1 раздел)
- Предварительно [скачать данные](https://drive.google.com/drive/folders/1X1DhKjMuDXNQCd8bYmroBwt9mNePhaRB?usp=share_link) и разместить в каталоге `botify/data/data_all_recommenders`   
*Примечание:* Там же отображены все проведенные A/B эксперименты (2-3 раздел).

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
