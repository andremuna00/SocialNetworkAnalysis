import TwitterAPI
import pandas as pd
import re
from feel_it import  SentimentClassifier
import sys
# pip install -U feel-it
# al momento non supportata per python 3.10.x
# https://towardsdatascience.com/sentiment-analysis-and-emotion-recognition-in-italian-using-bert-92f5c8fe8a2
api_key = ""
api_secret = ""
access_token = ""
access_secret = ""

api = TwitterAPI.TwitterAPI(api_key, api_secret, access_token,
                 access_secret, auth_type='oAuth2', api_version='2')

# leggiamo i dati delle conversation
conversation_data = pd.read_csv('Conversation.csv')

# rimuoviamo author id duplicati nelle conversation
conversation_data = conversation_data.drop_duplicates(subset=['author_id'])

# istanziamo nuovi dataframe
timeline_data = pd.DataFrame()
result = pd.DataFrame()

print("CARICO LIBRERIE PER DETERMINARE SENTIMENT...")
sentiment_classifier = SentimentClassifier()

print("SCARICO LE TIMELINE DI TUTTI GLI UTENTI CHE HANNO PARTECIPATO ALLE DIECI CONVERSATION...")
# valori necessari per iterare il programma tramite run timeline script
name, init, finish = sys.argv

init = int(init)
finish = int(finish)
count = 0
richieste = 0
lunghezza = len(conversation_data.index)

# iteriamo le conversazioni e prendiamo solo le timeline nelle posizioni passate da linea di comando: init e finish
for i in conversation_data.index:
    if count >= init and count <= finish:
        # prima pagina
        timeline = api.request('users/:%s/tweets' % (conversation_data["author_id"][i]),{
                               'tweet.fields': "author_id",
                                'max_results': "100"}).json()
        richieste = richieste + 1
        # errori di profili privati o non più esistenti
        if "'detail': 'Could not find user with id:" in str(timeline):
            print("ERROR: user_id not found")
        elif "detail': 'Sorry, you are not authorized to see the user with" in str(timeline):
            print("ERROR: private user_id")
        else:
            # calcolo del next_token per l'eventuale seconda pagina
            if "next_token" in timeline['meta'].keys():
                next_token = timeline['meta']['next_token']
            else:
                next_token = None
    
            # scarico i dati e li memorizzo del dataframe
            if timeline["meta"]["result_count"]>0:
                for x in timeline["data"]:
                    # inizializzo data_frame
                    if timeline_data.empty:
                        timeline_data = pd.DataFrame(x, dtype=str, index=[0])
                    # appendo nuovi dati
                    else:
                        temp = pd.DataFrame(x, dtype=str, index=[0])
                        timeline_data = timeline_data.append(temp, ignore_index=True)
                # numero di pagine scaricate (ogni pagina ha 100 tweet)
                k = 1
                print("timeline N°" + str(count + 1) + "/" + str(lunghezza) + "--> tweets downloaded: " + str(k * 100))
            # itero queste operazioni
            while next_token:
                timeline = api.request('users/:%s/tweets' % (conversation_data["author_id"][i]), {
                        'tweet.fields': "author_id",
                        'max_results': "100",
                        'pagination_token': next_token}).json()

                richieste = richieste + 1

                if "next_token" in timeline['meta'].keys():
                    next_token = timeline['meta']['next_token']
                else:
                    next_token = None

                if timeline["meta"]["result_count"] > 0:
                    for x in timeline["data"]:
                        temp = pd.DataFrame(x, dtype=str, index=[0])
                        timeline_data = timeline_data.append(temp, ignore_index=True)

                    k = k + 1
                    print("timeline N°" + str(count + 1) + "/" + str(lunghezza) + "--> tweets downloaded: " + str(k * 100))
                    if k*100 >= 1000:
                        break;
            # numero timeline scaricate
    elif count > finish:
        break;
    count = count + 1

# cleaning data
print("RIMUOVIAMO TWEET NON INERENTI AL TEMA ...")
initial_len = len(timeline_data.index)
timeline_data = timeline_data[timeline_data.text.str.contains('greenpass|vaccino|super green|siero')]
final_len = len(timeline_data.index)
print("tweets iniziali: "+str(initial_len)+"; tweets finali: "+str(final_len)+"; tweets rimossi: "+str(initial_len-final_len))

# enrichment data con sentiment
print("CALCOLIAMO SENTIMENT DEI TWEET...")
timeline_data = timeline_data.assign(sentiment = "nan")
len = len(timeline_data.index)
count = 0
for i in timeline_data.index:
    timeline_data["sentiment"][i] = str(sentiment_classifier.predict([timeline_data["text"][i]]))
    count = count + 1
    print("sentiment calcolato: "+str(count)+"/"+str(len))

# calcolo polarization e creo dataset risultante
print("CALCOLO POLARIZZAZIONE UTENTI DA SENTIMENT...")
aux = pd.DataFrame()
for id in timeline_data.groupby(['author_id']).groups.keys():
    positive = timeline_data[(timeline_data.author_id == id) & (timeline_data.sentiment == "['positive']")].count()['sentiment']
    negative = timeline_data[(timeline_data.author_id == id) & (timeline_data.sentiment == "['negative']")].count()['sentiment']
    total = positive + negative
    polar = positive - negative
    if result.empty:
        aux = {'id': [id],
               'polarization': [(polar/total)]}
        result = pd.DataFrame(data = aux)
    else:
        aux = {'id': id,
               'polarization': (polar / total)}
        result = result.append(aux, ignore_index=True)

# memorizza dataset
result.to_csv("Timeline["+str(init+1)+"-"+str(finish)+"].csv" , index=False)