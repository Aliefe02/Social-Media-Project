from steam import Steam
from decouple import config
import mysql.connector

KEY = config("STEAM_API_KEY")
ID =config("STEAM_ID")
steam = Steam(KEY)

games = steam.users.get_owned_games(ID)
games = games['games']
print(games[0]['appid'])



mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="Dominikefe2002",
  database="gamemedia"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM auth_api_game")
myresult = mycursor.fetchall()
print(myresult)
# db_game_id_list = []
# for game in myresult:
#     db_game_id_list.append(game[0])
# print(db_game_id_list)
# n = 0

# for user_games in games:
#     if user_games['appid'] in db_game_id_list:
#         continue

# mycursor.execute("INSERT INTO auth_api_game (game_name,app_id) VALUES('Raft',789)")