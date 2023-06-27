FROM dipdup/dipdup:6.5.7

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .
