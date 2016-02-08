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
            try:
                height_data = name_data.findNext('td').findNext('td').findNext('td').findNext('td')
                weight_data = height_data.findNext('td')
                url = 'http://www.basketball-reference.com/' + name_data.attrs['href'];

                player_page = get_soup(url)
                #subtracting the last 3 characters removes the extra dot that accompanies the position
                position = player_page.find(text='Position:').parent.next_sibling[1:-3]
                shooting_hand = player_page.find(text='Shoots:').parent.next_sibling[1:]

                player_data.append((
                    name_data.contents[0],
                    position,
                    convert_height_to_inches(height_data.contents[0]),
                    weight_data.contents[0],
                    shooting_hand
                ))
            except:
                #Exceptions usually arise when data is missing from BballRef (results in Nonetype)
                pass

    return player_data


def save_raw_player_data():
    raw_player_data = numpy.array(get_raw_player_data())
    numpy.save('raw_player_data.npy', raw_player_data)

def convert_height_to_inches(height):
    height_split = height.split("-")
    feet = int(height_split[0]) * 12
    return feet + int(height_split[1])

def get_statistics_for_height(position):
    raw_player_data = numpy.load('raw_player_data.npy')
    heights = []
    for data in raw_player_data:
        if position in data[1]:
            heights.append(int(data[2]))

    heights = numpy.array(heights)
    return [numpy.average(heights), numpy.std(heights)]

def get_basic_comparison_for_height(my_height, my_position, num_of_players):
    names = list()
    # arbitrarily define average PG height at local gym as 5'8
    local_height = 68
    height_data = get_statistics_for_height(my_position)
    converted_height = height_data[0] + (my_height - local_height)
    # path must be specified for this to work in Flask
    raw_player_data = numpy.load('/Users/dennisdeng2002/Documents/Programming/PycharmProjects/nba-comparison/raw_player_data.npy')

    for data in raw_player_data:
        points = 100 - numpy.abs(converted_height - int(data[2]))/height_data[1]
        names.append((data[0], points))

    names.sort(key=itemgetter(1), reverse=True)
    return names[0:num_of_players]

print(get_basic_comparison_for_height(78, "Point Guard", 10))