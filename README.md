#  Инструкция по работе с сервисом data-api-vtb-backend

Цель закрепить порядок работы с сервисом на основе go, python, grpc и swagger codegen.

## Пошаговое руководство

1. Запускаем сервис:
```scala
   sbt run
```
2. Загружаем image swagger-editor командой, если не установлено:
```bash
   docker pull swaggerapi/swagger-editor
```
3. Запускаем swagger-editor командой, например, на 85 порту и согласно текущей конфигурации адреса сервиса:
```bash
   docker run -d -p 85:8080 -e URL="http://localhost:8085/v1/swagger.json" swaggerapi/swagger-editor
```
4. Наблюдаем и пользуемся swagger-editor по адресу:
   http://localhost:85
  