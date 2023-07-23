import os
import psycopg2
import telegram
from dotenv import load_dotenv
from openpyxl import Workbookgit
from telegram.ext import Updater, Filters, MessageHandler

CHANNEL_ID = '@aster_task'

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)
def execute_postgresql_function(brand=None, model=None):
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        dbname='postgres',
        user=os.environ.get("user"),
        password=os.environ.get("password")
    )
    cursor = conn.cursor()
    if brand == None and model == None:
        query = 'SELECT * FROM get_car_info(Null, Null)'
    elif brand != None and model == None:
        query = 'SELECT * FROM get_car_info(' + f"'{brand}'" + ', Null)'
    else:
        query = 'SELECT * FROM get_car_info(' + f"'{brand}'" + f", '{model}')"

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def write_to_excel(result):
    workbook = Workbook()
    sheet = workbook.active

    for row_index, row_data in enumerate(result, start=1):
        for column_index, value in enumerate(row_data, start=1):
            sheet.cell(row=row_index, column=column_index, value=value)

    file_name = 'result.xlsx'
    workbook.save(file_name)

    return file_name


def send_file_to_channel(file_name):
    with open(file_name, 'rb') as file:
        bot.send_document(chat_id=CHANNEL_ID, document=file)


def user_message(update, context):
    if update.channel_post:
        channel_text = update.channel_post.text

    if channel_text == '/start':
        result = execute_postgresql_function()
        file_path = write_to_excel(result)
        send_file_to_channel(file_path)

    elif channel_text == '/help':
        string = """Excel file consist info like: Car brand, model, average price by brand + model,
max price by brand + model, min price by brand + model, 
number of records by brand + model, number of unique years by brand + model, 
the most popular year by brand + model.

Type /start to get all info about cars in 1 file.
Type "brand" to get all info about models of specific car.
Type "brand model" to get info about car brand and model."""
        bot.send_message(text=string, chat_id=CHANNEL_ID)
    else:
        if len(channel_text.split()) == 1:
            param1 = channel_text.split()[0]
            param1 = param1.capitalize()
            param2 = None

        elif len(channel_text.split()) == 2:
            param1, param2 = channel_text.split()[0], channel_text.split()[1]
            param1, param2 = param1.capitalize(), param2.capitalize()

        result = execute_postgresql_function(param1, param2)
        file_name = write_to_excel(result)
        send_file_to_channel(file_name)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.update, user_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
#bot.polling()
