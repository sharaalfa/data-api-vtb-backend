#  Инструкция по работе с сервисом data-api-vtb-backend

Цель закрепить порядок работы с сервисом.

## Пошаговое руководство

1. Загружаем либы питона:
```bash
   pip install -r py/requirements.txt
   pip install -r py/requirements_ml.txt
```
2. Запускаем сервер на питоне:
```bash
   python py/server.py
```
3. Запускаем сервер на go:
```bash
   go run cmd/main.go
```
4. Наблюдаем и пользуемся api по адресу:
   http://localhost:8080/sw/
  