#!/usr/bin/python3
"""Test docstring
"""
import re
import os
import subprocess
from slackclient import SlackClient
slack_client = SlackClient(os.environ.get('SLACK_CLIENT'))
api_call = slack_client.api_call('users.list', presence=False)
users = api_call.get('members')
def audit_sheet():
    names = ['1skreations','a_dc_diary','A_Lockerman','aaronyabes','abearhouse','adnrew','adventuresforalways','afg','alalyak','alexandermalati','alfred1of1','alinaqih','alliugosoliphotograph','ameowssa','amixxita','amysticallife','anabeldflux','andra.oprea','andrefphoto','andrewmarty_','antswinn','artbyabong','ashleakristina','ashleybyers','ashleysenja','Audreylanepartlow ','austin_paz','austinrspeer','averyschrader','ayoubskar','bazzana','beachbouquet','beardofshareef','bendavisual','bengrainger_','benjamin','benmurphy.photography','bielbespin','bjoerntempl','bossons','brandonyamaguchi','brianfv','britnizzlet','brknlabel','bytinekevv','caitdelphine','camillia_lee','camleeyoga','candice_vorbeck','Carltonrhodes','cartographyandcloture','cassimanner','chaitography','charbz._','charoliviap','Chasing_christina','ChelseaLeighdamon','chewoutloud','chicity_shots','chris.biersack','christian_correa','christianallenphoto','chsvirtuosi','clairebeary94','clarkfletcher','clondon','cludymudy','Codyblue_','colburn.collective','commonrejects','cormacpow','cristblackwell','cruisemonster','daisychainsupplyco','dan_mateus','daniel_sheppard','danielcbtavares','DanielKoehler','danleephoto','Davidnyk','deanpags','depth.of.reality','derekrliang','desgettier','destinationweddingdet','divi.mangla','dopexposure','drewmedica','dutchwnderer','dyllan_khawam','e_alejandro','em.town','emanzi','emilywrdh','emmaamies','eric.aydin.barberini','eric.mears','erkanyvas','ethanknoll.photo','eyk_blog','fabricated_minds','faceycowler','Farewhispers','faycalmarjane','flywithhani','focal.pt','foreverwanderinginlif','fotokites','francoisbeyers','freedomvisual','freireweddingphoto','fvanpuyenbroeck','gabriel.baldasari','garyhebding','gastrotravelogues','genevasandss','gillian__photography','goingplacesphysically','griffinolis','gwenruais','h.f.photo','hamb0y','hammerspb','hangingpixels_photo_a','hansonsenhancements','hdoria','heidilynnephoto','herconfetti','heydanking','heyitsj0n','heysluggage','heytheremeesh','homebyforesee','honestlymarketing','i_cirkovic','IamJanFreire','iamliesamaria','iamsantifox','ido8all','ikinphillips','imwithloewer','indiatraveladventure','inspiringreflections','irahok','irenebel_photography','ironak','its_glorial','itscarmenhong','jaadyth','jack_in_nature','jacobs105','jahmeirgraham','jahnatrie','jaimemoreiraa','jakobstanley','jareddallen','jbshutter','jeanpouabou','jeffandmichelephoto','jeffcolhoun','jefferymurphy','jeltown','jennajones','jessica.yahn','jessie_19970307','jillianmgale','jillmarjeanwagner','jmartinevents','jmattcorbin','joblogsandtakespictur','Jon.bachtold','jonnybernardino','jonpak','jonsams.jpg','josekasek','josh_krobe','joshphotoadventures','joshua.laplap','joshuadthorne','journey_so_far','julesk0','just.cajon','kaanatilaisik','kamagnusson','kendaldockery','kergozou','kev_anh','kevin.xyi','kevinhoehne','Kevmbautista','keyshank','killahwave','kistymea','kitchenscientists ','knitsafari','kodidustinphotography','krashek','Kriks','kyle____peterson','l0cals','lafrikidelaleica','laurelinann','lekophoto','leomoyano','lesmiserables','littlevictah','lonelyonly4u','louisraphael','m4everpics','ma1inowski','malev','manolobrown','marijnkuiper','marz26','mashagreeg','megan.sweeting','mellerobot','meredithwashburn','metalliquin','metinogurluu','milomethod','MollyMakesFood','mominstilettosblog','monicamendozaaa','mrtriumph','mszpauline','murdrae','mxmadsen','nemidani','newyorkvirtuosi','nic.furlong','nickipollack','nicolexzittel','nikkij','noelhigareda','odnabtoronto','oladimeg','oladimeg','olisebastianphoto','pat_hikes_co','Peachhatesyou','peterkiral','photog_uri','photography.gbt','photosbyty98','pizzaandpumps','portraitsbysudansh','preetpraylove','primexcel','pterhx','pureframed','rachelannettehelson','richerpoorer','roadstowilderness','ronderrek','ruan.bekker','ryanstefanphoto','s.rob_','salinakaylor','sboimov','Scouttheearth','sheyaar','silent.skream','sinthography','snitpherspective','socallednatalie','sotanakethphotography','sounds_app','Stateology','stefanofull','stephanievanderauwera','stephjfs','strangefarmhouse','stronglobee','sufyan_nr1','svargg','talhastrike','taz0tealeaves','teeemcha','that.coffeeguy','the_roadtripper','thearianasoleil','theeverydayfoodie','thekevinchxw','thelightrecord','theloveliestlily','themarkdalton','themidtime','theolister','thezenomads','thruthickthin','tminspired','tobylynnphotography','tofutraveler','tomcarman','tomcochrane','tothewolves.co','Travelers_Memoire','travelreign','trentniino','u1markut','ujjwalchande','veefaceswest','verbala','veronicapgg','victorianelsonn','vitor.esteves','wander.licious','willardhannah','willstrath','xjtian','yalinky','ygwengrace','yourstoryfilmandphoto','yusufex','zombiesofthenight','calimanders','mandii.creates','wanderlosangeles','shotsbytots','thanh.tastic','dccitygirl','dawninoc','Desgettier','Vitto_riana','shutterhero','markmackoviak','arwin.l','bellarosehickling','curtis.strange','FredSpigelman','theprintableconcept','Weeling88','Explauradise','micktographer','g.e.r.m.s','zuzanacloud','the_bluecloud','Sufyan_Nr1','roving.rivera','607rez']
    found = False
    for sheet_name in names:
        found = False
        for user in users:
            if 'name' in user and user.get('name').lower() == sheet_name.lower() and (not user.get('deleted')):
                found = True
                print(user.get('name') + '\t' + user.get('id'))
        if not found:
            print(sheet_name + '\tMissmatch')
def test_user(userinfo):
    found = False
    for user in users:
        if 'name' in user and user.get('name').lower() == userinfo.lower():
            found = True
            print(user)
        if 'id' in user and user.get('id') == userinfo.upper():
            found = True
            print (user)
        if found:
            break
    if not found:
        print('Could not find any user with that name')
def main():
    if api_call.get('ok'):
        audit_sheet()
       #test_user('leech_detector')
    else:
        print('There was a problem connecting to the slack client')
if __name__ == "__main__":
    main()
