from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import data_scraper as ds


app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/basic_comparison', methods=['POST'])
def height():
    user_position = request.form['position']
    user_height = int(request.form['height'])

    data = (user_position, user_height)
    names = ds.compare(data)

    return render_template('basic_comparison.html', player_names = names)


if __name__ == '__main__':
    app.run()
