import io
import csv
from pyrogram import Client, filters
from pyrogram.types import Message
import logging
from config import PyrogramClient, SessionLocal
from models import Sell, Buy
from datetime import datetime, timedelta
from sqlalchemy import and_, func

logging.basicConfig(level=logging.INFO)

app = PyrogramClient

@app.on_message(filters.command ('help', '/'))
async def handle_help_command(client: Client, message: Message):
    help_string = """--- Help ----
    /sell {sell_qty} {sell_rate} - Adds a sell entry timestamped for today
    /buy {buy_qty} {buy_rate} - Adds a buy entry timestamped for today
    /profit {day-month-year} - Calculates profit for a given date
    /log - Gives you 5 latest buy and sell data
    /dump {day-month-year} - Gives you your DB as a CSV
    """

    message_user_id = message.from_user.id
    await message.reply(help_string, message_user_id)


@app.on_message(filters.command ('sell', '/'))
async def handle_sell_command(client: Client, message: Message):
    # help_string = "/sell {sell_qty} {sell_rate}"

    message_user_id = message.from_user.id
    command_array = message.command
    current_time = message.date # utc time
    maldives_time = current_time + timedelta(hours=5)

    command_array_len = len(command_array)
    if (command_array_len != 3):
        await message.reply("Invalid args: 3 expected", message_user_id)
        return

    sell_qty_str = command_array[1]
    sell_rate_str = command_array[2]

    try:
        sell_qty = float(sell_qty_str)
        sell_rate = float(sell_rate_str)
    except ValueError:
        await message.reply("Invalid args: could not be converted to floats", message_user_id)
        return

    db = SessionLocal()
    try:
        sell_record = Sell(qty=sell_qty, rate=sell_rate, user_id=message_user_id, deleted_at=None, created_at=maldives_time)
        db.add(sell_record)
        db.commit()
        db.refresh(sell_record)
        return_data = f"Sell ID: {sell_record.id}\nQty: {sell_record.qty}\nRate: {sell_record.rate}\nAction At: {maldives_time}\nTransaction Recorded."
    finally:
        db.close()

    # await app.send_message(chatid, table_data)
    await message.reply(return_data, message_user_id)

@app.on_message(filters.command ('buy', '/'))
async def handle_buy_command(client: Client, message: Message):
    # help_string = "/buy {buy_qty} {buy_rate}"

    message_user_id = message.from_user.id
    command_array = message.command
    current_time = message.date # utc time
    maldives_time = current_time + timedelta(hours=5)

    command_array_len = len(command_array)
    if (command_array_len != 3):
        await message.reply("Invalid args: 3 expected", message_user_id)
        return

    buy_qty_str = command_array[1]
    buy_rate_str = command_array[2]

    try:
        buy_qty = float(buy_qty_str)
        buy_rate = float(buy_rate_str)
    except ValueError:
        await message.reply("Invalid args: could not be converted to floats", message_user_id)
        return

    db = SessionLocal()
    try:
        buy_record = Buy(qty=buy_qty, rate=buy_rate, user_id=message_user_id, deleted_at=None, created_at=maldives_time)
        db.add(buy_record)
        db.commit()
        db.refresh(buy_record)
        return_data = f"Buy ID: {buy_record.id}\nQty: {buy_record.qty}\nRate: {buy_record.rate}\nAction At: {maldives_time}\nTransaction Recorded."
    finally:
        db.close()

    await message.reply(return_data, message_user_id)

