FROM dipdup/dipdup:7.5.10

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY fix_reward_field.py .
RUN python3 fix_reward_field.py

COPY . .
