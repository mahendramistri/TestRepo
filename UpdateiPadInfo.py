import socket
import base64
import time
import mysql.connector
import urllib2
from mysql.connector import errorcode
import logging
logging.basicConfig(filename='/var/log/iPadInfo.log',level=logging.DEBUG)
config={
        'user':'root',
        'password':'ps7778',
        'host':'172.16.0.2',
        'database':'iremote',
}

try:
        cnx=mysql.connector.connect(**config)
	curdb=cnx.cursor()
	curdb1=cnx.cursor()
except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.warning("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.warning("Database does not exists")
UDP_IP = "0.0.0.0"
UDP_PORT = 7113
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) 
while True:
	try:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		info=base64.b64decode(data)
		logging.debug(info)
		#print info,addr
		infoarray=info.split(",")
		appinfo=infoarray[3]+"("+infoarray[4]+")/iOS"+infoarray[2]
		roomnumber=infoarray[0].lower()
		if roomnumber.startswith("room"):
			roomnumber=roomnumber[4:]
        	newroomnumber = roomnumber.replace('bedroom1', 'bedroom')
		queryz="SELECT iremote, battery FROM digivalet_status WHERE CONCAT(room_no,lower(room_description)) LIKE '"+roomnumber+"' OR CONCAT(room_no,lower(room_description)) LIKE '"+newroomnumber+"'"
        	#print queryz
        	curdb.execute(queryz)
        	row = curdb.fetchone()
        	iremote=row[0]
		old_battery_str = row[1]
		new_battery_str = infoarray[1]
		logging.warning(iremote)
				
        	if iremote==0:
                	#url="http://10.80.130.102/iremote/emailalert.php?to=nirmit@casadigi.com%2Cketan.gode@digivalet.com%2Cpriyank@paragon.co.in%2Cnitin@digivalet.com&text=INFO%3A%20"+roomnumber+"%20iPad%20is%20Reachable"
                    	url="http://172.16.0.2/iremote/emailalert.php?to=bhavesh.tiwari@digivalet.com%2Cmahendra.mistri@paragon.co.in%2Carpita.bhandari@paragon.co.in%2Cmukesh.sahu@digivalet.com&text=INFO%3A%20"+roomnumber+"%20iPad%20is%20Reachable"
            		url=url.replace(' ', '%20')
			urllib2.urlopen(url)
			logging.debug("Send Reachable Mail " + url)
		
		if new_battery_str != "charging" and old_battery_str != "charging":
			try:
				old_battery = int(old_battery_str)
            			new_battery = int(new_battery_str)
				logging.debug(old_battery_str + " " + new_battery_str)
				if new_battery != old_battery and new_battery <= 20:
                                	logging.debug("************Battery less then 20***************")
					if new_battery%5==0 :
						url="http://172.16.0.2/iremote/emailalert.php?to=bhavesh.tiwari@digivalet.com%2Cmahendra.mistri@paragon.co.in%2Carpita.bhandari@paragon.co.in%2Cmukesh.sahu@digivalet.com&text=ALERT%3A iPad battery for " + roomnumber + " is only " + new_battery_str
                                        	url=url.replace(' ', '%20')
                                        	urllib2.urlopen(url)
                                        	logging.debug("Send Battery low Mail " + url)
			except Exception,e:
				logging.warning("Unable to send battery low mail "+ str(e))
			
        	query="UPDATE digivalet_status SET battery='"+infoarray[1]+"',iPad_App='"+appinfo+"',ipadts="+str(int(time.time())) +", iremote =1  WHERE CONCAT(room_no,lower(room_description)) LIKE '"+roomnumber+"' OR CONCAT(room_no,lower(room_description)) LIKE '"+newroomnumber+"'"
        	logging.warning(query)
		#print query
		curdb1.execute(query)
	except KeyboardInterrupt:
		print "keyboard intrupt"
		break
	except Exception,e:
		#logging.warning(query);
		logging.warning('Unable to update iPad Info '+ str(e))
		curdb.close()
        	curdb1.close()
		cnx.close()
		cnx=mysql.connector.connect(**config)
        	curdb=cnx.cursor()
            	curdb1=cnx.cursor()
	else:
		logging.debug('Data updated in database')
