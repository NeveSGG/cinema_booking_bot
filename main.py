from PIL import Image, ImageDraw, ImageFont
import csv
import telebot

bot = telebot.TeleBot('5976173556:AAFq5WaLR9st7Ki76QwytLqAC2TMRnQ96JM')

square_size = 80
image = Image.new("RGB", (square_size * 12, square_size * 9), "gray")
draw = ImageDraw.Draw(image)

lightFont = ImageFont.truetype("./Roboto-Light.ttf", 18)
headerFont = ImageFont.truetype("./Roboto-Medium.ttf", 22)
mediumFont = ImageFont.truetype("./Roboto-Medium.ttf", 18)

def generate_initial_grid():
    global draw
    global square_size
    global headerFont

    for i in range(10):
        for j in range(8):
            x1 = (i + 1) * square_size
            y1 = (j + 1) * square_size
            x2 = x1 + square_size
            y2 = y1 + square_size

            draw.rectangle([x1, y1, x2, y2], fill="gray", outline="black")

    draw.text((square_size - 35, square_size // 2), 'ряд', fill="black", font=headerFont, anchor="mm")
    draw.text((6 * square_size + 5, square_size // 2), 'ЭКРАН', fill="black", font=headerFont, anchor="mm")


def fill_item(draw_el, a, b, color='red'):
    global square_size

    x1 = int(b) * square_size + 1
    y1 = int(a) * square_size + 1
    x2 = x1 + square_size - 1
    y2 = y1 + square_size - 1

    draw_el.rectangle([x1, y1, x2, y2], fill=color, outline="black")

def prepare_image(id = False):
    global image
    global square_size
    global lightFont
    global mediumFont

    res_image = image
    new_draw = ImageDraw.Draw(res_image)

    with open('database.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            x = int(row[1])
            y = int(row[2])
            if (id != False) & (str(id) == str(row[0])):
                fill_item(new_draw, x, y, 'blue')
            else:
                fill_item(new_draw, x, y)

    for j in range(8):
        for i in range(12):
            x1 = i * square_size
            y1 = (j + 1) * square_size
            x2 = x1 + square_size
            y2 = y1 + square_size

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            if i == 0:
                new_draw.text((center_x, center_y), str(j + 1), fill="black", font=lightFont, anchor="mm")
            elif i == 11:
                new_draw.text((center_x, center_y), str(j + 1), fill="black", font=lightFont, anchor="mm")
            else:
                new_draw.text((center_x, center_y), str(i), fill="black", font=mediumFont, anchor="mm")
    return res_image

def remove_rows_with_id(id):
    with open('database.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

        data = [row for row in data if row[0] != str(id)]
        generate_initial_grid()

        print(data)

        with open('database.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

def count_free_seats():
    with open('database.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

        return 81-len(data)

generate_initial_grid()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Показать места', callback_data='show_seats'))
        keyboard.add(telebot.types.InlineKeyboardButton('Информация о фильме', callback_data='movie_info'))

        free_seats = count_free_seats()

        bot.send_message(message.chat.id, 'Вы можете забронировать место на фильм на 16:00\nОсталось '+str(free_seats)+' мест',
                         reply_markup=keyboard)
    except:
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             message.chat.username) + ' начать диалог с ботом. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             message.chat.username) + ' начать диалог с ботом. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "movie_info")
def show_seats_handler(call):
    try:
        chat_id = call.message.chat.id

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Посмотреть свободные места', callback_data='show_seats'))
        keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))

        bot.send_message(chat_id, 'Где: Омск, 10 лет Октября, 195Б\nКогда: 22.07.2023, начало в 16:00\nСколько стоит: вход 100 рублей\nКак забронировать место: по телефону 89994568133 или в этом боте\nКак называется фильм: это пока что секрет :)', reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' показать информацию о фильме. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' показать информацию о фильме. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "show_seats")
def show_seats_handler(call):
    try:
        chat_id = call.message.chat.id
        photo_path = './generated_image.png'
        prepare_image().save(photo_path)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))
        keyboard.add(telebot.types.InlineKeyboardButton('Мои места', callback_data='my_seats'))

        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, reply_markup=keyboard)
            bot.answer_callback_query(call.id, show_alert=False)
    except:
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' отобразить все места. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' отобразить все места. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "my_seats")
def show_seats_handler(call):
    try:
        chat_id = call.message.chat.id
        photo_path = './generated_image.png'
        prepare_image(id=chat_id).save(photo_path)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))
        keyboard.add(telebot.types.InlineKeyboardButton('Отменить бронь', callback_data='close_booking'))

        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, reply_markup=keyboard)
            bot.answer_callback_query(call.id, show_alert=False)
    except:
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' отобразить его места. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' отобразить его места. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "close_booking")
def show_seats_handler(call):
    try:
        chat_id = call.message.chat.id
        remove_rows_with_id(chat_id)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Показать места', callback_data='show_seats'))
        keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))

        bot.send_message(chat_id, 'Ваша бронь успешно отменена', reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' отменить бронь. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' отменить бронь. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "start_booking")
