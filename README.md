# ДЗ3 — Docker

## Что в репо?

- `app/app.py` — исходный код приложения. Его не трогал и не менял никак, что и было написано в задании.
- `app/requirements.txt` — зависимости Pythonа.
- `Dockerfile` — инструкция для докера по сборке докер-образа.
- `compose.yaml` — файл конфигурации, для нескольких Docker-контейнеров для выполнения пунктов на 6-10 баллов.
- `.env.example` — пример файла переменных окружения для пункта на 6 баллов.
- `.dockerignore` — убираем лишнее из сборки.
- `scripts/check.py` — скрипт автоматической проверки для десяточки с резервным копированием данных Redis и удалением тестового окружения.

## Что необходимо для запуска?

### Один контейнер на `sqlite` для пунктов на 4-6 баллов

```sh
docker build -t hw3-dock:ver1 .
docker run -d --name hw3-first -p 8080:8000 -e GREETING="Hello, hello!" hw3-dock:ver1
```

### Несколько контейнеров через Docker Compose с `redis` для пунктов на 8-10 баллов

```sh
docker compose up -d --build --wait
```

### Python скрипт для 10!

```sh
python3 scripts/check.py
```

---

## Отчёт проверок для зачета задания

### 4 балла — сборка образа и запуск контейнера

Создал и запустил контейнер, проверил что при POST счетчик увеличивается (0->1->2), как и требует задание. + вывел логи докера, после удалил контейнер, чтобы освободить порт и
можно было спокойно переходить к пункту на 6 баллов.

Команда и её вывод (если был)

```
$docker build -t hw3-dock:ver1 .$ docker run -d --name hw3-first -p 8080:8000 -e GREETING="Hello, hello!" hw3-dock:ver1
8e306730fe1d6d7cd55009ce8bc5ccda407e761030199277de37ac6a42d73b72
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, hello!", "count": 1, "hostname": "8e306730fe1d", "storage": "sqlite"}

$ curl -fsS [http://127.0.0.1:8080/readyz](http://127.0.0.1:8080/readyz)
{"status": "ready", "storage": "sqlite"}

$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, hello!", "count": 2, "hostname": "8e306730fe1d", "storage": "sqlite"}

$ docker logs hw3-first
2026-11-23 14:15:58,603 listening port=8000 storage=sqlite
2026-11-23 14:16:39,810 http 172.17.0.1 "GET / HTTP/1.1" 200 -
2026-11-23 14:16:39,845 http 172.17.0.1 "POST /increment HTTP/1.1" 200 -
2026-11-23 14:16:39,872 http 172.17.0.1 "GET /readyz HTTP/1.1" 200 -
2026-11-23 14:20:49,781 http 172.17.0.1 "POST /increment HTTP/1.1" 200 -

$ docker rm -f hw3-first
hw3-first
```

### 6 баллов — Docker Compose

