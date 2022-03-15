import streamlit as st

import pandas as pd

import requests

from bs4 import BeautifulSoup

 

st.title('ANALYSE OPCVM')

 

def opcvm(opcvm,datalengh):

    stringgiven = opcvm

 

    URL = f"https://google.com/search?q={stringgiven}+boursorama+objectif+investissement"

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

 

    resp = requests.get(URL, headers=headers)

    googlelinks=[]

 

    if resp.status_code == 200:

        soup = BeautifulSoup(resp.content, "html.parser")

        href = soup.find_all('div')

        for x in href:

            href2 = x.find_all('a')

            for y in href2:

                link = y.get('href')

                if link != None and link.startswith("https://www.boursorama.com"):

                    googlelinks.append(link)

        googlelink=googlelinks[0]

 

    result = requests.get(googlelink, headers=headers)

    soup = BeautifulSoup(result.text, 'html.parser')

    Name = soup.find_all('h1')[0].get_text().strip()

 

    i=0

    valueid=0
    

    while i<len(soup.find_all('p')):

        if soup.find_all('p')[i].get_text().strip()=="Catégorie générale":

            valueid = i

        i+=1

 

    if valueid!=0:

        Categoriegen = soup.find_all('p')[valueid+1].get_text().strip()

        Categoriems = soup.find_all('p')[valueid+3].get_text().strip()

        CategorieAMF = soup.find_all('p')[valueid+5].get_text().strip()

        FormeJur = soup.find_all('p')[valueid+7].get_text().strip()

        Name = str(Name)[5:].strip()


    boursocode=googlelink.split("/")[-2]
    
    ###PERFORMANCES / RISQUES
    URL = 'https://www.boursorama.com/bourse/opcvm/cours/performances-risques/'+boursocode
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all("td", {"class": "c-table__cell c-table__cell--dotted"})

    index = 0
    value_delta=0
    indicateurs = {}

    for table in tables:
        table = table.getText().replace(" ","").replace("\n","")
        if (table =="-" and index<5):
            value_delta+=1/2
        if index==5+value_delta:
            indicateurs["Volatilité_1an"]=table
        if index==6+value_delta:
            indicateurs["Alpha_1an"]=table
        if index==7+value_delta:
            indicateurs["R2_1an"]=table
        if index==8+value_delta:
            indicateurs["Beta_1an"]=table
        if index==13+value_delta:
            indicateurs["Volatilité_3ans"]=table
        if index==14+value_delta:
            indicateurs["Alpha_3ans"]=table
        if index==15+value_delta:
            indicateurs["R2_3ans"]=table
        if index==16+value_delta:
            indicateurs["Beta_3ans"]=table
        if index==21+value_delta:
            indicateurs["Volatilité_5ans"]=table
        if index==22+value_delta:
            indicateurs["Alpha_5ans"]=table
        if index==23+value_delta:
            indicateurs["R2_5ans"]=table
        if index==24+value_delta:
            indicateurs["Beta_5ans"]=table
        if index==29+value_delta:
            indicateurs["Volatilité_10ans"]=table
        if index==30+value_delta:
            indicateurs["Alpha_10ans"]=table
        if index==31+value_delta:
            indicateurs["R2_10ans"]=table
        if index==32+value_delta:
            indicateurs["Beta_10ans"]=table
        index+=1

    ###COMPOSITION
    URL = 'https://www.boursorama.com/bourse/opcvm/cours/composition/'+boursocode
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    scripts = soup.find_all('script')

    for script in scripts:
        script = str(script).replace(r"\u00e8","è").replace(r"\u00e9","é")

        keyword_regional = script.find('"id":"regional"')
        keyword_portfolio = script.find('"id":"portfolio"')
        keyword_sector = script.find('"id":"sector"')

        #REGIONAL
        if keyword_regional!=-1:
            regional = {}
            splitscript = script.split('[{')[1]
            temporary = ("[{"+splitscript.split('}]')[0]+"}]")
            temporary = temporary.replace('{"name":"',"").replace('"value":',"").replace('"','').replace('}','').replace("[","").replace("]","")
            temporary = list(temporary.split(','))
            for elem in temporary:
                if temporary.index(elem)%2==0:
                    previous_value=elem
                else:
                    regional[previous_value]=elem

        #PORTFOLIO
        if keyword_portfolio!=-1:
            portfolio = {}
            splitscript = script.split('[{')[1]
            temporary = ("[{"+splitscript.split('}]')[0]+"}]")
            temporary = temporary.replace('{"name":"',"").replace('"value":',"").replace('"','').replace('}','').replace("[","").replace("]","")
            temporary = list(temporary.split(','))
            for elem in temporary:
                if temporary.index(elem)%2==0:
                    previous_value=elem
                else:
                    portfolio[previous_value]=elem


        #SECTOR
        if keyword_sector!=-1:
            sector = {}
            splitscript = script.split('[{')[1]
            temporary = ("[{"+splitscript.split('}]')[0]+"}]")
            temporary = temporary.replace('{"name":"',"").replace('"value":',"").replace('"','').replace('}','').replace("[","").replace("]","")
            temporary = list(temporary.split(','))
            for elem in temporary:
                if temporary.index(elem)%2==0:
                    previous_value=elem
                else:
                    sector[previous_value]=elem

    #Cookies valide pour 1 semaine

    cookies = {'RT': '"z=1&dm=boursorama.com&si=1spfv37lz4i&ss=khorg5kz&sl=1&tt=4fo&bcn=%2Fbucky%2Fv1%2Fsend%2F&ld=4fx"'}

 

    boursocode=googlelink.split("/")[-2]

    perflink ="https://www.boursorama.com/bourse/action/graph/ws/download?length={}&period=-2&symbol={}".format(datalengh,boursocode)

    r = requests.get(perflink, headers=headers, cookies=cookies)

    lines = r.content.decode("utf-8").replace("00:00","").split('\r\n')

 

    first_line=0

 

    for line in lines:

        if first_line==0:

            df = pd.DataFrame(columns=line.split('\t')[:-1])

            first_line+=1

        else:

            try:

                df.loc[len(df)] = line.split('\t')[:-1]

            except:

                pass

    df['clot'] = df['clot'].astype(float)

    #df = df.set_index('date')

    try:

        return df,Name,FormeJur,Categoriegen,Categoriems,CategorieAMF,regional,portfolio,sector,indicateurs

    except:

        return df
