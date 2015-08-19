#@author: jhertz

import challonge
import pprint


kMinimum = 32 
kStart = 800


player_db = {}


class player:
    name = ""
    rating = 0

    def __init__(self, name, rating=1200):
        self.name = name
        self.rating = rating
        self.k = 0
        self.gamesPlayed = 0
        self.wins = 0
        self.losses = 0

    def __str__(self):
        return "name: " + self.name + " rating: " + str(self.rating) + " K Value: " + str(self.k) + " gamesPlayed: " + str(self.gamesPlayed) + " Wins: " + str(self.wins) + " Losses: " + str(self.losses)


class match:
    winner = ""
    loser = ""
    score = ""

    def __init__(self, winner, loser, score):
        self.winner = winner
        self.loser = loser
        self.score = score

    def __str__(self):
        return "winner: " + self.winner + " loser: " + self.loser + " score: " + self.score



def get_player(name):
    if player_db.has_key(name):
        return player_db[name]
    else:
        player_db[name] = player(name)
        return player_db[name]


def print_ratings():
    players = player_db.values()
    sorted_players = sorted(players, key=lambda p: p.rating, reverse=True)
    for p in sorted_players:
        print p


def update_rating(winner, loser, scores):

    pprint.pprint(scores)

    wins = int(scores[1])
    for games in range(0, wins):
        winner.gamesPlayed += 1
        winner.wins += 1
        loser.gamesPlayed += 1
        loser.losses += 1
        winner_old_rating = winner.rating
        loser_old_rating = loser.rating
        winner.k = kStart / winner.gamesPlayed;
        if winner.k < kMinimum:
            winner.k = kMinimum
        loser.k = kStart / loser.gamesPlayed;
        if loser.k < kMinimum:
            loser.k = kMinimum
        Ea = calcE(winner_old_rating, loser_old_rating)
        Eb = calcE(loser_old_rating, winner_old_rating)
        winner.rating =  winner_old_rating + winner.k * (1 - Ea)
        loser.rating =  loser_old_rating + loser.k * (0 - Eb)
        print("WINNING: " + str(winner_old_rating) + ' ' + str(winner.rating))

    losses = int(scores[0])
    for games in range(0, losses):
        winner.gamesPlayed += 1
        winner.losses += 1
        loser.gamesPlayed += 1
        loser.losses += 1
        winner_old_rating = winner.rating
        loser_old_rating = loser.rating
        winner.k = kStart / winner.gamesPlayed;
        if winner.k < kMinimum:
            winner.k = kMinimum
        loser.k = kStart / loser.gamesPlayed;
        if loser.k < kMinimum:
            loser.k = kMinimum
        Ea = calcE(winner_old_rating, loser_old_rating)
        Eb = calcE(loser_old_rating, winner_old_rating)
        winner.rating =  winner_old_rating + winner.k * (0 - Ea)
        loser.rating =  loser_old_rating + loser.k * (1 - Eb)
        print("Losing!: " + str(winner_old_rating) + ' ' + str(winner.rating))



def calcE(a, b):
    return 1.0 / (1.0 + 10.0**((b - a) / 400))


def init_challonge(username, api_key):
    challonge.set_credentials(username, api_key)

def get_tournament(id):
    return challonge.tournaments.show(id)

def get_participants(id):
    return challonge.participants.index(id)

def get_matches(id):
    return challonge.matches.index(id)

def harvest_matches(id):
    participants = get_participants(id)
    matches = get_matches(id)
    ids_to_names = {}
    for p in participants:
        ids_to_names[p['id']] = p['name']
    toReturn = []
    for m in matches:
        winner = ids_to_names[m['winner-id']]
        loser = ids_to_names[m['loser-id']]
        score = m['scores-csv']
        toReturn.append(match(winner, loser, score))
    return toReturn

def update_elos_from_matches(matches):
    for match in matches:
       # print "about to process a match::"
        winner = get_player(match.winner)
       # print "winner: " , winner
        loser = get_player(match.loser)
       # print "loser: " , loser
        scores = match.score.split('-')
        scores.sort()
        update_rating(winner, loser, scores)





if __name__ == "__main__":
    api_key = ""
    username = ""
    brackets = []

    with open("brackets.txt") as bracket_file:
        for line in bracket_file:
            brackets.append(line.rstrip())

    if not brackets:
        print "failed to read brackets, exiting"
        exit(-3)

    with open("creds.txt") as creds_file:
        username = creds_file.readline().rstrip()
        api_key = creds_file.readline().rstrip()


    if not api_key:
        print "failed to read api key, exiting"
        exit(-1)

    if not username:
        print "failed to read username, exiting"
        exit(-2)



    init_challonge(username, api_key)
    for bracket_id in brackets:
        #print "about to do bracket:" , bracket_id , "\n"
        matches = harvest_matches(bracket_id)
        update_elos_from_matches(matches)
        #print_ratings()

   # print "done, printing final ratings \n"
    print_ratings()
  #  print "exiting"
#test