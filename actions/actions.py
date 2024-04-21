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
from rasa_sdk.events import SlotSet


from dotenv import load_dotenv

#
#

load_dotenv()

DB_NAME = os.environ.get("dbname")
USER = os.environ.get("user")
PASSWORD = os.environ.get("password")

#connection = pg.connect(database = DB_NAME, user = USER, password = PASSWORD)


connection = pg.connect("dbname=progetto_rasa user=postgres password=prova host=localhost")
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
        #genre : str = tracker.get_slot("genre")
        genre = next(tracker.get_latest_entity_values("genre"),None)

        genre = str(genre)

        if not genre:
            dispatcher.utter_message("I'm sorry, I do not understand the genre.")
            return []

        #print(connection.isexecuting())
        query = f"SELECT name FROM serie_tv WHERE genres_1 ILIKE '{genre}'  OR genres_2 ILIKE '{genre}' ORDER BY vote_count DESC LIMIT 20"
        print(query)
        cursor.execute(query)
        data = cursor.fetchall()

        #print(data)

        if data:
            names : list = [row[0] for row in data] 
            dispatcher.utter_message("here some {} tv series:\n- {}".format(genre, "\n- ".join(names))) #forse basta
            #dispatcher.utter_message("funziona")
        else:
            dispatcher.utter_message("I'm sorry, I couldn't find TV series with the specified genre.")

        return [SlotSet("genre", genre)] # forse non serve
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
            names : list = [row[0] for row in data] 
            fstr = "Here are the most rated TV series:\n- {}".format("\n- ".join(names))
            dispatcher.utter_message(fstr)
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
        serie_tv : str = next(tracker.get_latest_entity_values("tv_series"), None)

        print(serie_tv)

        if not serie_tv:
            dispatcher.utter_message("Non ho capito su quale serie TV stai chiedendo informazioni.")
            return []

        query = f"SELECT DISTINCT name,overview,in_production,original_language,number_of_seasons,number_of_episodes,vote_count FROM serie_tv WHERE name ILIKE '{serie_tv}'"
        cursor.execute(query)
        data = cursor.fetchall()
        

        if data:
            #dispatcher.utter_message(f"Hai chiesto informazioni su {serie_tv}.")
            #name = data[0][0]
            #fstr = f"name : {data[0][0]}\noverview : {data[0][1]}\nin production : {data[0][2]}\noriginal language : {data[0][3]}\n \
            #number of season : {data[0][4]}"
            parsed_data = format_info(data)
            ##### messaggio con dati query
            dispatcher.utter_message(f"here is some information about : {serie_tv}\n{parsed_data}") ##### da cambiare
        else:
            dispatcher.utter_message("Non ho trovato la serie TV che stai chiedendo informazioni.")

        return []#[SlotSet("rating", rating)]



class ActionKidsSeries(Action):

    def name(self) -> Text:
        return "recommend_kids_tvseries"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        query = "SELECT name FROM serie_tv WHERE genres_1 = 'Animation'  OR genres_2 = 'Animation' OR genres_1 = 'Kids' OR  \
                genres_2 = 'Kids' ORDER BY vote_count DESC LIMIT 20"
        
        cursor.execute(query)
        data = cursor.fetchall()

        if data:
            names : list = [row[0] for row in data] 
            fstr = "Here are some TV series for kids:\n- {}".format("\n- ".join(names))
            dispatcher.utter_attachment(fstr)
        else:
            dispatcher.utter_message("I'm sorry, there is a problem with the database")

        return []
    

class ActionRecommendbyYears(Action):
    def name(self) -> Text:
        return "recommend_by_years"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        pass 



def format_info(data : list) -> str:

    # Lista di tuple di esempio (puoi sostituirla con i tuoi dati)
    #data = [("Nome serie", "Panoramica della serie", "In produzione", "Lingua originale", 3, 24, 1000)]

    fields = ["name", "overview", "in production", "original language", "number of seasons", "number of episodes", "vote count"]

    fstr = ""

    # Funzione per aggiungere un campo alla stringa se esiste nella tupla dei dati
    def add_field(field_name, field_value):

        if field_value is not None:
            if isinstance(field_value, float):
                field_value = int(field_value)
            return f"\n{field_name.replace('_', ' ')}: {field_value}"
        else:
            return ""

    # Itera attraverso i campi e aggiungi quelli presenti nella tupla dei dati
    for field in fields:
        index = fields.index(field)
        if index < len(data[0]):
            fstr += add_field(field, data[0][index])

    return fstr

