import subprocess
import pandas as pd

numero_timeline = 100
step = 25
final_data = pd.DataFrame()

# eseguiamo API_timeline n volte per sudduvisione del carico computazionale
# se il pc non riesce comunque a mantenere i dataframe occore diminuire il valore di step
# il range va da 0 fino al numero di conversation
for init in range(0, numero_timeline, step):
    finish = init + step
    program = 'API_timeline.py '+str(init)+' '+str(finish)
    subprocess.call(['python', 'API_timeline.py ', str(init), str(finish)])
    print("Finished:" + program)

print("MERGING...")
# uniamo tutti i dataframe in un unico risultante
for init in range(0, numero_timeline, step):
    timeline_data = pd.read_csv("Timeline["+ str(init+1) +"-"+ str(init+step) +"].csv")
    if init == 0:
        final_data = pd.DataFrame(timeline_data)
    else:
        final_data = final_data.append(timeline_data, ignore_index = True)

#rimuoviamo duplicati
final_data = final_data.drop_duplicates(subset=['id'])

conversation_data = pd.read_csv('Conversation.csv')
conversation_data = conversation_data.drop_duplicates(subset=['author_id'])
for i in conversation_data.index:
    if final_data.loc[final_data['id'] == conversation_data['author_id'][i]].empty:
        aux = {'id': id,
               'polarization': 0}
        final_data = final_data.append(aux, ignore_index=True)


final_data = final_data.drop_duplicates(subset=['id'])
final_data.to_csv("Timeline.csv" , index=False)