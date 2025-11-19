from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer, FunctionTransformer, OneHotEncoder
import seaborn as sns

# Test to verify the null impact of the missing values in a numerical variable
def Diagnose_MV_Numerical(df,str_att_name,BM_MV):
    MV_labels = {True:'With Missing Values',False:'Without Missing Values'}

    labels=[]
    box_sr = pd.Series('',index = BM_MV.unique())
    for poss in BM_MV.unique():
        BM = BM_MV == poss
        box_sr[poss] = df[BM][str_att_name].dropna()
        labels.append(MV_labels[poss])

    plt.boxplot(box_sr,vert=False)
    plt.yticks([1,2],labels)
    plt.xlabel(str_att_name)
    plt.show()

    plt.figure(figsize=(10,4))

    att_range = (df[str_att_name].min(),df[str_att_name].max())

    for i,poss in enumerate(BM_MV.unique()):
        plt.subplot(1,2,i+1)
        BM = BM_MV == poss
        df[BM][str_att_name].hist(bins=50)
        plt.xlim = att_range
        plt.xlabel(str_att_name)
        plt.title(MV_labels[poss])

    plt.show()

    group_1_data = df[BM_MV][str_att_name].dropna()
    group_2_data = df[~BM_MV][str_att_name].dropna()

    p_value = ttest_ind(group_1_data,group_2_data).pvalue

    print('p-value of t-test: {}'.format(p_value))

#Graph to show the importance of the features
def pred_feature_importances_table(df):

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6)) 

    sns.barplot(
        data=df,
        x='Importance',
        y='Variable',
        color="#276ef1",
        ax=ax
    )

    ax.set_xlabel("Feature importance", fontweight='bold')
    ax.set_ylabel("Feature", fontweight='bold')
    
    # Ajustar el layout
    plt.tight_layout()
    return fig