@app.on_message(filters.command ('log', '/'))
async def handle_log_command(client: Client, message: Message):

    message_user_id = message.from_user.id
    limit = 5

    db = SessionLocal()
    try: 
        latest_sells = db.query(Sell).filter(and_(Sell.user_id == message_user_id, Sell.deleted_at.is_(None) )).order_by(Sell.id.desc()).limit(limit).all()
        latest_buys = db.query(Buy).filter(and_(Buy.user_id == message_user_id, Buy.deleted_at.is_(None) )).order_by(Buy.id.desc()).limit(limit).all()
    finally:
        db.close()

    return_data = "---Sell Log---\n"
    for sell in latest_sells:
        return_data+=f"Sell ID: {sell.id}, Qty: {sell.qty}, Rate: {sell.rate}\n"

    return_data += "\n---Buy Log---\n"
    for buy in latest_buys:
        return_data+=f"Buy ID: {buy.id}, Qty: {buy.qty}, Rate: {buy.rate}\n"

    await message.reply(return_data, message_user_id)

@app.on_message(filters.command ('profit', '/'))
async def handle_profit_command(client: Client, message: Message):
    # help_string = "/profit {day-month-year}"

    message_user_id = message.from_user.id
    command_array = message.command

    command_array_len = len(command_array)
    if (command_array_len != 2):
        await message.reply("Invalid args: 2 expected", message_user_id)
        return

    date_format = "%d-%m-%Y" 
    profit_calculation_date_str = command_array[1]

    try:
        profit_calculation_date = datetime.strptime(profit_calculation_date_str, date_format)
    except ValueError:
        await message.reply("Invalid args: could not be converted to floats", message_user_id)
        return
   
    db = SessionLocal()
    try:
        query_date = profit_calculation_date.date()
        sell_records = db.query(Sell).filter(
            and_(
                func.date(Sell.created_at) == query_date,
                Sell.user_id == message_user_id,
                Sell.deleted_at.is_(None) 
            )
        ).all()
        buy_records = db.query(Buy).filter(
            and_(
                func.date(Buy.created_at) == query_date,
                Buy.user_id == message_user_id,
                Buy.deleted_at.is_(None) 
            )
        ).all()
    finally:
        db.close()


    total_buy = 0.0
    for buy in buy_records:
        total_buy += buy.qty * buy.rate

    total_sell = 0.0
    for sell in sell_records:
        total_sell += sell.qty * sell.rate
        
    return_data = "---Profit Log---\n"
    return_data += f"Date: {query_date}\n"
    return_data += f"Total Buy: {total_buy}\n"
    return_data += f"Total Sell: {total_sell}\n"
    return_data += "------------------------\n"

    return_data += f"Profit: {total_sell - total_buy}\n"
    await message.reply(return_data, message_user_id)

@app.on_message(filters.command ('dump', '/'))
async def handle_dump_command(client: Client, message: Message):

    message_user_id = message.from_user.id
   
    db = SessionLocal()
    try:
        sell_records = db.query(Sell).filter(
            and_(
                Sell.user_id == message_user_id,
            )
        ).all()
        buy_records = db.query(Buy).filter(
            and_(
                Buy.user_id == message_user_id,
            )
        ).all()
    finally:
        db.close()


    # Create an in-memory text stream
    output = io.StringIO()

    # Create a CSV writer object
    csvwriter = csv.writer(output)

    header = ['id', 'created_at', 'user_id', 'qty', 'rate', 'deleted_at', 'type']
    csvwriter.writerow(header)

    for record in sell_records:
        row = [
            record.id,
            record.created_at,
            record.user_id,
            record.qty,
            record.rate,
            record.deleted_at, 
            'sell'
        ]
        csvwriter.writerow(row)

    for record in buy_records:
        row = [
            record.id,
            record.created_at,
            record.user_id,
            record.qty,
            record.rate,
            record.deleted_at, 
            'buy'
        ]
        csvwriter.writerow(row)

    # Get the CSV string from the in-memory text stream
    csv_data  = output.getvalue()
    
    # Close the in-memory text stream
    output.close()

    virtual_csv = io.BytesIO(csv_data.encode('utf-8'))

     # Send the CSV file as a document
    await client.send_document(
        chat_id=message.chat.id,
        document=virtual_csv,
        file_name="data.csv",
        caption="Your DB"
    )

if __name__ == '__main__':
    logging.info("Bot started")
    app.run() 

