import os
import sys
from PIL import Image

# Чиним кодировку консоли
os.system('chcp 65001 > nul')

def convert_to_ico():
    print("--- КОНВЕРТЕР В .ICO ---")
    filename = input("Введите название файла (с расширением) или полный путь: ").strip('" ')

    if not os.path.exists(filename):
        print(f"[!] Файл '{filename}' не найден. Проверь название.")
        input("Нажми Enter, чтобы выйти..."); return

    try:
        # Открываем картинку
        img = Image.open(filename)
        
        # Генерируем имя для иконки (меняем расширение на .ico)
        base_name = os.path.splitext(filename)[0]
        output_name = f"{base_name}.ico"

        # Сохраняем. Для ICO стандартные размеры: 16x16, 32x32, 48x48, 256x256
        # Pillow сделает это автоматически при сохранении в ICO
        img.save(output_name, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        
        print(f"\n[OK] Готово! Иконка создана: {output_name}")
    except Exception as e:
        print(f"\n[!] Ошибка при конвертации: {e}")

    print("\nНажми ENTER для выхода...")
    input()

if __name__ == "__main__":
    convert_to_ico()