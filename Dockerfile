FROM python:2.7

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY requirements.yml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY website/ 		./website/
COPY roles/ 		./roles/
COPY group_vars/ 	./group_vars/
COPY conf/ 		./conf/

COPY wsgi.py 		./wsgi.py
COPY app_main.py 	./app_main.py
COPY babel.cfg          ./babel.cfg
COPY ansible.cfg 	./ansible.cfg

COPY startup.sh         ./startup.sh
RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

RUN mkdir -p ./logs
RUN chmod 777 ./logs
VOLUME ./logs

RUN mkdir -p ./images
RUN chmod 777 ./images
VOLUME ./images

EXPOSE 443

RUN pybabel compile -d website/translations

CMD ["./startup.sh"]
