# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import psycopg2 as pg
import os


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from dotenv import load_dotenv

#
#

load_dotenv()

DB_NAME = os.environ.get("dbname")
USER = os.environ.get("user")
PASSWORD = os.environ.get("password")

#conn2 = pg.connect(database = DB_NAME, user = USER, password = PASSWORD)

connection = pg.connect("dbname=progetto_rasa user=postgres password=prova")
cursor = connection.cursor()



class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


#"Ciao {}:\n- {}".format(genre, "\n- ".join(l))
#per genere
class ActionRecommendGenre(Action):

    def name(self) -> Text:
        return "recommend_genre"
    
    def run(self, dispatcher : CollectingDispatcher, tracker : Tracker, domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        genre = tracker.get_slot("genre")
        query = f"SELECT name FROM serie_tv WHERE genres_1 = '{genre}'  OR genres_2 = '{genre}' ORDER BY vote_count DESC LIMIT 20"
        cursor.execute(query)
        data = cursor.fetchall()

        if data:
            names : list = [row[2] for row in data]
            dispatcher.utter_message("here some {} tv series:\n- {}".format(genre, "\n- ".join(names))) #forse basta
        else:
            dispatcher.utter_message("I'm sorry, I couldn't find TV series with the specified genre.")

        return []
        #for rows in data:


# top rating
class ActionRecommendTopRating(Action):

    def name(self) -> Text:
        return "recommend_top_rating"
    
    def run(self, dispatcher : CollectingDispatcher, tracker : Tracker, domain : Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        query = "SELECT name FROM serie_tv ORDER BY vote_count DESC LIMIT 20"
        cursor.execute(query)
        data = cursor.fetchall()

        if(data):
            pass
        else:
            dispatcher.utter_message("I'm sorry, there is a problem with the database")
        
        return []
    

#per informazioni su una serie tv
class ActionInfoSeries(Action):
    def name(self) -> Text:
        return "info_serie_tv"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Estrai il valore dell'entità 'serie_tv' dal tracker
        serie_tv = next(tracker.get_latest_entity_values("serie_tv"), None)

        if not serie_tv:
            dispatcher.utter_message("Non ho capito su quale serie TV stai chiedendo informazioni.")
            return []

        query = f"SELECT DINSTICT name,overview,in_production,original_language,number_of_seasons,number_of_episodes,vote_count FROM serie_tv WHERE name = '{serie_tv}'"
        cursor.execute(query)
        data = cursor.fetchall()

        if data:
            dispatcher.utter_message(f"Hai chiesto informazioni su {serie_tv}.")
            ##### messaggio con dati query
        else:
            dispatcher.utter_message("Non ho trovato la serie TV che stai chiedendo informazioni.")

        return []



class ActionKidsSeries(Action):

    def name(self) -> Text:
        return "recommend_kids_tvseries"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        query = "SELECT name FROM serie_tv WHERE genres_1 = 'Animation'  OR genres_2 = 'Animation' OR genres_1 = 'kids' OR  \
                genres_2 = 'kids' ORDER BY vote_count DESC LIMIT 20"
        
        cursor.execute(query)
        data = cursor.fetchall()

        if data:
            pass
        else:
            dispatcher.utter_message("I'm sorry, there is a problem with the database")

        return []