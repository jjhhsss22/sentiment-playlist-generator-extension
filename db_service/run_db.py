from __init__ import create_db

app = create_db()

if __name__ == "__main__":
    app.run(port=8003, debug=True)