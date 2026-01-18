import subprocess
import time
import os
import re
import sys

# Настройки путей
current_dir = os.path.dirname(os.path.abspath(__file__))
token_file_path = os.path.join(current_dir, "TOKEN")

# Читаем токен
try:
    with open(token_file_path, "r", encoding="utf-8") as f:
        GITHUB_TOKEN = f.read().strip()
    print("[OK] Токен подгружен.")
except FileNotFoundError:
    print(f"[!] Ошибка: Файл {token_file_path} не найден!"); sys.exit(1)

os.system('chcp 65001 > nul')

def update_github_beacon(url):
    """Обновляет ТОЛЬКО index.html и пушит его"""
    print(f"[*] Обновляю маяк на GitHub...")
    root_dir = os.path.abspath(os.path.join(current_dir, ".."))
    index_path = os.path.join(root_dir, "index.html")
    
    content = f'<html><head><script>window.location.href="{url}";</script></head></html>'
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    try:
        os.chdir(root_dir)
        # ВАЖНО: Мы пушим только один файл, чтобы не вывалить всю папку
        remote_url = f"https://{GITHUB_TOKEN}@github.com/hipmmiron/Auto_hosting_rugram.git"
        
        os.system('git add index.html') 
        os.system('git commit -m "Beacon Update"')
        os.system(f'git push {remote_url} main --force')
        print("[OK] Маяк обновлен. Остальные файлы не тронуты.")
    except Exception as e:
        print(f"[!] Ошибка Git: {e}")

def run():
    try:
        root_dir = os.path.abspath(os.path.join(current_dir, ".."))
        ssh_key = os.path.join(root_dir, 'ssh', 'ssh.txt')
        os.chdir(root_dir)

        print("[!] Очистка...")
        os.system('taskkill /f /im ssh.exe /t >nul 2>&1')

        # Запуск Flask
        server_script = os.path.join(root_dir, 'code', 'app.py')
        server = subprocess.Popen([sys.executable, server_script], 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL,
                                    cwd=os.path.join(root_dir, 'code'))
        print("[1/3] Flask запущен.")

        # Запуск SSH (nokey режим, чтобы не мучаться с Permission Denied)
        print("[2/3] Запуск SSH...")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -R 80:localhost:5555 nokey@localhost.run'
        tunnel = subprocess.Popen(ssh_cmd, shell=True, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT, 
                                   text=True, encoding='utf-8')

        print("[3/3] Ловим ссылку...")
        url = ""
        start_t = time.time()
        while time.time() - start_t < 25:
            line = tunnel.stdout.readline()
            if not line: continue
            match = re.search(r"https://[a-zA-Z0-9.-]+\.lhr\.life", line)
            if match:
                url = match.group(0)
                break

        if url:
            os.system('cls')
            print(f"СИСТЕМА ГОТОВА\nСсылка: {url}")
            os.system(f'echo {url} | clip')
            update_github_beacon(url)
        else:
            print("[!] Ссылка не найдена.")

        print("\nENTER для выхода...")
        input()
    finally:
        if 'server' in locals(): server.terminate()
        os.system('taskkill /f /im ssh.exe /t >nul 2>&1')

if __name__ == "__main__":
    run()