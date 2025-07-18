from flask import Flask, render_template_string
import os
import re
from collections import defaultdict

app = Flask(__name__)

LOG_FILE = 'received_traps.log'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>📡 SNMP Trap Viewer</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f5f6fa;
            color: #2f3640;
            padding: 20px;
        }
        h1 {
            text-align: center;
        }
        /* 탭 스타일 */
        .tabs {
            display: flex;
            border-bottom: 2px solid #00a8ff;
            margin-bottom: 20px;
            cursor: pointer;
            flex-wrap: wrap;
        }
        .tab {
            padding: 10px 20px;
            background: #d6eaff;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 6px;
            font-weight: bold;
            color: #0077cc;
            user-select: none;
        }
        .tab.active {
            background: #00a8ff;
            color: white;
            box-shadow: 0 -3px 8px rgba(0,168,255,0.7);
        }
        /* 시간별 박스 */
        .hour-group {
            margin-bottom: 30px;
            padding-left: 8px;
            border-left: 4px solid #00a8ff;
        }
        .hour-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #0077cc;
            font-size: 1.1em;
        }
        .trap {
            background: #ffffff;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .oid {
            margin-left: 10px;
            font-family: monospace;
            color: #40739e;
        }
        .value-line {
            margin-left: 10px;
            font-family: monospace;
            background: #e1f5fe;
            padding: 8px;
            border-radius: 8px;
            color: #0c5460;
            border-left: 4px solid #00a8ff;
            font-weight: bold;
            margin-top: 10px;
        }
        .meta {
            font-size: 13px;
            color: #888;
        }
        /* 탭별 컨텐츠 숨김 처리 */
        .trap-group {
            display: none;
        }
        .trap-group.active {
            display: block;
        }
    </style>
</head>
<body>
    <h1>📡 SNMP Trap Viewer</h1>

    {% if grouped_traps %}
        <div class="tabs" id="tabs">
            {% for date in grouped_traps.keys() %}
                <div class="tab" data-date="{{ date }}">{{ date }}</div>
            {% endfor %}
        </div>

        {% for date, hours in grouped_traps.items() %}
            <div class="trap-group" id="group-{{ date }}">
                {% for hour, traps in hours.items() %}
                    <div class="hour-group">
                        <div class="hour-title">{{ hour }} 시</div>
                        {% for trap in traps %}
                            <div class="trap">
                                <div class="meta">🕒 {{ trap.timestamp }}</div>
                                {% for i in range(trap.data|length) %}
                                    {% if i == trap.data|length - 1 %}
                                        <div class="value-line">📌 Value: {{ trap.data[i] }}</div>
                                    {% else %}
                                        <div class="oid">🔹 {{ trap.data[i] }}</div>
                                    {% endif %}
                                {% endfor %}
                            </div>
                        {% endfor %}
                    </div>
                {% endfor %}
            </div>
        {% endfor %}
    {% else %}
        <p>No trap data available.</p>
    {% endif %}

    <script>
        const tabs = document.querySelectorAll('.tab');
        const groups = document.querySelectorAll('.trap-group');

        function activateTab(date) {
            tabs.forEach(tab => {
                tab.classList.toggle('active', tab.dataset.date === date);
            });
            groups.forEach(group => {
                group.classList.toggle('active', group.id === 'group-' + date);
            });
        }

        if(tabs.length > 0) {
            activateTab(tabs[0].dataset.date);
        }

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                activateTab(tab.dataset.date);
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    traps = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        current_trap = None
        for line in lines:
            line = line.strip()
            if "📡 Received new Trap message" in line:
                if current_trap:
                    traps.append(current_trap)
                current_trap = {"timestamp": "", "data": []}
            elif "OID:" in line:
                if current_trap:
                    match = re.search(r'OID: (.+?) \| Type: (.+?) \| Value: (.+)', line)
                    if match:
                        oid, dtype, val = match.groups()
                        current_trap["data"].append(f"{oid} → ({dtype}) {val}")
            elif line.startswith("20") and current_trap and not current_trap["timestamp"]:
                current_trap["timestamp"] = line

        if current_trap:
            traps.append(current_trap)

    grouped = defaultdict(lambda: defaultdict(list))
    for t in traps:
        date_str = t['timestamp'][:10] if t['timestamp'] else 'Unknown'      # YYYY-MM-DD
        hour_str = t['timestamp'][11:13] if t['timestamp'] else '??'          # HH
        grouped[date_str][hour_str].append(t)

    # 날짜 역순, 시간 오름차순 정렬
    grouped_sorted = dict(sorted(grouped.items(), reverse=True))
    for date in grouped_sorted:
        grouped_sorted[date] = dict(sorted(grouped_sorted[date].items()))

    return render_template_string(HTML_TEMPLATE, grouped_traps=grouped_sorted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
