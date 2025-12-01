from __init__ import create_ms

app = create_ms()

if __name__ == "__main__":
    app.run(port=8002, debug=True)