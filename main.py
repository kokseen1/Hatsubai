import requests
import re
from datetime import datetime
import pickle
from matplotlib import pyplot as plt
from matplotlib import dates as mdates

PICKLE_FILENAME = "data_list.pkl"


def to_pickle(mylist):
    with open(PICKLE_FILENAME, "wb") as f:
        pickle.dump(mylist, f)


def from_pickle():
    with open(PICKLE_FILENAME, "rb") as f:
        mynewlist = pickle.load(f)
    return mynewlist


def get_html(url):
    return requests.get(url).text


def gsearch(query):
    return get_html(
        f"https://www.google.com/search?q={query}+carousell+site%3Ahttps%3A%2F%2Fwww.carousell.sg%2Fp%2F"
    )


def get_valid_urls(html):
    return re.findall(r'<a href="/url\?q=(https://www.carousell.sg/p/.+?)/&amp;', html)


def format_date(date_str):
    return datetime.strptime(date_str, "%Y/%m/%d").date()


def get_name_date_price(html):
    try:
        photo_url = re.findall(
            r"https://media.karousell.com/media/photos/products/.+?.jpg", html
        )
        date_str = "/".join(photo_url[0].split("/")[6:9])
        date = format_date(date_str)
        price_str = re.findall(r"S\$<!-- -->.+?</p><div>", html)
        price = price_str[0].strip("S$<!-- -->").rstrip("</p><div>").replace(",", "")
        name_str = re.findall(r'"name":".+?","offers"', html)
        name = name_str[0][8:-10]
    except IndexError:
        return
    else:
        return name, date, price


def gen_plot(data_list):
    data_list.sort(key=lambda x: x[1])
    x_values = [x[1] for x in data_list]
    y_values = [float(x[2]) for x in data_list]
    ax = plt.gca()
    formatter = mdates.DateFormatter("%Y/%m/%d")
    ax.xaxis.set_major_formatter(formatter)
    locator = mdates.DayLocator(interval=100)
    ax.xaxis.set_major_locator(locator)
    plt.title(data_list[0][0])
    plt.xlabel("Date")
    plt.ylabel("Price (S$)")
    plt.plot(x_values, y_values)
    plt.gcf().autofmt_xdate()
    plt.show()


def get_car_data(car_urls, verbose=False):
    if verbose:
        print(car_urls)
    data_list = []
    for url in car_urls:
        html = get_html(url)
        data = get_name_date_price(html)
        if not data:
            continue
        data += tuple([url])
        data_list.append(data)
        if verbose:
            print("{}\n{}\n${}\n{}\n".format(*data))
    return data_list


def main():
    html = gsearch("ier m9")
    # with open("gsearch.html", "r", encoding="utf8") as f:
    #     html = f.read()
    car_urls = get_valid_urls(html)
    # with open("car.html", "r", encoding="utf8") as f:
    # res = f.read()
    data_list = get_car_data(car_urls, True)
    to_pickle(data_list)
    gen_plot(data_list)


def debug():
    data_list = from_pickle()
    gen_plot(data_list)


if __name__ == "__main__":
    main()
    # debug()
