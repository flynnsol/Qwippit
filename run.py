from qwippit import create_app

app = create_app()

@app.template_filter()
def number_format(num):
    magnitude = 0
    while num >= 1000:
        num = float('{:.3g}'.format(num))
        magnitude += 1
        num /= 1000.0
    formatted_num = '{:,.1f}'.format(num) if 1000 <= num < 10000 else '{:f}'.format(num)
    return '{}{}'.format(formatted_num.rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


if __name__ == '__main__':
    app.run(debug=True)