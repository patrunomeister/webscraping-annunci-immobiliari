#!/usr/bin/env python

import scraperwiki
import requests
import parslepy
import pprint
import urlparse
import string 
import datetime


#usa parslepy per individuare i dati da screpare sulla pagina degli annunci http://www.subito.it/annunci-emilia-romagna/vendita/appartamenti/

rules = {
    "annunci(.list li)": [
        {
        "annuncio_url":           "div[class=th_box]  a @href",
        "annuncio_desc":          "div[class=descr]  p a strong",
        "annuncio_ora":           "div[class=date]",
        }
    ],
    "next_page_url": ".//a[contains(., 'Avanti')]/@href",
}

#usa parslepy per individuare i dati da screpare sulla pagina di dettaglio del singolo annuncio
detrules = {
      
        "info(div.annuncio_info li)": [{
         "item": ".",
         
         }],
        "coord": ".//script[contains(., 'loadMapQuest')]",
}


parselet = parslepy.Parselet(rules)
detparselet = parslepy.Parselet(detrules)

#inserire qui l'url della regione. Per la Basilicata sarà ad esempio http://www.subito.it/annunci-basilicata/vendita/appartamenti/

next_url = "http://www.subito.it/annunci-emilia-romagna/vendita/appartamenti/"

while next_url:
    
    print "fetching", next_url
    current_url = next_url

    # ottiene il contenuto della pagina
    html = requests.get(next_url)

   
    extracted = parselet.parse_fromstring(html.content)
    
    for release in extracted.get("annunci"):
        
        
        dethtml = requests.get("http://www.subito.it/"+release['annuncio_url'])
		
		#accede al contenuto della pagina di dettaglio dell'annuncio
        detextracted = detparselet.parse_fromstring(dethtml.content)
        pprint.pprint(detextracted)
		
        #print "dettagli", detextracted
        b=""
        b = detextracted.get("coord")
        a = detextracted.get("item")
        prezzo=""
        comune=""
        locali=""
        superficie=""
        lat=""
        lng=""
        for detrelease in detextracted.get("info"):
            if string.find(detrelease["item"], "Prezzo")==0:
                prezzo=detrelease["item"][6:-2]
            if string.find(detrelease["item"], "Comune")==0:
                comune=detrelease["item"][6:]
            if string.find(detrelease["item"], "Locali")==0:
                locali=detrelease["item"][6:]
            if string.find(detrelease["item"], "Superficie")==0:
                superficie=detrelease["item"][10:-2]
      
        s1 = string.find(repr(b), "lat")
        sub1=repr(b)[s1+4:]
        e1 = string.find(sub1, ",")
        l1 = len(sub1)
        lat=sub1[:-l1+e1]
        
        s2 = string.find(repr(b), "lng")
        sub2=repr(b)[s2+4:]
        e2 = string.find(sub2, "}")
        l2 = len(sub2)
        lng=sub2[:-l2+e2]
        
        
       #non ditemi niente. Non ho trovato una soluzione migliore per ottenere la data! :-)
            
        if string.find(release['annuncio_ora'], "Oggi")==0:
            today=datetime.date.today ()
            gg=today.strftime("%d/%m/%Y")
        else:
            if string.find(release['annuncio_ora'], "Ieri")==0:
                yesterday = datetime.date.today () - datetime.timedelta (days=1) 
                gg=yesterday.strftime ("%d/%m/%Y") 
            else:
                g=release['annuncio_ora'][:-9]
                m=release['annuncio_ora'][3:-5]
                if m=='gen': mm='01'
                elif m=='feb': mm='02'
                elif m=='mar': mm='03'
                elif m=='apr': mm='04'
                
                gg=g+"/"+mm+"/2014"
                
                
            
       
        data = {
            'giorno' : gg,
            'url' : "http://www.subito.it/"+release['annuncio_url'],
            'desc' : release['annuncio_desc'],
            'prezzo' : prezzo,
            'comune' : comune,
            'locali' : locali,
            'superficie' : superficie,
            'lat': lat,
            'lng': lng,
            #'comune' : comune,
            #'superficie' : superficie,
            
        }    
        
        
        scraperwiki.sql.save(unique_keys=['giorno','url','desc','prezzo','comune','locali','superficie','lat','lng'], data=data)

    # verivica se se c'è una ulteriore pagina da screpare
    
    if "next_page_url" in extracted:
        next_url = urlparse.urljoin(
            current_url,
            extracted["next_page_url"])
        
        # verifica se la pagina è l'ultima

        if next_url == current_url:
            break
        
        print "next URL to fetch", next_url
    else:
       
        next_url = None



# Saving data:
# unique_keys = [ 'id' ]
# data = { 'id':12, 'name':'violet', 'age':7 }
# scraperwiki.sql.save(unique_keys, data)
