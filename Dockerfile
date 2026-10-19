FROM python:3.12-slim
WORKDIR /workspace
COPY . .
RUN pip install --no-cache-dir .
RUN useradd --create-home researcher && chown -R researcher:researcher /workspace
USER researcher
CMD ["novig-hqmm"]
