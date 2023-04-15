# FastAPI 실습

## MySQL
---

```bash
docker pull mysql

docker run --name mysql -e MYSQL_ROOT_PASSWORD=<your_password> -d -p 3306:3306 mysql

docker exec -it mysql bash

mysql -uroot -p<your_password>
```

```sql
create database testdb;
```

## Database Config
---

```json
// configs/config.json
{
    "DB": {
        "user": "<user>",
        "password": "<password>",
        "host": "localhost",
        "port": 3306,
        "database": "testdb"
    },
    "SECRET_KEY": "<secret_key>"
}
```
