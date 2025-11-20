FROM dipdup/dipdup:7.2

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .
