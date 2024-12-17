conda activate uavcpp

gunicorn -w 1 -b 0.0.0.0:5000 api:app > out.log 2>&1 &