!pip install streamlit
# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# One-page CKD Dashboard
st.set_page_config(page_title='CKD Dashboard', layout='wide')

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_kidney_disease.csv')
    df['class'] = df['class'].map({'Chronic Kidney Disease': 1, 'Not Chronic Kidney Disease': 0})
    bins = [0, 30, 50, 70, df['age'].max() + 1]
    labels = ['<30', '30-50', '50-70', '70+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    return df

df = load_data()

st.title('Chronic Kidney Disease Dashboard')

# Key Metrics
col1, col2 = st.columns(2)
col1.metric('Total Patients', len(df))
col2.metric('CKD Prevalence', f"{df['class'].mean() * 100:.1f}%")

# Prevalence by Age Group
st.subheader('CKD Prevalence by Age Group')
age_prev = df.groupby('age_group')['class'].mean() * 100
fig, ax = plt.subplots()
age_prev.plot(kind='bar', color='teal', ax=ax)
ax.set_ylim(0, 100)
ax.set_ylabel('% with CKD')
for i, v in enumerate(age_prev):
    ax.text(i, v + 1, f"{v:.1f}%", ha='center')
st.pyplot(fig)

# Serum Creatinine Distribution
st.subheader('Serum Creatinine by CKD Status')
fig, ax = plt.subplots()
sns.boxplot(x='class', y='serum_creatinine', data=df, palette='Set2', ax=ax)
ax.set_xticklabels(['Non-CKD', 'CKD'])
ax.set_ylabel('Creatinine (mg/dL)')
st.pyplot(fig)

# Key Risk Factors (Odds Ratios)
st.subheader('Key Risk Factors (OR)')
factors = ['hypertension', 'diabetes_mellitus']
or_vals = {}
for var in factors:
    tab = pd.crosstab(df[var], df['class']) + 0.5
    a, b = tab.loc[1, 1], tab.loc[1, 0]
    c, d = tab.loc[0, 1], tab.loc[0, 0]
    or_vals[var.replace('_', ' ').title()] = (a / b) / (c / d)
or_df = pd.DataFrame.from_dict(or_vals, orient='index', columns=['Odds Ratio']).sort_values('Odds Ratio')
fig, ax = plt.subplots()
or_df['Odds Ratio'].plot(kind='barh', color='orange', ax=ax)
ax.set_xlabel('Odds Ratio')
for i, v in enumerate(or_df['Odds Ratio']):
    ax.text(v + 0.1, i, f"{v:.1f}")
st.pyplot(fig)

# Incidence of Key Abnormal Findings
st.subheader('Incidence of Abnormal Findings (%)')
defs = {
    'High Creatinine': df['serum_creatinine'] > 1.2,
    'Low Hemoglobin': df['hemoglobin'] < 12,
    'Proteinuria': df['albumin'] > 0
}
inc_data = []
for name, cond in defs.items():
    non = cond[df['class'] == 0].mean() * 100
    ck = cond[df['class'] == 1].mean() * 100
    inc_data.append([non, ck])
inc_df = pd.DataFrame(inc_data, index=defs.keys(), columns=['Non-CKD %', 'CKD %'])
fig, ax = plt.subplots(figsize=(6, 3))
sns.heatmap(inc_df, annot=True, fmt='.1f', cmap='coolwarm', ax=ax)
ax.set_ylabel('')
st.pyplot(fig)
