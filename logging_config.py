import logging

def setup_logger():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log"),  # Логи записываются в файл
            logging.StreamHandler()  # Логи выводятся в консоль
        ]
    )
    return logging.getLogger(__name__)