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
    names = ['drewmedica','1skreations','a_dc_diary','a_Lockerman','aaronyabes','adnrew','adventuresforalways','ahcolburn','alalyak','alexandermalati','alfred1of1','alinaqih','alliugosoliphotograph','ameowssa','amixxita','amysticallife','anabeldflux','andra.oprea','andrefphoto','andrewmarty_','antswinn','ashleakristina','ashleysenja','Audreylanepartlow','austin_paz','averyschrader','ayoubskar','bazzana','beachbouquet','beardofshareef','bearhouse','bendavisual','bengrainger_','benjamin','benmurphy.photography','bjoerntempl','brandonyamaguchi','brianfv','britnizzlet','brknlabel','bytinekevv','cabaphotography','candice_vorbeck','Carltonrhodes','cartographyandcloture','cassimanner','chaitography','charbz._','charoliviap','chewoutloud','chicity_shots','chris.biersack','christian_correa','christianallenphoto','clairebeary94','clarkfletcher','Codyblue_','commonrejects','cormacpow','cristblackwell','cruisemonster','daisychainsupplyco','dan_mateus','daniel_sheppard','danielcbtavares','danleephoto','deanpags','depth.of.reality','derekrliang','desgettier','destinationweddingdet','divi.mangla','dutchwnderer','dyllan_khawam','e_alejandro','em.town','emanzi','emmaamies','eric.aydin.barberini','eric.mears','erkanyvas','ethanknoll.photo','eyk_blog','faceycowler','Farewhispers','faycalmarjane','flywithhani','focal.pt','foreverwanderinginlif','fotokites','francoisbeyers','freedomvisual','freireweddingphoto','fvanpuyenbroeck','gabriel.baldasari','garyhebding','gastrotravelogues','genevasandss','gillian__photography','goingplacesphysically','griffinolis','gwenruais','h.f.photo','hamb0y','hangingpixels_photo_a','hansonsenhancements','hdoria','heidilynnephoto','henry_popiolek','herconfetti','heydanking','heyitsj0n','heysluggage','heytheremeesh','homebyforesee','honestlymarketing','i_cirkovic','iamliesamaria','iamsantifox','ido8all','ikinphillips','indiatraveladventure','inspiringreflections','irahok','irenebel_photography','ironak','its_glorial','itscarmenhong','jaadyth','jack_in_nature','jacobs105','jahmeirgraham','jahnatrie','jaimemoreiraa','jakobstanley','jareddallen','jbshutter','jeanpouabou','jeffandmichelephoto','jefferymurphy','jeltown','jennajones','jessica.yahn','jessie_19970307','jmartinevents','jmattcorbin','joblogsandtakespictur','Jon.bachtold','jonnybernardino','jonpak','jonsams.jpg','josekasek','josh_krobe','joshphotoadventures','joshua__dantes','joshua.laplap','joshuadthorne','journey_so_far','julesk0','just.cajon','kaanatilaisik','kamagnusson','kendaldockery','kergozou','kev_anh','kevin.xyi','kevinhoehne','keyshank','kistymea','knitsafari','kodidustinphotography','krashek','kyle____peterson','l0cals','laurelinann','leomoyano','lesmiserables','littlevictah','lonelyonly4u','louisraphael','m4everpics','ma1inowski','malev','manolobrown','marijnkuiper','marz26','megan.sweeting','mellerobot','meredithwashburn','metalliquin','metinogurluu','monicamendozaaa','mominstilettosblog','mszpauline','murdrae','nemidani','newyorkvirtuosi','nic.furlong','nikkij','noelhigareda','oladimeg','olisebastianphoto','pat_hikes_co','photog_uri','photography.gbt','photosbyty98','portraitsbysudansh','preetpraylove','primexcel','pterhx','pureframed','rachelannettehelson','richerpoorer','roadstowilderness','ronderrek','ruan.bekker','ryanstefanphoto','s.rob_','salinakaylor','sboimov','Scouttheearth','silent.skream','sinthography','sm_rt','snitpherspective','socallednatalie','sotanakethphotography','sounds_app','Stateology','stefanofull','stephjfs','strangefarmhouse','stronglobee','talhastrike','tallielieberman','taz0tealeaves','teeemcha','that.coffeeguy','thearianasoleil','theeverydayfoodie','theinstantology','thekevinchxw','theloveliestlily','themarkdalton','themidtime','theolister','thezenomads','thruthickthin','tminspired','tobylynnphotography','tofutraveler','tomcarman','tomcochrane','tothewolves.co','travelreign','travelure','u1markut','ujjwalchande','veefaceswest','verbala','veronicapgg','wander.licious','willstrath','yalinky','yehitsgrace','yourstoryfilmandphoto','yusufex','zeteny','zombiesofthenight','mrtriumph','fabricated_minds','lekophoto','Kevmbautista','imwithloewer','milomethod','Chasing_christina','dopexposure','austinrspeer','jillianmgale','bossons','lafrikidelaleica','Davidnyk','kitchenscientists','pizzaandpumps','mxmadsen','emilywrdh','IamJanFreire','vitor.esteves','clondon','mashagreeg','MollyMakesFood','stephanievanderauwera','camleeyoga','camillia_lee','svargg','trentniino','xjtian','thelightrecord','Thanh.tastic','Peachhatesyou','nicolexzittel','DanielKoehler','bielbespin','victorianelsonn','Kriks','jillmarjeanwagner','Travelers_Memoire','sufyan_nr1','hammerspb','afg','sheyaar','oladimeg','the_roadtripper','odnabtoronto','killahwave','cludymudy']
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
        #audit_sheet()
        test_user('leech_detector')
    else:
        print('There was a problem connecting to the slack client')
if __name__ == "__main__":
    main()
