#User
main_menu = {
            "Записаться": "zap", 
            "Настройки": "settings",
            "Отменить запись": "antizap",
            "Прайс лист": "price_list",
            "Мои записи": "myzap",
            }

settings = {
            "Изменить имя": "change_name",
            "Удалить профиль": "change_del",
            "Отмена": "change_0",
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
