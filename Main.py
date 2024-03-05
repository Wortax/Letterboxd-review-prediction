from Web_scrapping import *
from Machine_learning import *
import re
import PySimpleGUI as sg
from datetime import datetime

class CancelExecution(Exception):
    pass

def predict_dataset(dataset,output_file):

    with open(output_file, 'w', newline='') as outfile:
             writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
             for i in dataset :
                 if len(i)==0 :
                     continue
                 i=[re.sub(r'[^\x00-\x7F]', ' ', i[0]),i[1],i[2]]
                 writer.writerow(i)
    outfile.close()



layout = [  [sg.Text("Upload your ratings.csv file: ")],
            [sg.FileBrowse(key="TrDtIn"), sg.Text("")],[sg.Button("Submit")],[sg.Text('', key = 'review_text'  ,visible=False)],
            [sg.Text('')],
            [sg.Text('Enter the list URL'), sg.InputText(key="ListURL")],[sg.Button("Submit URL")],[sg.Text('', key = 'listURL_text'  ,visible=False)],
            [sg.Text('')],
            [sg.Text('_________________________________________________________')],
            [sg.Text("Upload your Train dataset: ")],
            [sg.FileBrowse(key="TrDtprd"), sg.Text("")],
            [sg.Text("Upload your Movie dataset: ")],
            [sg.FileBrowse(key="TeDtprd"), sg.Text("")],
            [sg.Text('')],
            [sg.Button("Predict")],[sg.Button("Precision Test")],[sg.Text('', key = 'Prec_result'  ,visible=False)],
            [sg.Text('', key = 'predict_text'  ,visible=False)],
            [sg.Text('')],
            [sg.Button('Exit')] ]


window = sg.Window('Letterboxd ML', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or event =='Exit':	
        break
    if event == 'Submit':
        try :
            today = datetime.today()
            d1 = str("CSV/Train_dataset_"+today.strftime("%d-%m-%Y-%H-%M")+".csv")
            
            if Create_dataset(values["TrDtIn"],d1) == 0 :
                raise CancelExecution("Execution Canceled")

            
            window['review_text'].Update(visible = True,text_color='pale green')
            window['review_text'].Update('Train dataset file Created at '+d1)
        except Exception as e:

            window['review_text'].Update(visible = True,text_color='red')
            window['review_text'].Update(e)


        
    elif event == 'Submit URL':
        try :
            today = datetime.today()
            d1 = str("CSV/Movie_dataset_"+today.strftime("%d-%m-%Y-%H-%M")+".csv")
            
            if Create_predict_dataset(d1,Get_urls_from_list(values["ListURL"])) == 0 :
                raise CancelExecution("Execution Canceled")

        
            window['listURL_text'].Update(visible = True,text_color='pale green')
            window['listURL_text'].Update('Movie dataset file Created at '+d1)

        except Exception as e:
            
            window['listURL_text'].Update(visible = True,text_color='red')
            window['listURL_text'].Update(e)
        
    elif event == 'Predict':
        
        try :
            data = pd.read_csv(values["TrDtprd"], encoding='latin-1')
            data2 = pd.read_csv(values["TeDtprd"], encoding='latin-1')
            
            dir_dict = Create_dirdict(data)
            actors_dict = Create_actdict(data)
            coun_dict = Create_coundict(data)
            
            train_x = Process_data(data,True,actors_dict,dir_dict,coun_dict)
            train_y = Process_y(data["Own_Rate"])


            train_mod = Train(train_x, train_y)
            rf = train_mod[0]
            model = train_mod[1]

            list_result= []
            for i in range(0,len(data2)):
                r = check_movie(data2.iloc[i],rf,model,actors_dict,dir_dict,coun_dict)
                if not sg.one_line_progress_meter('Progress Meter', i+1, len(data2), 'Predicting list :') and i+1 != len(data2):
            	    raise CancelExecution("Execution Canceled")
                list_result.append(r)
            
            today = datetime.today()
            d1 = str("CSV/Prediction_Result_"+today.strftime("%d-%m-%Y-%H-%M")+".csv")
            
            predict_dataset(list_result,d1)

            window['predict_text'].Update(visible = True,text_color='pale green')
            window['predict_text'].Update('Prediction file Created at '+d1)
            
        except Exception as e:
            window['predict_text'].Update(visible = True,text_color='red')
            window['predict_text'].Update(e)
            

    elif event == 'Precision Test':

        try :
            data = pd.read_csv(values["TrDtprd"], encoding='latin-1')
            data2 = data.tail(len(data)//10)
            data.drop(data.tail(len(data)//10).index,inplace = True)
            dir_dict = Create_dirdict(data)
            actors_dict = Create_actdict(data)
            coun_dict = Create_coundict(data)

            train_x = Process_data(data,True,actors_dict,dir_dict,coun_dict)
            train_y = Process_y(data["Own_Rate"])

            test_x = Process_data(data2,True,actors_dict,dir_dict,coun_dict)
            test_y = Process_y(data2["Own_Rate"])


            train_mod = Train(train_x, train_y)
            rf = train_mod[0]
            model = train_mod[1]
            
            test_y = test_y.to_numpy()
            Precision_result = Precision_test((rf.predict(test_x)+model.predict(test_x))/2, test_y)

            window['Prec_result'].Update(visible = True,text_color='white')
            window['Prec_result'].Update("0.5 star precision :"+str(Precision_result[0])+" %"+"\n"+"0.25 star precision precision :"+str(Precision_result[1])+" %")
            
        except Exception as e:
            window['Prec_result'].Update(visible = True,text_color='red')
            window['Prec_result'].Update(e)
        

window.close()
