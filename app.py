from flask import Flask
from stores import falabella, ripley, paris

app = Flask(__name__)
app.register_blueprint(falabella.view)
app.register_blueprint(ripley.view)
app.register_blueprint(paris.view)


@app.route('/')
def hello_world():
    return 'Hello rata!'


if __name__ == '__main__':
    app.run()