opcvm_choice = st.text_input("Nom et/ou code ISIN de l'OPCVM", "")

 

selectbox = st.selectbox("Quantité de données : ",["1 Mois", "3 Mois", "6 Mois", "1 An", "3 Ans", "5 Ans", "10 Ans"])

 

datadict = {"1 Mois":30,"3 Mois":90,"6 Mois":180,"1 An":365,"3 Ans":365*3,"5 Ans":365*5,"10 Ans":365*10}

 

datalengh = datadict[selectbox]

 

finish = st.button("Générer")

 

if opcvm_choice !="" and datalengh!=0 and finish:

    alls = opcvm(opcvm_choice,datalengh)

    try:

        df = alls[0]

        st.text("Nom de l'OPCVM : "+alls[1])

        st.text("Forme juridique : "+alls[2])

        st.text("Categorie générale : "+alls[3])

        st.text("Categorie MorningStar : "+alls[4])

        st.text("Categorie AMF : "+alls[5])

        st.text("Répartition géographique : "+str(alls[6]))
    
        st.text("Répartition sectorielle : "+str(alls[8]))

        st.text("Répartition classe d'actif : "+str(alls[7]))

        st.text("Indicateurs techniques : "+str(alls[9]))

    except:

        df = alls[0]

    st.dataframe(df.set_index('date'))

    st.line_chart(df['clot'])
