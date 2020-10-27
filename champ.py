#! /usr/bin/env python3
try:
    import requests
    from bs4 import BeautifulSoup
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
except:
    print('Missing imports')
    exit()

def fetch_champs():
    championList = []
    # Fetching and population of list for all current champions
    response = requests.get("https://u.gg/lol/champions")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        champs = soup.find_all("div", {"class": "champion-name"})
        for champ in champs:
            championList.append(champ.string)
    else:
        print('Error fetching champions')
        exit()
    return championList


def spells(soup):
    tempSpells = []
    # Find Summoner spells
    for summSpells in soup.find_all("div", {"class","summoner-spells"}):
        for spell in summSpells.find_all("img"):
            tempSpells.append(spell['alt'].replace('Summoner Spell', '').strip())
    return tempSpells


def runes(type,soup):
    tempTree = {}
    # Grab all the runes from specified tree
    for runes in soup.find_all("div", {"class","{}-tree".format(type)}):
        tempPerkTitle = runes.find_all("div", {"class","perk-style-title"}, limit=1)
        tempTree['perk_title'] = tempPerkTitle[0].string
        tempActiveKeystones = runes.find_all("div", {"class","perk-active"})
        for num,keystone in enumerate(tempActiveKeystones):
            temp = keystone.find("img")["alt"].replace('The Keystone', '').replace('The Rune', '').strip()
            tempTree['keystone-'+str(num+1)] = temp
    return tempTree

def matchup(soup):
    tempMatchup = []
    # Find toughest champion matchups
    matchups = soup.find_all("div", {"class","champion-name"})
    for matchup in matchups:
        tempMatchup.append(matchup.string)
    return tempMatchup

def skills(soup):
    tempPriority = []
    for skills in soup.find_all("div", {"class","skill-priority"}):
        for skill in skills.find_all("div", {"class", "skill-label"}):
            tempPriority.append(skill.string)
    return tempPriority

def print_data(champion, spells, primaryTree, secondaryTree, toughestMatchup, skillPriority):
    print("-----Champion-----\n")
    print("      {}".format(champion.upper()))
    print("\n-------Runes------\n")
    print("Primary:\n")
    print(' --> '.join(str(x) for x in primaryTree.values()))
    print("\n\nSecondary:\n")
    print(' --> '.join(str(x) for x in secondaryTree.values()))
    print("\n\n-----Skill-Priority-----\n")
    print('-->'.join(skillPriority))
    print("\n-----Summoner-Spells-----\n")
    print(', '.join(spells))
    print("\n----Toughest-Matchups----\n")
    print(', '.join(toughestMatchup))

def main():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("champion", action="store", default='', help="Name of champion to look up.")
    parser.add_argument("-l", "--list", action="store_true", default=False, dest="list", help="Prints a list of all current champions")
    args = parser.parse_args()

    # if list arugment is specified
    if args.list is not False:
        for champ in fetch_champs():
            print("-{}".format(champ),end=' ')
        exit()
    
    # champion selected
    if args.champion is not None and type(args.champion) is str:
        championSelect = args.champion
        # Check to see if it is a valid champion
        if championSelect.lower() not in [champion.lower() for champion in fetch_champs()]:
            print("Champion '{}' does not exist. For a list of champions use the -l or --list argument".format(championSelect))
            exit()
        else:
            response = requests.get("https://u.gg/lol/champions/{}/build".format(championSelect.lower()))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')

                # Find Summoner spells
                summonerSpells = spells(soup)

                # Find primary runes
                primaryTree = runes('primary',soup)

                # Find secondary runes
                secondaryTree = runes('secondary',soup)

                # Find toughest matchups
                toughestMatchup = matchup(soup)

                # Find skill priority
                skillPriority = skills(soup)

                # Gather data and print
                print_data(championSelect,summonerSpells,primaryTree,secondaryTree,toughestMatchup,skillPriority)
                exit()
            else:
                print('Error fetching champion build')
                print(response)
                exit()
    else:
        print('Enter a champion name or type -l for a list of champions')

if __name__ == "__main__":
    main()