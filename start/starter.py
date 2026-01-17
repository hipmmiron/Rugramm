import subprocess
import time
import os
import re
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
token_file_path = os.path.join(current_dir, "TOKEN")

try:
    with open(token_file_path, "r", encoding="utf-8") as f:
        # Теперь в GITHUB_TOKEN реально лежит твой секретный ключ
        GITHUB_TOKEN = f.read().strip()
    print("[OK] Токен успешно считан из скрытого файла.")
except FileNotFoundError:
    print(f"[!] Ошибка: Файл {token_file_path} не найден!")
    sys.exit(1)# Чиним кодировку
os.system('chcp 65001 > nul')

def run():
    try:
        # Определяем пути
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(script_dir, ".."))
        os.chdir(root_dir)
        
        print(f"[*] Корень проекта: {root_dir}")

        # 1. Безопасная очистка (убиваем только SSH, сервер Flask добьем позже)
        print("[!] Очистка старых туннелей...")
        os.system('taskkill /f /im ssh.exe /t >nul 2>&1')
        # Не убиваем python.exe целиком, иначе стартер закроется сам!
        time.sleep(1)

        # 2. Проверка файлов
        server_script = os.path.join(root_dir, 'code', 'app.py')
        ssh_key = os.path.join(root_dir, 'ssh', 'ssh.txt')

        if not os.path.exists(server_script):
            print(f"[!] ОШИБКА: Файл {server_script} не найден!")
            input(); return

        # 3. Запуск сервера Flask
        print("[1/3] Запуск сервера Flask...")
        # Используем отдельный флаг, чтобы не дублировать процессы
        server = subprocess.Popen([sys.executable, server_script], 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL,
                                    cwd=os.path.join(root_dir, 'code'))
        
        # Счётчик
        for i in range(3, 0, -1):
            print(f"\r[*] Ожидание: {i} сек... ", end="", flush=True)
            time.sleep(1)
        print("\n[OK] Сервер запущен.")

        # 4. SSH Туннель
        print("[2/3] Запуск SSH...")
        ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i "{ssh_key}" -R 80:localhost:5555 localhost.run'
        tunnel = subprocess.Popen(ssh_cmd, shell=True, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT, 
                                   text=True, encoding='utf-8', errors='ignore')

        print("[3/3] Перехват ссылки...")
        url = ""
        start_time = time.time()
        
        while time.time() - start_time < 15:
            line = tunnel.stdout.readline()
            if not line: continue
            
            print(".", end="", flush=True)
            match = re.search(r"https://[a-zA-Z0-9.-]+\.lhr\.life", line)
            if match:
                url = match.group(0)
                break

        # 5. Результат
        os.system('cls')
        print("==================================================")
        print("          RUGRAMM СИСТЕМА ЗАПУЩЕНА")
        print("==================================================")
        
        if url:
            print(f"\nВАША ССЫЛКА: {url}")
            os.system(f'echo {url} | clip')
            print("\n(Скопировано в буфер обмена!)")
        else:
            print("\n[!] Не удалось поймать ссылку.")
            print("Попробуй запустить еще раз или проверь ssh.txt")

        print("\nДля закрытия нажмите ENTER (это выключит сервер)")
        input()

    except Exception as e:
        print(f"\n[!!!] Ошибка: {e}")
        input()
    finally:
        # Принудительно выключаем Flask при выходе
        if 'server' in locals():
            server.terminate()
        os.system('taskkill /f /im ssh.exe /t >nul 2>&1')

if __name__ == "__main__":
    run()