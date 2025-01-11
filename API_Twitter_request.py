import TwitterAPI
import pandas as pd
from feel_it import  EmotionClassifier, SentimentClassifier
#pip install -U feel-it
#https://towardsdatascience.com/sentiment-analysis-and-emotion-recognition-in-italian-using-bert-92f5c8fe8a2

# chiavi API
api_key = ""
api_secret = ""
access_token = ""
access_secret = ""

api = TwitterAPI.TwitterAPI(api_key, api_secret, access_token,
                 access_secret, auth_type='oAuth2', api_version='2')

# creazione variabili dataframe
tweet_data = pd.DataFrame()
conversation_user_info = pd.DataFrame()
conversation_data = pd.DataFrame()
timeline_data = pd.DataFrame()

print("CARICO LIBRERIE PER DETERMINARE SENTIMENT ...")
sentiment_classifier = SentimentClassifier()

print("INIZIO A SCARICARE TWEET...")
QUERY = "(#greenpass OR #supergreenpass) lang:it -is:retweet"

# primi cento tweetr scaricati
tweet = api.request('tweets/search/recent',
                   {'query':QUERY,
                    'max_results': "100",
                    'tweet.fields': "public_metrics,conversation_id"}).json()

next_token = tweet['meta']['next_token']

# modifica del campo public metrics con la somma di tutte le metriche
init = True
for t in tweet['data']:
    t['public_metrics'] = int(t['public_metrics']['like_count'] + t['public_metrics']['quote_count'] + t['public_metrics']['reply_count'] +t['public_metrics']['retweet_count'])
    t['text'] = str(sentiment_classifier.predict([t['text']]))
    # inzializza dataframe
    if init:
        tweet_data = pd.DataFrame(t, index=[0])
        init = False
    # appende nuovi dati
    else:
        tweet_data = tweet_data.append(pd.DataFrame(t, index=[0]), ignore_index=True)

i = 0
print("tweet scaricati e analizzati: "+ str((i+1)*100))

# sulla base di next_token scarico le "pagine" successive dei tweet ed elaboro le metriche come fatto precedentemente finchè disponibili, circa 7000 tweet in totale
while next_token:
    tweet = api.request('tweets/search/recent',
                            {'query': QUERY,
                             'max_results': "100",
                             'next_token': next_token,
                             'tweet.fields': "public_metrics,conversation_id"}).json()
    # verifica presenza next_token
    if "next_token" in tweet["meta"].keys():
        next_token = tweet['meta']['next_token']
    else:
        next_token = None

    for t in tweet['data']:
        t['public_metrics'] = int(t['public_metrics']['like_count'] + t['public_metrics']['quote_count'] + t['public_metrics']['reply_count'] + t['public_metrics']['retweet_count'])
        t['text'] = str(sentiment_classifier.predict([t['text']]))
        tweet_data = tweet_data.append(pd.DataFrame(t, index=[0]), ignore_index=True)

    i = i + 1
    print("tweet scaricati e analizzati: " + str((i + 1) * 100))

# ordino ed esporto i tweet
tweet_data.sort_values('public_metrics', ascending = False, ignore_index = True, inplace=True)
tweet_data.to_csv("Tweets.csv", index=False)

'''-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

print("DAI PRIMI DIECI TWEET (ordinati in base a somma public_metrics) SCARICO LE CONVERSATION...")

# similmente a prima scarico i tweet relativi alle prime 5 conversation "positive" e "negative" limitando però le pagine a 10
selected_tweets = pd.DataFrame()
count = 0
positive = 0
negative = 0

for i in tweet_data.index:
    # calcolo se tweet è "positivo o negativo"
    if tweet_data["text"][i] == "['positive']":
        b_positive = True
        positive = positive + 1
    else:
        b_positive = False
        negative = negative + 1
    if (b_positive and positive <= 5) or (not b_positive and negative <= 5):
        # creazione dataset dei 10 tweet selezionati
        if selected_tweets.empty:
            row = {
                'conversation_id': [tweet_data['conversation_id'][i]],
                'id': [tweet_data['id'][i]],
                'public_metrics': [tweet_data['public_metrics'][i]],
                'text': [tweet_data['text'][i]],
            }
            selected_tweets = pd.DataFrame(row, index=[0])
        else:
            selected_tweets = selected_tweets.append(tweet_data.iloc[i], ignore_index=True)

        conversation = api.request('tweets/search/recent',
                            {'query': ('conversation_id:'+str(tweet_data["conversation_id"][i])),
                             'tweet.fields': "author_id,in_reply_to_user_id,conversation_id",
                             'max_results':"100"
                             }).json()

        # verifco la presenza di next_token
        if "next_token" in conversation["meta"].keys():
            next_token = conversation['meta']['next_token']
        else:
            next_token = None

        if conversation["meta"]["result_count"]>0:
            for x in conversation["data"]:
                # inizializza dataframe
                if conversation_data.empty:
                    conversation_data = pd.DataFrame(x, dtype=str, index=[0])
                # appende i nuovi dati
                else:
                    temp = pd.DataFrame(x, dtype=str, index=[0])
                    conversation_data = conversation_data.append(temp, ignore_index=True)

        k = 1
        print("conversation N°"+ str(count+1) + "--> replies downloaded: " + str(k*100))
        # itero le pagine
        while next_token:
            conversation = api.request('tweets/search/recent',
                                       {'query': ('conversation_id:' + str(tweet_data["conversation_id"][i])),
                                        'tweet.fields': "author_id,in_reply_to_user_id,conversation_id",
                                        'max_results': "100",
                                        'next_token': next_token
                                        }).json()

            if "next_token" in conversation["meta"].keys():
                next_token = conversation['meta']['next_token']
            else:
                next_token = None

            if conversation["meta"]["result_count"] > 0:
                for x in conversation["data"]:
                    temp = pd.DataFrame(x, dtype=str, index=[0])
                    conversation_data = conversation_data.append(temp, ignore_index=True)

            k = k + 1
            print("conversation N°" + str(count + 1) + "--> replies downloaded: " + str(k * 100))

            # massimo 500 replies
            if k == 5:
                break;
                
        # quando ho scaricato mille tweet dalla conversazione passo alla successiva
        count = count + 1
        if(count >= 10):
            break

# esporto tutti i tweet scaricati delle conversazioni
selected_tweets.to_csv("SelectedTweets.csv" , index=False)
result = pd.DataFrame()

print("COSTRUENDO DATASET FINALE ...")
for i in conversation_data.index:
    if result.empty:
        aux = {'author_id': [str(conversation_data["author_id"][i])],
               'in_reply_to_user_id': [str(conversation_data["in_reply_to_user_id"][i])],
               'conversation_id': [str(conversation_data["conversation_id"][i])]}
        result = pd.DataFrame(data = aux)
    else:
        aux = {'author_id': str(conversation_data["author_id"][i]),
               'in_reply_to_user_id': str(conversation_data["in_reply_to_user_id"][i]),
               'conversation_id': str(conversation_data["conversation_id"][i])}
        result = result.append(aux, ignore_index = True)

result.to_csv("Conversation.csv", index = False)

# rimuoviamo author id duplicati nelle conversation
result = result.drop_duplicates(subset=['author_id'])
print("NUMERO DI AUTORI DIVERSI DA CUI SCARICARE LE TIMELINE: "+ str(len(result.index)))

