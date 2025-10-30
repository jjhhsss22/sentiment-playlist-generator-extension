from __init__ import create_app

app = create_app()

if __name__ == "__main__":  # so that it's only ran as a script not a module (dunder needs to match).
    app.run(port=5000, debug=True)