import os, uvicorn
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

PORT=8082

# Load enviroment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

print(DB_URL)

conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/temp")
def temp():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM messages")
        messages = cur.fetchall()
    return messages


# get all rooms
@app.get("/rooms")
def get_rooms():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM hotel_rooms 
            ORDER BY room_number""")
        rooms = cur.fetchall()
        return rooms
    
# get one room
@app.get("/rooms/{id}")
def get_one_room(id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM hotel_rooms WHERE id = %s", [id])
        #cur.execute("SELECT * FROM hotel_rooms WHERE id = %s", (id,)) # tuple
        #cur.execute("SELECT * FROM hotel_rooms WHERE id = %(id)s", {"id": id})
        room = cur.fetchone()
        if not room: 
            return { "msg": "Room not found"}
        return room

# Get all booking
@app.get("/bookings")
def get_bookings():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM hotel_bookings
            ORDER BY datefrom""")
        bookings = cur.fetchall()
        return bookings

# Create booking
@app.post("/bookings")
def create_booking(booking: Booking):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO hotel_bookings (
            guest_id,
            room_id,
            datefrom,
            dateto
        ) VALUES (
            %s, %s, %s, %s
        ) RETURNING id
        """, [
            booking.guest_id, 
            booking.room_id, 
            booking.datefrom, 
            booking.dateto
        ])
        new_id = cur.fetchone()['id']

    return { "msg": "booking created!", "id": new_id}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        ssl_keyfile="/etc/letsencrypt/privkey.pem",
        ssl_certfile="/etc/letsencrypt/fullchain.pem",
    )