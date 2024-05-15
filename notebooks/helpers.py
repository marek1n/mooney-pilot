import pandas as pd
import numpy as np
from pathlib import Path


def check_timeout(df):
    """Account for timeout trials
    Find trials which _only_ have a timer row, label them as 'timeout' trials; then remove all other timer rows
    """
    df_timeouts = pd.DataFrame()
    PIDs = df.PID.unique().tolist()

    #for sub in [PIDs[2]]:
    for sub in PIDs:
        df_sub = df.loc[df["PID"] == sub,:]
        # Find unique rows based on 'image' & get their indices (= timed out trials)
        duplicates = df_sub.duplicated(subset=['image','condition'], keep=False)
        unique_indices = np.where(~duplicates)[0]     
        # set timeout to true
        df_sub.iloc[unique_indices,-1] = 1
        # remove duplicates
        df_sub = df_sub.drop_duplicates(subset=['image','condition'],keep='first') 
        # add to new df
        df_timeouts = pd.concat([df_timeouts, df_sub])

    df = df_timeouts.reset_index(drop=True)
    df = df.drop(columns=['Zone Name','Screen Name'])

    return df


def add_correct_trial_block_nr(df):
    trial = 1
    block = 1
    for r in range(0,len(df.index)):
        df.loc[r,'trial'] = trial
        trial += 1
        df.loc[r,'block'] = block
        
        if r < (len(df. index) - 1):
            if df.loc[r, 'PID'] == df.loc[r + 1,'PID']:
                if (df.loc[r, 'condition'] == 'post') & (df.loc[r + 1, 'condition'] == 'pre'):
                    trial = 1
                    block += 1
            else:
                trial = 1
                block = 1
    return df


def load_prolific(path_to_data: str | Path) -> pd.DataFrame:
    
    if isinstance(path_to_data, str): 
        path_to_data = Path(path_to_data) 

    files = [f for f in path_to_data.glob("data_exp_*.csv")]

    df = pd.DataFrame()
    display_counts = []
    names = []

    for f in files:
        df_raw = pd.read_csv(f)
        display_counts.append(df_raw.display.value_counts())
        names.append(df_raw["Participant Public ID"].dropna().unique().item())

        #df_raw.loc[(df_raw["answer"] == 'body(animal)'), 'answer'] = 'body (animal)' # fix typo

        df_s = (df_raw
                .loc[:, ['randomiser-bv5x','Participant Public ID','Zone Name','Screen Name', 'display','Trial Number','image','answer','Response','Reaction Time', 'Correct','Incorrect']]
                #.drop(df_raw[df_raw["Zone Name"] == "timer"].index) # drop timer info
                .drop(df_raw[~df_raw["Screen Name"].isin(["Mooney", "grayscale"])].index) # keep trial screens only
                #.assign(correct=lambda x: x.apply(lambda y: 1 if y['answer'] == y['Response'] else 0, axis=1))
                .assign(image=lambda x: x["image"].apply(lambda s: s[4:] if s.startswith("dis_") else s))
                .assign(keyword=lambda x: x["image"].apply(lambda s: s.split("_")[0]))            
            )
        df = pd.concat([df, df_s], ignore_index=True)

    df.rename(columns={'Participant Public ID': 'PID', 
                    'randomiser-bv5x': 'group',
                    'answer': 'category',
                    'image': 'image',
                    'display': 'condition',
                    'Reaction Time': 'RT',
                    'Response':'response',
                    'Correct':'correct',
                    'Incorrect':'incorrect',
                    'Trial Number': 'trial'
                    }, inplace=True)

    df["timeout"] = 0
    df["block"] = ""

    # rearrange columns
    df = df[['group',
            'PID',
            'Zone Name',
            'Screen Name',
            'condition',
            'block',
            'trial',
            'image',
            'category',
            'keyword',
            'response',
            'RT',
            'correct',
            'incorrect',
            'timeout']]

    # convert correct/incorrect to integers
    df['correct'] = df['correct'].astype('int')
    df['incorrect'] = df['incorrect'].astype('int')
    df['RT'] = df['RT'].astype('float')

    # sort by group, PID
    df = df.sort_values(['group', 'PID'],ascending = [True, True])
    df = df.reset_index(drop=True)

    # remove 'Group' prefix from group name
    df['group'] = df.group.str.strip('Group')

    df = check_timeout(df)
    df = add_correct_trial_block_nr(df)


    return df