В качестве теста в .env записал: `APP_PORT=8088` и `GREETING=Hello, another check!`. Так как надо было позданию проверить что все работает с настраевыми портами и приветсвием.
Поле этого создали контейнер, седали два POST, счётчик стал 2, после этого удлили контейнер и посмотретрили, что всё сохранилось при пересоздании контейнера.
Прикрепил вначале итоговую версию с redis (на sqlite внизу этого блока), так как пока делал сначала на sqlite забыл попробовать с портами и привествием не по умолчанию, а после уже всё перевёл на redis.(

Команда и её вывод (если был)

```
$ docker compose up -d --build --wait
[+] up 5/5
 ✔ Image hw_3_own-app         Built
 ✔ Network hw_3_own_default   Created
 ✔ Volume hw_3_own_redis_data Created
 ✔ Container hw_3_own-redis-1 Healthy
 ✔ Container hw_3_own-app-1   Healthy

$ curl -fsS [http://127.0.0.1:8088/](http://127.0.0.1:8088/)
{"greeting": "Hello, another check!", "count": 0, "hostname": "0f9682f2f997", "storage": "redis"}
$ curl -fsS -X POST [http://127.0.0.1:8088/increment](http://127.0.0.1:8088/increment)
{"greeting": "Hello, another check!", "count": 1, "hostname": "0f9682f2f997", "storage": "redis"}
$ curl -fsS -X POST [http://127.0.0.1:8088/increment](http://127.0.0.1:8088/increment)
{"greeting": "Hello, another check!", "count": 2, "hostname": "0f9682f2f997", "storage": "redis"}

$ docker compose down
[+] down 3/3
 ✔ Container hw_3_own-app-1   Removed
 ✔ Container hw_3_own-redis-1 Removed
 ✔ Network hw_3_own_default   Removed

$ docker compose up -d --wait
[+] up 3/3
 ✔ Network hw_3_own_default   Created
 ✔ Container hw_3_own-redis-1 Healthy
 ✔ Container hw_3_own-app-1   Healthy

$ curl -fsS [http://127.0.0.1:8088/](http://127.0.0.1:8088/)
{"greeting": "Hello, another check!", "count": 2, "hostname": "b54b543a4614", "storage": "redis"}

$ docker compose down -v
[+] down 4/4
 ✔ Container hw_3_own-app-1   Removed
 ✔ Container hw_3_own-redis-1 Removed
 ✔ Volume hw_3_own_redis_data Removed
 ✔ Network hw_3_own_default   Removed
```

На `sqlite`:

```
$ docker compose up -d --build
[+] up 4/4
 ✔ Image hw_3_own-app       Built
 ✔ Network hw_3_own_default Created
 ✔ Volume hw_3_own_app_memo Created
 ✔ Container hw_3_own-app-1 Started

$ curl -fsS [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
{"greeting": "Hello, Compose!", "count": 0, "hostname": "356db748bdba", "storage": "sqlite"}
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, Compose!", "count": 1, "hostname": "356db748bdba", "storage": "sqlite"}
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, Compose!", "count": 2, "hostname": "356db748bdba", "storage": "sqlite"}

$ docker compose down
[+] down 2/2
 ✔ Container hw_3_own-app-1   Removed
 ✔ Network hw_3_own_default Removed

$ docker compose up -d
[+] up 2/2
 ✔ Network hw_3_own_default Created
 ✔ Container hw_3_own-app-1 Started

$ curl -fsS [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
{"greeting": "Hello, Compose!", "count": 2, "hostname": "5e348517c61c", "storage": "sqlite"}

$ docker compose down -v
[+] down 3/3
 ✔ Container hw_3_own-app-1   Removed
 ✔ Volume hw_3_own_app_memo Removed
 ✔ Network hw_3_own_default Removed
```

### 8 баллов — отдельное хранилище

1. По факту копия аналогичного задания на 6 баллов только на redis:

Команда и её вывод (если был)

```
$ curl -fsS [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
{"greeting": "Hello, Compose!", "count": 0, "hostname": "94c12f33753d", "storage": "redis"}
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, Compose!", "count": 1, "hostname": "94c12f33753d", "storage": "redis"}
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, Compose!", "count": 2, "hostname": "94c12f33753d", "storage": "redis"}

$docker compose down$ docker compose up -d --wait

$ curl -fsS [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
{"greeting": "Hello, Compose!", "count": 2, "hostname": "134de04721da", "storage": "redis"}
```

2. Остановка `redis` (`200` на `/healthz`, `503` на `/readyz` и `POST /increment`). На `/healthz` вернулось 'alive', что означает что сервер как раз таки и вернул (ответил) 200:

Команда и её вывод (если был)

```
$ docker compose stop redis
[+] stop 1/1
 ✔ Container hw_3_own-redis-1 Stopped

$ curl -fsS [http://127.0.0.1:8080/healthz](http://127.0.0.1:8080/healthz)
{"status": "alive"}
$ curl -fsS [http://127.0.0.1:8080/readyz](http://127.0.0.1:8080/readyz)
curl: (22) The requested URL returned error: 503
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
curl: (22) The requested URL returned error: 503
```

3. Повторный запуск `redis` без ручного перезапуска `app`. Данные сохранились, при повторном POST count увеличился до 3, что и требовалось:

Команда и её вывод (если был)

```
$ docker compose start redis
[+] start 1/1
 ✔ Container hw_3_own-redis-1 Started

$ curl -fsS [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
{"greeting": "Hello, Compose!", "count": 2, "hostname": "134de04721da", "storage": "redis"}
$ curl -fsS -X POST [http://127.0.0.1:8080/increment](http://127.0.0.1:8080/increment)
{"greeting": "Hello, Compose!", "count": 3, "hostname": "134de04721da", "storage": "redis"}
```

### 10 баллов — проверка восстановления

1. Проверка того, что приложение запускается от непривелигированного пользователся и доступно только для чтения, задали лимиты CPU/RAM контейнера `app`,
проверили что они успешно применились:

Команда и её вывод (если был)

```
$ docker compose exec app id
uid=10001 gid=10001 groups=10001

$ docker inspect hw_3_own-app-1 --format 'ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}'
ReadonlyRootfs=true Memory=268435456 NanoCpus=1000000000
```

2. Два последовательных запуска нашего Python-скрипта `scripts/check.py` с сохранением резервных копий redis во внешний файл
и удалением тест-проектов:

Команда и её вывод (если был)

```
$ python3 scripts/check.py
OK: /home/alechell/HW_3_own/hw3_check_1795452108.tar.gz

$ python3 scripts/check.py
OK: /home/alechell/HW_3_own/hw3_check_1795452158.tar.gz

$ ls -lh *.tar.gz
-rw------- 1 root root 489 Nov 23 19:42 hw3_check_1795452108.tar.gz
-rw------- 1 root root 485 Nov 23 19:43 hw3_check_1795452158.tar.gz
```
