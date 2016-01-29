from bs4 import BeautifulSoup
from operator import itemgetter
import requests, string, numpy


def get_soup(url):
    try:
        r = requests.get(url)
    except:
        print("Invalid url")

    return BeautifulSoup(r.text, "html.parser")


def get_raw_player_data():

    player_data = []
    # Since b-ball reference organizes players by the first letter of last name
    # get all pages by iterating through all letters in alphabet
    for letter in string.ascii_lowercase:
        letter_page = get_soup('http://www.basketball-reference.com/players/%s/' % letter)
        # Active players are denoted in bold - html: strong
        active_players_names = letter_page.findAll('strong')

        # Example HTML
        #    <tr  class="">
        #    <td align="left" ><a href="/players/a/abdulka01.html">Kareem Abdul-Jabbar</a>*</td>
        #    <td align="right" >1970</td>
        #    <td align="right" >1989</td>
        #    <td align="center" >C</td>
        #    <td align="right"  csk="86.0">7-2</td>
        #    <td align="right" >225</td>
        #    <td align="left"  csk="19470416"><a href="/friv/birthdays.cgi?month=4&amp;day=16">April 16, 1947</a></td>
        #    <td align="left" ><a href="/friv/colleges.cgi?college=ucla">University of California, Los Angeles</a></td>
        #    </tr>

        for names in active_players_names:
            name_data = names.children.__next__()
            position_data = name_data.findNext('td').findNext('td').findNext('td')
            height_data = position_data.findNext('td')
            weight_data = height_data.findNext('td')

            player_data.append((name_data.contents[0],
                            #url to player profile page
                            'http://www.basketball-reference.com/' + name_data.attrs['href'],
                            position_data.contents[0],
                            height_data.contents[0],
                            weight_data.contents[0]
                            ))

    return player_data


def save_raw_player_data():
    raw_player_data = numpy.array(get_raw_player_data())
    numpy.save('raw_player_data.npy', raw_player_data)


def get_basic_comparison(height, num):
    names = list()
    # path must be specified for this to work in Flask
    raw_player_data = numpy.load('/Users/dennisdeng2002/Documents/Programming/PycharmProjects/nba-comparison/raw_player_data.npy')
    for data in raw_player_data:
        if data[3] == height:
            names.append([data[0], 1])
        else:
            names.append([data[0], 0])

    names.sort(key=itemgetter(1), reverse=True)
    return names[0:num]