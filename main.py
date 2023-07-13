from PIL import Image, ImageDraw, ImageFont
import csv
import telebot
import os

bot = telebot.TeleBot('6359853556:AAFZpHezFfJgUBinXkL4eSj1D2scSNUK2tY')

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
    filename = 'database.csv'
    temp_filename = 'temp_' + filename

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    count = 0

    with open(filename, 'r') as file, open(temp_filename, 'w', newline='') as temp_file:
        reader = csv.reader(file)
        writer = csv.writer(temp_file)

        for row in reader:
            if (row[0] == 'id'):
                writer.writerow(row)
                print(row)
            elif row[0] != id:
                writer.writerow(row)
                print(row)
            count+=1

    os.replace(temp_filename, filename)

generate_initial_grid()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Показать места', callback_data='show_seats'))
    bot.send_message(message.chat.id, 'Вы можете забронировать место на фильм ... в ...\nОсталось ... мест',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "show_seats")
def show_seats_handler(call):
    chat_id = call.message.chat.id
    photo_path = './generated_image.png'
    prepare_image().save(photo_path)

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))
    keyboard.add(telebot.types.InlineKeyboardButton('Мои места', callback_data='my_seats'))

    with open(photo_path, 'rb') as photo:
        bot.send_photo(chat_id, photo, reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "my_seats")
def show_seats_handler(call):
    chat_id = call.message.chat.id
    photo_path = './generated_image.png'
    prepare_image(id=chat_id).save(photo_path)

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))
    keyboard.add(telebot.types.InlineKeyboardButton('Отменить бронь', callback_data='close_booking'))

    with open(photo_path, 'rb') as photo:
        bot.send_photo(chat_id, photo, reply_markup=keyboard)
        bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "close_booking")
def show_seats_handler(call):
    chat_id = call.message.chat.id
    remove_rows_with_id(chat_id)

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Показать места', callback_data='show_seats'))
    keyboard.add(telebot.types.InlineKeyboardButton('Забронировать место', callback_data='start_booking'))

    bot.send_message(chat_id, 'Ваша бронь успешно отменена', reply_markup=keyboard)
    bot.answer_callback_query(call.id, show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data == "start_booking")
def book_row_handler(call):
    chat_id = call.message.chat.id

    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in range(1, 9):
        keyboard.add(telebot.types.InlineKeyboardButton(str(i), callback_data='book_row_' + str(i)))

    bot.send_message(chat_id, 'Выберите ряд', reply_markup=keyboard)
    bot.answer_callback_query(call.id, show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data[0:8] == "book_row")
def book_row_handler(call):
    chat_id = call.message.chat.id
    str_splitted = call.data.split('_')
    row = str_splitted[-1]

    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in range(1, 11):
        keyboard.add(telebot.types.InlineKeyboardButton(str(i), callback_data='book_column_' + row + '_' + str(i)))

    bot.send_message(chat_id, 'Выберите место в ряду ' + row, reply_markup=keyboard)
    bot.answer_callback_query(call.id, show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data[0:11] == "book_column")
def book_row_handler(call):
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


@bot.callback_query_handler(func=lambda call: call.data[0:15] == "confirm_booking")
def book_row_handler(call):
    chat_id = call.message.chat.id
    str_splitted = call.data.split('_')
    column = str_splitted[-1]
    row = str_splitted[-2]

    with open('./database.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, row, column])

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Посмотреть забронированные места', callback_data='show_seats'))

    bot.send_message(chat_id, 'Успешно!', reply_markup=keyboard)
    bot.answer_callback_query(call.id, show_alert=False)


bot.polling()