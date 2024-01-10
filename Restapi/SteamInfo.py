from steam import Steam
from decouple import config

# Screenshot links -> https://steamcommunity.com/profiles/76561198869949927/screenshots/

KEY = config("STEAM_API_KEY")
ID =config("STEAM_ID")
steam = Steam(KEY)

# GAMES
# print("     User Games\n") 
# games = steam.users.get_owned_games(ID)
# n = 1
# for i in games['games']:
#     print(str(n)+" -> "+ i['name'])
#     n += 1

# # User Badges
# print("\n****************************\n")
# print("     User Badges\n")
# user_badges = steam.users.get_user_badges(ID)
# for badges in user_badges['badges']:
#     print(badges['badgeid'],end=", ")
#     print(badges['level'],end=", ")
#     print(badges['completion_time'],end=", ")
#     print(badges['xp'],end=", ")
#     print(badges['scarcity'])

# print(user_badges['player_level'])
# print(user_badges['player_xp'])
# print(user_badges['player_xp_needed_to_level_up'])
# print(user_badges['player_xp_needed_current_level'])


# UserDetails
# print("\n****************************\n")
# print("     User Details\n")

# user_details = steam.users.get_user_details(ID)
# print("Steam ID -> "+user_details['player']['steamid'])
# print("Profile State -> "+str(user_details['player']['profilestate']))
# print("Personaname -> "+user_details['player']['personaname'])
# print("ProfileURL -> "+user_details['player']['profileurl'])
# print("Last log off -> "+str(user_details['player']['lastlogoff']))
# print("Persona State -> "+str(user_details['player']['personastate']))
# print("Real name -> "+user_details['player']['realname'])
# print("Time created -> "+str(user_details['player']['timecreated']))
# print("Persona state Flags -> "+str(user_details['player']['personastateflags']))
# print("Loc country code -> "+str(user_details['player']['loccountrycode']))
# print("Loc state code -> "+str(user_details['player']['locstatecode']))
# print("Loc city id -> "+str(user_details['player']['loccityid']))


# # #Friends
# # print("\n****************************\n")
# # print("     User Friends\n")

# # user_friends = steam.users.get_user_friends_list(ID)
# # for friends in user_friends['friends']:
# #     print(friends["personaname"])
# # print()
# # for friends in user_friends['friends']:
# #     try:
# #         PersonaName = friends["personaname"]
# #         try:
# #             RealName = friends['realname']
# #         except:
# #             RealName = ""
# #         SteamID = str(friends['steamid'])

# #         print(PersonaName+" ("+RealName+") -> "+SteamID)
# #     except:
# #         pass


# # # Recently Played
# # # print("\n****************************\n")
# # # print("     Recently Played\n")

# # # user_recently_played = steam.users.get_user_recently_played_games(ID)
# # # for games in user_recently_played['games']:
# # #     print(games['name']+" ->  "+str(round(float(games["playtime_2weeks"]/60),2))+" "+str(games['appid']))


# # # App Details 
# # # steam.apps.get_app_details() return str, wait for an update

# # beamng_details = steam.apps.get_app_details(app_id=284160)
# # print(beamng_details)
# print(beam_details["284160"]['data'].keys())

