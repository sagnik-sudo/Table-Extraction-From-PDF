import pandas as pd
import json
import time



def json_respone_to_df(path):
    '''

    :param path to json response from dexter:
    :return: list of tables formed from response

    '''

    with open(path) as data_file:
        data = json.load(data_file)
    df = pd.json_normalize(data,sep="_")
    sub_json_list=df["pages"].iloc[0]
    main_df = pd.json_normalize(sub_json_list)
    final_op=[]
    for i,page in main_df.iterrows():

        tables = page["tables"]
        for table in tables:
            df_op=[]
            for row in table["text"]:
                temp=[]
                for column in table["text"][row]:
                    temp.append(table["text"][row][column]["text"])
                df_op.append(temp)
            final_op.append(df_op)
    print(final_op)
    i=1
    ts = time.time()
    for DF in final_op:
        filenm = f"dexterOutput/file{ts}.csv"
        pd.DataFrame([[f"Data Frame {i}"],[" "]],columns=["---------------------------------"]).to_csv(filenm,mode = 'a', index=False)
        pd.DataFrame(DF).to_csv(filenm,mode = 'a', index = False)
        i+=1
    print("DONE")
    return filenm
