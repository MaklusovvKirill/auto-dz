from playwright.sync_api import sync_playwright
from loguru import logger
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
logger.info("Запуск браузера...")

with sync_playwright() as p:
    logger.add("file.log",
               format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
               rotation="3 days", backtrace=True, diagnose=True)

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://journal.top-academy.ru/")
    logger.info("Страница загружена")

    page.wait_for_selector('input[name="username"]', timeout=10000)

    page.fill('input[name="username"]', LOGIN)
    page.fill('input[name="password"]', PASSWORD)
    logger.info("Данные для входа введены")

    page.click('button[type="submit"]')
    logger.info("Кнопка входа нажата")

    page.wait_for_timeout(5000)

    logger.success(f"Вход выполнен! Текущий URL: {page.url}")

    page.goto("https://journal.top-academy.ru/main/homework/page/index")

    # Ждем загрузки страницы с домашними заданиями
    page.wait_for_selector('.homework-item', timeout=10000)
    logger.info("Страница с домашними заданиями загружена")

    # Ищем все элементы с домашними заданиями
    homework_items = page.query_selector_all('.homework-item')
    logger.info(f"Найдено элементов с домашними заданиями: {len(homework_items)}")

    # Проходим по каждому домашнему заданию
    for index, homework_item in enumerate(homework_items):
        try:
            # Проверяем, есть ли кнопка загрузки выполненного задания
            upload_button = homework_item.query_selector('.upload-file img[src*="upload.png"]')
            
            if upload_button:
                # Получаем информацию о предмете для логирования
                subject_element = homework_item.query_selector('.name-spec')
                subject_name = subject_element.inner_text() if subject_element else f"Задание {index + 1}"
                
                logger.info(f"Найдена кнопка загрузки для: {subject_name}")
                
                # Наводим курсор на элемент, чтобы показать кнопки
                homework_item.hover()
                page.wait_for_timeout(1000)  # Ждем появления кнопок
                
                # Кликаем на кнопку загрузки
                upload_button.click()
                logger.info(f"Клик на кнопку загрузки для: {subject_name}")
                
                # Ждем появления модального окна с формой загрузки
                page.wait_for_selector('label[for="file0"]', timeout=10000)
                logger.info("Модальное окно загрузки появилось")
                
                # Кликаем на элемент "Кликните здесь"
                file_label = page.query_selector('label[for="file0"]')
                if file_label:
                    file_label.click()
                    logger.info("Клик на область загрузки файла выполнен")
                    
                    # Загружаем файл pic.jpg
                    file_path = os.path.join(os.path.dirname(__file__), 'pic.jpg')
                    
                    if os.path.exists(file_path):
                        # Находим input для загрузки файла и загружаем картинку
                        file_input = page.query_selector('input[type="file"][id="file0"]')
                        if file_input:
                            file_input.set_input_files(file_path)
                            logger.success(f"Файл {file_path} загружен для: {subject_name}")
                            
                            # Ждем немного чтобы увидеть результат
                            page.wait_for_timeout(3000)
                            
                            # Можно добавить подтверждение загрузки, если нужно
                            # submit_button = page.query_selector('button[type="submit"]')
                            # if submit_button:
                            #     submit_button.click()
                            #     logger.info("Файл отправлен")
                            
                        else:
                            logger.error("Не найден input для загрузки файла")
                    else:
                        logger.error(f"Файл {file_path} не найден. Убедитесь, что pic.jpg находится в той же папке, что и скрипт.")
                else:
                    logger.error("Элемент 'Кликните здесь' не найден")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке задания {index + 1}: {e}")|
            
            
            
            
            

    logger.info("Обработка домашних заданий завершена")

    input("Все операции завершены. Нажмите Enter для закрытия...")

    browser.close()
