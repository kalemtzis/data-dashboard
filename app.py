import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
@st.cache_data
def load_data():
    ds = pd.read_csv('data/covid_data.csv')
    
    ds.rename(columns={
        'referencedate': 'date',
        'area': 'region',
        'daytotal': 'daily_cases',
        'daydiff': 'case_diff',
        'totalvaccinations': 'total_vaccinations',
        'totaldistinctpersons': 'vaccinated_people',
        'dailydose1': 'dose1_daily',
        'dailydose2': 'dose2_daily',
        'dailydose3': 'dose3_daily',
        'totaldose1': 'dose1_total',
        'totaldose2': 'dose2_total',
        'totaldose3': 'dose3_total'
    }, inplace=True)
    
    ds['date'] = pd.to_datetime(ds['date'])
    
    col_to_clip = ['daily_cases', 'case_diff', 'dose1_daily', 'dose2_daily', 'dose3_daily']
    ds[col_to_clip] = ds[col_to_clip].clip(lower=0)
    
    return ds


if __name__ == '__main__':
    # Set-Up Page
    st.set_page_config(page_title='Greek COVID Dashboard', layout='wide')
    st.title('📊 Greek COVID Dashboard')
    st.markdown('Εξερεύνησε τα δεδομένα COVID-19 στην Ελλάδα.')
    
    ds = load_data()
    
    # ===========================
    # Sidebar: Φίλτρα & Εργαλεία
    # ===========================
    st.sidebar.header('🔍 Φίλτρα')
    
    # Επιλογή ημερομηνιακού εύρους
    min_date = ds['date'].min()
    max_date = ds['date'].max()
    date_range = st.sidebar.date_input(
        'Επιλογή εύρους ημερομηνιών:', 
        value=(min_date, max_date), 
        min_value=min_date, 
        max_value=max_date
    )
    
    # Επιλογή/Αναζήτηση περιοχής
    region = st.sidebar.selectbox('Επίλεξε περιφέρεια', ['Όλες'] + sorted(ds['region'].unique()))
    
    # Φιλτράρισμα δεδομένων
    filtered_ds = ds.copy()
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_ds = filtered_ds[(filtered_ds['date'] >= start_date) & (filtered_ds['date'] <= end_date)]
    if region != 'Όλες':
        ds = ds[ds['region'] == region]
    
    # ===========================   
    # Κουμπί για Εξαγωγή σε CSV
    # ===========================  
    csv_data = filtered_ds.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label='📤 Εξαγωγή CSV',
        data=csv_data,
        file_name='filtered_covid_data.csv',
        mime='text/csv'
    )
    
    # ===========================
    # Μετρικές
    # ===========================
    st.subheader('📌 Βασικά Στατιστικά')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Συνολικά Κρούσματα', f'{ds['daily_cases'].sum():,}')
    col2.metric('Μέσος Όρος/Ημέρα', f'{ds['daily_cases'].mean():.2f}')
    col3.metric('Μέγιστο Ημερήσιο', f'{ds['daily_cases'].max()}')
    col4.metric('Συνιλικά Εμβόλια', f'{ds['total_vaccinations'].max():,}')

    # ===========================
    # Bar Chart
    # ===========================
    st.subheader('📊 Κρούσματα ανά Περιοχή')
    
    bar_data = filtered_ds.groupby('region')['daily_cases']\
        .sum()\
        .reset_index()\
        .sort_values('daily_cases', ascending='False')
    
    fig_bar = px.bar(
        bar_data,
        x='daily_cases',
        y='region',
        orientation='h',
        color='daily_cases',
        color_continuous_scale='reds',
        labels={'daily_cases': 'Σύνολο Κρουσμάτων', 'region': 'Περιοχή'},
        title='Σύνολο Κρουσμάτων ανά Περιοχή'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # ===========================
    # Pie Chart
    # ===========================
    st.subheader('🧩 Κατανομή Τύπων Εμβολιασμού (Μ.Ο. ημερήσιων δόσεων)')
    
    pie_data = filtered_ds[['dose1_daily', 'dose2_daily', 'dose3_daily']].mean()
    
    fig_pie = px.pie(
        values=pie_data.values,
        names=['Δόση 1', 'Δόση 2', 'Δόση 3'],
        title='Μέση Ημερήσια Κατανομή Δόσεων'
    )
    st.plotly_chart(fig_pie)
    
    # ===========================
    # Heat Map
    # ===========================
    st.subheader('🔥 Heatmap Κρουσμάτων')
    
    heatmap_data = filtered_ds.groupby(['date', 'region'])['daily_cases'].sum().reset_index()
            
    heatmap_pivot = heatmap_data.pivot(index='region', columns='date', values='daily_cases').fillna(0)
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x='Ημερομηνία', y='Περιοχή', color='Κρούσματα'),
        aspect='auto',
        color_continuous_scale='Reds'
    )
    fig_heatmap.update_layout(title='Ημερήσια Κρούσματα ανά Περιοχή')
    st.plotly_chart(fig_heatmap, use_container_width=True)
