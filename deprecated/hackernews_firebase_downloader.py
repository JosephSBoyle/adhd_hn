import requests
import threading
import time
import sqlite3

WRITER_SLEEP_TIME = 5 # FLush to db every n seconds.
main_conn = sqlite3.connect('hn_comments.db')
main_cursor = main_conn.cursor()

main_cursor.execute(
"""
    CREATE TABLE IF NOT EXISTS comments (
        id         INTEGER PRIMARY KEY,
        author     TEXT,
        text       TEXT,
        created_at TEXT
    )
""")
main_conn.commit()

result = main_cursor.execute("SELECT MAX(id) FROM comments;").fetchone()[0]
id_last_item_queried = int(result or 0)
target_rows = 1_000_000

print("LAST ID: ", id_last_item_queried)

url_template = "https://hacker-news.firebaseio.com/v0/item/%s.json"
records = []

def query_firebase(lock: threading.Lock) -> None:
    global id_last_item_queried
    while id_last_item_queried < target_rows:
        with lock:
            id_last_item_queried += 1
            url = url_template % id_last_item_queried

        resp = requests.get(url)
        json_ = resp.json()

        if json_["type"] == "comment" and (text := json_.get("text")) is not None:
            # Sometimes there can be no text, for reasons that escape me.
            with lock:
                records.append((id_last_item_queried, json_["by"], text, json_["time"]))

def write_to_db(lock: threading.Lock) -> None:
    global records

    conn = sqlite3.connect('hn_comments.db')
    cursor = conn.cursor()
    conn.commit()

    # Flush records to the db and empty the list of records.
    while (id_last_item_queried < target_rows) or records: # If records remain then flush em. XXX Maybe a race cond. here?
        with lock:
            if records:
                cursor.executemany(
                    """
                        INSERT INTO comments
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT (id) DO NOTHING;
                    """,
                    records,
                )
                conn.commit()
                records = []
        
        print(id_last_item_queried)
        time.sleep(WRITER_SLEEP_TIME)

lock = threading.Lock()
threads: list[threading.Thread] = []

t0 = time.time()
for i in range(128):
    t = threading.Thread(target=query_firebase, args=(lock,))
    t.start()
    threads.append(t)

# Start the writer thread.
writer = threading.Thread(target=write_to_db, args=(lock,))
writer.start()
threads.append(writer)


# Sync all threads.
for t in threads:
    t.join()

# Write any remaining rows to the db.
write_to_db(lock)
assert len(records) == 0

# Summarize execution.
t1 = time.time()
print("Total comments after: ", main_cursor.execute("""SELECT COUNT(*) FROM comments""").fetchone())
print("Total time: ", t1 - t0)
print("Requests per second:", target_rows / (t1 - t0))
