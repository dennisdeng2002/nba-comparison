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
    user_height = request.form['height']
    names = ds.get_basic_comparison(user_height, 10)
    return render_template('basic_comparison.html', player_names = names)


if __name__ == '__main__':
    app.run()
