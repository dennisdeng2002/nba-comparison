from bs4 import BeautifulSoup
from operator import itemgetter
import requests, string, numpy

raw_data_path = "/Users/dennisdeng2002/Documents/Programming/PycharmProjects/nba-comparison/raw_player_data.npy"
starting_points = 100
position_value_weight = 1

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
    numpy.save(raw_data_path, raw_player_data)


def convert_height_to_inches(height):
    height_split = height.split("-")
    feet = int(height_split[0]) * 12
    return feet + int(height_split[1])


def get_statistics_for_height(position, raw_player_data):
    heights = []
    for data in raw_player_data:
        if position in data[1]:
            heights.append(int(data[2]))

    heights = numpy.array(heights)
    return [numpy.average(heights), numpy.std(heights)]


def get_statistics_for_weight(position, raw_player_data):
    weights = []
    for data in raw_player_data:
        if position in data[1]:
            weights.append(int(data[3]))

    weights = numpy.array(weights)
    return [numpy.average(weights), numpy.std(weights)]


def get_player_names(my_data):

    my_position, my_height, my_weight = my_data[0], my_data[1], my_data[2]

    # path must be specified for this to work in Flask
    raw_player_data = numpy.load(raw_data_path)
    comparison_data = list()

    comparison_data = compare_position(my_position, comparison_data, raw_player_data)
    comparison_data = compare_height(my_position, my_height, comparison_data, raw_player_data)
    comparison_data = compare_height(my_position, my_weight, comparison_data, raw_player_data)

    comparison_data.sort(key=itemgetter(1), reverse=True)

    return comparison_data


def compare_position(my_position, comparison_data, raw_player_data):

    for data in raw_player_data:
        if my_position == data[1]:
            comparison_data.append([data[0], starting_points])
        else:
            points = starting_points - position_value_weight
            comparison_data.append([data[0], points])

    return comparison_data


def compare_height(my_position, my_height, comparison_data, raw_player_data):

    # arbitrarily define average PG height at local gym as 5'8
    local_height = 68

    average_height = get_statistics_for_height(my_position, raw_player_data)
    converted_height = average_height[0] + (my_height - local_height)

    for i in range(0, len(comparison_data)):
        points = comparison_data[i][1] - numpy.abs(converted_height - int(raw_player_data[i][2]))/average_height[1]
        comparison_data[i][1] = points

    return comparison_data


def compare_weight(my_position, my_weight, comparison_data, raw_player_data):

    local_weight = 150

    average_weight = get_statistics_for_weight(my_position, raw_player_data)
    converted_weight = average_weight[0] + (my_weight - local_weight)

    for i in range(0, len(comparison_data)):
        points = comparison_data[i][1] - numpy.abs(converted_weight - int(raw_player_data[i][2]))/average_weight[1]
        comparison_data[i][1] = points

    return comparison_data


data = ["Point Guard", 62, 180]
print(get_player_names(data))