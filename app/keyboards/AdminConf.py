main_menu = {
            "Посмотреть записи": "view_rec", 
            "Удалить запись": "delete_rec",
            "Рассылка": "newsletter",
            "Добавить запись": "add_rec",
            "Обновить Фото": "update_media",
            "Обновить услуги": "update_service",
            "Удалить услугу": "delete_service",
            "Напомнить о записи": "remind",
            }


def answer(ans1, ans2):
    text = {
            "Да": ans1,
            "Нет": ans2,
        }
    return text


def answer_text(text_name):
    try:
        string = f"Ваши записи:\n"
        for text in text_name:
            string += f"{text}\n"
        return string
    except Exception as e:
        print(e)