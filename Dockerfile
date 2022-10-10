FROM dipdup/dipdup:6.1.2

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

