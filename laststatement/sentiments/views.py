# coding: utf-8

from flask import (Blueprint, render_template)

sentiments = Blueprint('sentiments', __name__,
                       template_folder='templates',
                       static_folder='static')


@sentiments.route('/', methods=['GET', 'OPTIONS'])
def index():
    return render_template('sentiments/sentiments.html')
