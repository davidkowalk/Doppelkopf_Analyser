from csvloader import load_sheet as get
from math import sqrt
from math import floor
from math import ceil

swap_party = {
    "r":"c",
    "c":"r"
}

player_list = ['D', 'A', 'M', 'P']

def initialize(players):
    global player_list

    player_list = players

def get_win_percentage_for_game(sheets):

    games = 0

    #Initialize win percentage
    win_percentage = {}
    for player in player_list:
        win_percentage[player] = 0


    for sheet in sheets:
        players = sheet[0]
        final_row = sheet[len(sheet)-2]

        for cell_nr in range(4):
            current_player = players[cell_nr]

            if int(final_row[cell_nr]) > 0:
                win_percentage[current_player] +=1 #Count number of wins

        games += 1


    #At the end, divide number of wins through the number of games for each player.
    for player in win_percentage:
        win_percentage[player] /= games

    return win_percentage

def gen_user_stats(sheets):

    games = {}

    for player in player_list:
        games[player] = {
                "r": {"played":0, "won":0, "score":0},
                "c": {"played":0, "won":0, "score":0},
                "sheet_stats":[],
                "prev": 0
            }

    games["total"] = 0

    # For every player define for each party [played, won, score] and previous
    # And define Total Games

    # Keep Track of current position for data error alerts
    sheet_nr = 0

    for sheet in sheets:

        #Add Sheet to statistics over sheets [won, played]
        for player in player_list:
            games[player]["sheet_stats"].append([0, 0])

        sheet_nr += 1
        reset_previous(games)

        player = sheet[0]

        for row_int in range(1, len(sheet)):

            # For every row in the sheet:
            # 1. Verify that the round does not imply any special case (Trumpfarmut, Solo, etc)
            # 2. Determine winning Party
            # 3. Count wins and participations for each player in loop
            # 4. Verify data integrity

            total_wins = 0  # Counts the winning players for every round to verify data integrity

            #Read row and round value from sheet
            row = sheet[row_int]
            game_score = int(row[4])

            if len(row) != 5 or int(row[4]) == 0: # Skip row if special game
                # print(f"=== Scipping game (Sheet {sheet_nr}, Row {row_int}) ===")
                update_previous(row, games, player)
                continue

            games["total"] += 1


            #Determine Winning Party
            if game_score >= 1:
                winning_party = "r"
            elif game_score <= -1:
                winning_party = "c"
            else:
                continue

            loosing_party = swap_party[winning_party]

            for cell in range(0, 4):

                # For player of any given round:
                # 1. Load score from this and the previous round
                # 2. Count a win if in the winning party
                # 3. Count participation in played parties
                # 4. Check sum and winner count

                current_player = player[cell]
                previous_round = games[current_player]["prev"] # Score after previous round -> Example games["D"][p]
                score = int(row[cell])

                games[current_player] ["sheet_stats"] [-1] [1] += 1

                if score > previous_round:

                    # if score for player increased, add 1 to winning party's wins
                    games[current_player] [winning_party] ["won"] += 1
                    games[current_player] [winning_party] ["played"] += 1
                    games[current_player] [winning_party] ["score"] += abs(game_score) #Count up winning points

                    #Count Sheet Specific Stats
                    games[current_player] ["sheet_stats"] [-1] [0] += 1

                    total_wins += 1
                elif score < previous_round:
                    games[current_player] [loosing_party] ["played"] += 1
                else:
                    print(f"=== ALERT (Unexpected static: Sheet {sheet_nr}, Row {row_int}, Player {current_player}) ALERT ===")
                    exit()

                #Update Previous Game to current for next iteration
                games[current_player]["prev"] = int(row[cell])


            if total_wins != 2 or not check_sum_right(row):
                print(f"===ALERT (Sheet {sheet_nr}, Row {row_int}) ALERT===")

            if games[current_player]["r"]["played"] + games[current_player]["c"]["played"] != games["total"]:
                print(f"=== ALERT (Game count does not align: Sheet {sheet_nr}, Row {row_int}, Score {row[4]}) ALERT ===")
                exit()

    return games


def append_significant_interval(games, p):
    for player in player_list:

        # Re
        n = games[player]["r"]["played"]
        my = p["r"]*n
        games[player]["r"]["my"] = round(my*10)/10
        sigma = sqrt(my*(1-p["r"]))
        games[player]["r"]["interval"] = (floor(my-1.96*sigma), ceil(my+1.96*sigma))

        # Contra
        n = games[player]["c"]["played"]
        my = p["c"]*n
        games[player]["c"]["my"] = round(my*10)/10
        sigma = sqrt(my*(1-p["c"]))
        games[player]["c"]["interval"] = (floor(my-1.96*sigma), ceil(my+1.96*sigma))


from probability_engine import radius
def append_significant_interval_custom(games, p, significance):
    p_rad = 1-significance

    for player in player_list:
        # Re
        n = games[player]["r"]["played"]
        my = p["r"]*n
        sigma = sqrt(my*(1-p["r"]))
        my_rad = radius(p_rad, sigma)
        games[player]["r"]["interval"] = (floor(my-my_rad), ceil(my+my_rad))

        # Contra
        n = games[player]["c"]["played"]
        my = p["c"]*n
        sigma = sqrt(my*(1-p["c"]))
        my_rad = radius(p_rad, sigma)
        games[player]["c"]["interval"] = (floor(my-my_rad), ceil(my+my_rad))


def reset_previous(games):
    # players = ["D", "A", "M", "P"]

    players = player_list

    for player in players:
        games[player]["prev"] = 0

def update_previous(row, games, player):
    for cell in range(0, 4):
        games[player[cell]]["prev"] = int(row[cell]) # update cells

def check_sum_right(row):
    return int(row[0])+int(row[1])+int(row[2])+int(row[3]) == 0
    #Summ of all players needs to be 0

def win_sum_right(rwin, cwin, twin): #Re-Win, Contra-Win and Total-win
    return int(rwin) + int(cwin) == int(twin)



#print(get_map(["A", "D", "M", "P", "S"]))
