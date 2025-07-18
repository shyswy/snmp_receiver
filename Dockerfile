FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

# 컨테이너 내부에서 162포트(UDP), 8081포트(TCP) 열기
EXPOSE 8081
EXPOSE 162/udp

CMD ["./start.sh"]
