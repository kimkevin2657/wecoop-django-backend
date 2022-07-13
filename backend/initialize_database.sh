read -p "연결된 데이터베이스의 데이터 및 마이그레이션 파일이 삭제 후 재생성됩니다. 정말로 삭제하시겠습니까? (yes/n) " RESP
if [ "$RESP" = "yes" ]; then
  venv/bin/python manage.py dumpdata -e auth -e contenttypes -e sessions -e admin --indent 2 > db.json
  venv/bin/python manage.py showmigrations | grep -G "^[^ ]" | xargs -I {app} python manage.py migrate {app} zero
  find ./app -path "*/migrations/__pycache__*" -delete
  find ./app -path "*/migrations/*.pyc" -delete
  find ./app -path "*/migrations/*.py" -not -name "__init__.py" -delete
  venv/bin/python manage.py makemigrations
  venv/bin/python manage.py migrate
  venv/bin/python manage.py loaddata db.json
#  venv/bin/python manage.py showmigrations | grep -G "^[^ ]" | xargs -I {app} python manage.py loaddata app/{app}/fixtures/initial_data.json
else
  echo "Cancelled"
fi
