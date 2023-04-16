# FastAPI 실습

## version

- python 3.10.10
- fastAPI 0.95.0
- mysql 8.0.32

## Pyenv

### Pyenv 설치 (Macbook)

```bash
brew install pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

- 특정 버전 python 설치

    ```bash
    pyenv install <python-version>
    ```


## Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -

# local에 python3 없을 시 아래 명령어 실행 후 다시 다운로드 시도
pyenv global <python-version>
python --version    # 지정한 python-version으로 나오는지 확인

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

poetry --version
```

- poetry config 확인

    ```bash
    poetry config --list
    ```

- 가상환경 폴더 프로젝트 내부에 만들기
    > 위 명령어에서 virtualenvs.in-project와 virtualenvs.path의 default 값 확인할 수 있음
    
    ```bash
    poetry config virtualenvs.in-project true
    ```


## MySQL

```bash
docker pull mysql

docker run --name mysql -e MYSQL_ROOT_PASSWORD=<your_password> -d -p 3306:3306 mysql

docker exec -it mysql bash

mysql -uroot -p<your_password>
```

```sql
create database testdb;
```

## Config

```json
// core/config.json
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

## 실행 방법
> 3.10.10 version python 필요 (pyenv install 3.10.10)

```bash
git clone https://github.com/JngMkk/fastapi_test.git
cd fastapi_test
poetry shell
poetry install
```

```py
# core/config.json 없으면 실행 안 됨
python apps/main.py
```
