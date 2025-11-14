FROM dipdup/dipdup:7

WORKDIR /app

COPY --chown=dipdup:dipdup . /app

USER root
RUN mkdir -p /app/registrydao/abi && \
    chown -R dipdup:dipdup /app && \
    pip install httpx && \
    python /app/fix_reward_field.py

USER dipdup
