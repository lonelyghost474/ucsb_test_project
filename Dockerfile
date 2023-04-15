FROM python:3

WORKDIR /ucsb_test

COPY ./requirements.txt .

COPY ./app .

RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt


ENTRYPOINT ["python","./sw_grab.py"]