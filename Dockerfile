FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

#RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
#RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["panel", "serve", "/code/app.py", "--address", "0.0.0.0", "--port", "7860", "--allow-websocket-origin", "mchiovaro-stock-assistant.hf.space"]