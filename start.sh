#!/bin/bash
# 하나의 컨테이너에서 두 프로세스 실행 (백그라운드 + 포그라운드)

# receiver.py를 백그라운드로 실행 (로그는 별도 파일로)
python3 receiver.py &

# Flask 웹서버 실행 (포그라운드)
python3 web-monitor.py