def book_row_handler(call):
    try:
        chat_id = call.message.chat.id

        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(1, 9):
            keyboard.add(telebot.types.InlineKeyboardButton(str(i), callback_data='book_row_' + str(i)))

        bot.send_message(chat_id, 'Выберите ряд', reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' начать бронирование. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' начать бронирование. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data[0:8] == "book_row")
def book_row_handler(call):
    try:
        chat_id = call.message.chat.id
        str_splitted = call.data.split('_')
        row = str_splitted[-1]

        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(1, 11):
            keyboard.add(telebot.types.InlineKeyboardButton(str(i), callback_data='book_column_' + row + '_' + str(i)))

        bot.send_message(chat_id, 'Выберите место в ряду ' + row, reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        str_splitted = call.data.split('_')
        row = str_splitted[-1]
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' выбрать ряд ' + row + '. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' выбрать ряд ' + row + '. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data[0:11] == "book_column")
def book_row_handler(call):
    try:
        chat_id = call.message.chat.id
        str_splitted = call.data.split('_')
        column = str_splitted[-1]
        row = str_splitted[-2]

        with open('database.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)

            for stroka in reader:
                if (stroka[1] == row) & (stroka[2] == column):
                    bot.send_message(chat_id,
                                     'Это место уже забронировано, попробуйте другое')
                    bot.answer_callback_query(call.id, show_alert=False)
                    return

        keyboard = telebot.types.InlineKeyboardMarkup()
        print(row, column)
        keyboard.add(telebot.types.InlineKeyboardButton('Да, хочу!', callback_data='confirm_booking_' + row + '_' + column))
        keyboard.add(telebot.types.InlineKeyboardButton('Отменить', callback_data='show_seats'))

        bot.send_message(chat_id, 'Вы действительно хотите забронировать место ' + column + ' в ряду ' + row + '?',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        str_splitted = call.data.split('_')
        column = str_splitted[-1]
        row = str_splitted[-2]
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' забронировать место ' + column + ' в ряду ' + row + '. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' забронировать место ' + column + ' в ряду ' + row + '. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data[0:15] == "confirm_booking")
def book_row_handler(call):
    try:
        chat_id = call.message.chat.id
        str_splitted = call.data.split('_')
        column = str_splitted[-1]
        row = str_splitted[-2]

        with open('./database.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([chat_id, row, column])

        bot.send_message('1396965518',
                         'Пользователь ' + str(call.message.chat.first_name) + ' ' + str(
                             call.message.chat.last_name) + ' под ником @' + str(
                             call.message.chat.username) + ' забронировал место ' + column + ' в ряду ' + row + '.')

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Посмотреть забронированные места', callback_data='show_seats'))

        bot.send_message(chat_id, 'Успешно! У вас есть возможность оплатить поход на фильм (100 руб) заранее. Для этого вы можете сделать перевод с пометкой "Кино" на Сбер по номеру телефона 89994568133 (Лев)', reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)
    except:
        str_splitted = call.data.split('_')
        column = str_splitted[-1]
        row = str_splitted[-2]
        bot.send_message('1396965518',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' забронировать место ' + column + ' в ряду ' + row + '. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message('451474085',
                         'Произошла ошибка при попытке пользователя @' + str(
                             call.message.chat.username) + ' забронировать место ' + column + ' в ряду ' + row + '. Разработчик тоже в курсе произошедшего',
                         reply_markup=keyboard)
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка в работе бота. Попробуйте удалить историю диалога и написать команду /start. Если это не помогло, обратитесь за билетами по телефону 89994568133 (Лев)',
                         reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)


bot.polling()
