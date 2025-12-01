from __init__ import create_auth

app = create_auth()

if __name__ == "__main__":
    app.run(port=8004, debug=True)