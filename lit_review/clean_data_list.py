import os
import pandas as pd
import re

def clean_title(x):
    x2 = re.sub('^ ','',x)
    x2 = re.sub(' $','',x2)
    return x2

def clean_DOI(x,idx):
    if isinstance(x,str):
        x2 = re.sub('^ ', '', x)
        x2 = re.sub(' $', '', x2)
        x2 = re.sub('\.$', '', x2)
        if x2[0] != '1':
            x2 = '1' + x2
        return x2
    else:
        return idx

def sort_var_inc(x):
    if x in ['healthcare utilisation', ' healthcare utilisation','healthcare utilidation',
                ' health care utilisation', 'health care utilisation', 'healthcare utilidasation',
                'health care utilidation']:
        return 'healthcare utilisation'
    elif x in ['comorbiditiers', 'comorbdities',' Comorbidies','  comorbidities','comrbdities',
                  ' comorbidities', ' cormorbidities','domorbidities', 'comorbidities','Comorbidities',
                  'comorbidies']:
        return 'comorbidities'
    elif x in ['demographics', 'demographcs', 'demographic','Demographics','demogrpahics',
               ' demographics']:
        return 'demographics'
    elif x in ['Medication','medicaito','medications', 'medication', ' medication', 'medicaiton']:
        return 'medication'
    elif x in ['diagnosese',' diagnoses']:
        return 'diagnoses'
    elif x in ['lifestyle factors','lifestyle',' lifestyle',' lifestyle factors']:
        return 'lifestyle factors'
    elif x in ['biomarker',' biomarkers', 'biomarkers', 'Biomarkers']:
        return 'lab tests'
    elif x in ['symtoms', 'symptom',' symptoms', 'symptoms']:
        return 'symptoms'
    elif x in [' procedures', 'procedures', ' procedures ']:
        return 'procedures'
    else:
        return x



if __name__=='__main__':
    papers = pd.read_csv('data/raw/litreview_list.csv')
    papers = papers.reset_index()
    papers['Title'] = papers['Title'].apply(clean_title)
    papers['DOI'] = papers[['index','DOI']].apply(lambda x: clean_DOI(x[1],x[0]),axis=1)
    print(len(papers))
    papers = papers.drop_duplicates(subset='Title')
    print(len(papers))
    papers = papers.drop_duplicates(subset='DOI')
    print(len(papers))
    papers.drop(columns='index')
    papers.to_csv('data/processed/litreview_short.csv',index=False)

    lit_df = pd.read_csv('data/raw/lit_review_data.csv')
    drop_reasons = lit_df.drop_duplicates('DOI')['Discard'].value_counts().reset_index()
    drop_reasons.to_csv('data/processed/excluded_counts.csv')

    lit_short = lit_df[lit_df['Discard']=='Keep']
    lit_short = lit_short[['Title', 'URL', 'Year',
       'Disease', 'Primary or Secondary Care',
       'Uses additional data', 'Country', 'Time Type', 'Variables included',
       'N varaibles', 'N', 'Missing data', 'Feature Selection',
       'Data Transformation', 'Clustering algorithm ', 'Deciding K 1',
       'Deciding K 2', 'Deciding K 3', 'Deciding K 4', 'K',
       'Charactersing clusters', 'Internal evaluation metric 1',
       'Internal evaluation metric 2', 'Internal evaluation metric 3',
       'Internal evaluation metric 4', 'External evaluation metric 1',
       'External evaluation metric 2', 'External evaluation metric 3',
       'External evaluation metric 4']]

    vars_inc = lit_short['Variables included'].copy().tolist()
    vars_list =[j for i in vars_inc for j in i.split(',')]
    vars_set = set(vars_list)
    var_chance = [[sort_var_inc(j) for j in i.split(',')] for i in vars_inc]
    new_keys = set([j for i in var_chance for j in i])
    new_keys = [i for i in new_keys if len(i)>0]
    new_var_df = pd.DataFrame({k:[1 if k in i else 0 for i in var_chance ] for k in new_keys})
    lit_short = lit_short.reset_index(drop=True)
    lit_short2 = lit_short.join(new_var_df).drop(columns='Variables included')
    lit_short2.to_csv('data/processed/litreview_analysis.csv',index=False)
