FROM python:3.9-bullseye

WORKDIR /app/

COPY commons.py maildown.py requirements.txt /app/

RUN python3 -m venv /app/venv

RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh

RUN chmod a+x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
