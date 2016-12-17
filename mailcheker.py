#! C:\bin\Python35\python.exe
# -*- coding: utf-8 -*-

'''
Modified for python3 on 2012/04/29
original python2 version is Created on 2011/10/30

@author: tyama
'''
import poplib, email.header
import string
import re
import urllib.request, urllib.error, urllib.parse, http.cookiejar, socket
import threading,time
import random
import mailcheker_data as config
from subprocess import check_call

'''
#sample
def decode_mime_header1(s0):
    return ''.join( str(s, c or 'ascii') if isinstance(s, (bytes,)) else s for s,c in email.header.decode_header(s0) )
'''





def decode_mime_header(st):
    decoded_st =""

    for s, enc in email.header.decode_header(st):
        try:
            if isinstance(s,str):
                decoded_st += s
            elif enc=='unknown-8bit': #case of type==bytes
                decoded_st += s.decode('Shift_JIS','ignore')
            elif enc:
                decoded_st += s.decode(enc,'ignore')
            else:
                decoded_st += s.decode('utf-8','ignore')
        except LookupError as e:
            print('encode error:',e)
        except:
            print('Unexpected error in decode, sleeping 8 sec')
            time.sleep(8)
    return decoded_st



def extract_url(msg, fromkey, payloadkey, multiurl):

    f_header = msg.get('From',str)

    # rakuten mail is not correctly decoded
    # the following replacement is useful
    if isinstance(f_header, str):
        f_header_mod = f_header.replace('==?=<','==?= <')
    else:
        f_header_mod = f_header#.encode()

    decoded_from=decode_mime_header(f_header_mod)
    url = []

    if fromkey in decoded_from:
        #print "YES"
        pattern = re.compile(payloadkey)
        for part in msg.walk():
            if part.get_content_maintype() == 'text':
                body = part.get_payload()
                enc = part.get_content_charset()
                if isinstance(body,str):
                    u_body = body
                elif enc=='unknown-8bit': #case of type==bytes
                    u_body = body.decode('Shift_JIS','ignore')
                elif enc:
                    u_body = body.decode(enc,'ignore')
                else:
                    u_body = body.decode('euc-jp','ignore')

                #print enc
                #print u_body

                if multiurl == True:
                    result = pattern.findall(u_body)
                    if result:
                        for each in result:
                            url.append(each)
                    url = list(set(url))
                    #sorted(set(url), key=url.index)
                else:
                    result = pattern.search(u_body)
                    if result:
                        url.append(result.group(1))
        return url
    else:
        return None

def isEmailTocheck(msg, fromkey):

    f_header = msg.get('From',str)

    # rakuten mail is not correctly decoded
    # the following replacement is useful
    if isinstance(f_header, str):
        f_header_mod = f_header.replace('==?=<','==?= <')
    else:
        f_header_mod = f_header#.encode()

    decoded_from=decode_mime_header(f_header_mod)

    if fromkey in decoded_from:
        return True
    else:
        return False


class http_get(threading.Thread):
    def __init__(self, url, opener, index):
        threading.Thread.__init__(self)
        self.url = url
        self.opener = opener
        self.index = index

    def run(self):
        try:
            response = self.opener.open(self.url)
            '''
            enc = response.headers.getparam('charset')
            if enc:
                print response.read().decode(enc,'ignore')
            else:
                print response.read().decode('euc-jp','ignore')
            '''
            print(self.index, self.url)
            return True
        except urllib.error.HTTPError as error:
            print ('HTTP Error')
            print(error)
        except socket.timeout as error:
            print ('Socket time out')
            print(error)
        except:
            print('Unexpected error in http-get')
            time.sleep(8)


        return None


import json

original_data = {
   'name' : 'ACME',
   'shares' : 100,
   'price' : 542.23
}



if __name__ == '__main__':

    print("Base", original_data)
    json_str = json.dumps(original_data)
    print(json_str)
    json_data = json.loads(json_str)
    print(json_data)

    server_list = config.server_list
    user_list = config.user_list
    pass_list = config.pass_list

    print(server_list)

    dl_list1=config.dl_list1
    dl_list2=config.dl_list2
    dl_list3=config.dl_list3

    dl_list=(dl_list1,dl_list2,dl_list3)

    #lines=open('setting.dat','r').readlines()
    #for line in lines:
    #    print line[:-1]


    lastuidl_lists=[]
    f=open('lastmsgid.dat','r')
    for line in f:
        lastuidl_lists.append(line.split())
    f.close()
    out_string=[]

    print(lastuidl_lists)

    print(dl_list)

    #time out
    socket.setdefaulttimeout(15.0)


    # connect to server
    cj = http.cookiejar.CookieJar()
    cjhdr = urllib.request.HTTPCookieProcessor(cj)

    opener = urllib.request.build_opener(cjhdr)
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2')]


    for j in range(len(server_list)):
        print('Start ')
        server = poplib.POP3_SSL(server_list[j])

        # login
        server.user(user_list[j])
        server.pass_(pass_list[j])

        # list items on server
        list_resp, list_items, list_octets = server.list()
        print (list_resp)
        #print (list_items)
        print (list_octets)
        uidl = server.uidl()

        lastuidl = lastuidl_lists[j]
        #print server.uidl()

        '''if j==1:
            lastuidl[1]='TEST'
        '''
        last_msg_id = 1

        x=int(lastuidl[0])

        if x > len(list_items):
            x = len(list_items)
        index=x
        print(x)
        if x==0:
            out_string.append('1')
            out_string.append('abc')
            continue
        while x > 0:
            #print (lastuidl[1], ":>", uidl[1][x-1].split()[1].decode('utf-8','ingore'))
            if lastuidl[1] == uidl[1][x-1].split()[1].decode('utf-8','ingore'):
                print('equal')
                break
            print(x)
            index=x
            x -= 1
        print(index)

        #if uidl[1][i].split()[1] == 'ANft2MsAABBhTsOb4QzFegr+jPA':
        #    print 'equal'
        #    continue

        delete_counter=0
        last_index=index
        for i in range(index, len(list_items)+1):

            try:
                #resp, text, octets = server.retr(i)
                t_resp, t_text, t_octets = server.top(i,1)
            except:
                print('Unexpected error in server.top of Main function\n')
                print('i=', i, ', index=', index)


            #print (text)'
            t_string_text = b'\n'.join(t_text)
            t_msg = email.message_from_bytes(t_string_text)

            url_list = None
            checkBody = False

            for from_key, text_key, multiurl in dl_list[j]:
                if isEmailTocheck(t_msg, from_key):
                    checkBody = True
                    break

            if checkBody:
                try:
                    resp, text, octets = server.retr(i)
                except:
                    print('Unexpected error in server.retr of Main function\n')
                    print('i=', i, ', index=', index)

                string_text = b'\n'.join(text)
                msg = email.message_from_bytes(string_text)
                for from_key, text_key, multiurl in dl_list[j]:
                    url_list = extract_url(msg, from_key, text_key, multiurl)
                    if url_list:
                        break
                        
            #print url_list
            if url_list:
                m_date = msg.get('Date')
                print(m_date)

                for each in url_list:
                    #print each
                    get=http_get(each,opener,i)
                    try:
                        get.start()
                        #server.dele(i)
                        delete_counter +=1
                        if 'r34' in each:
                            print ('Call Chrome')
                            check_call(["C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", " --disable-images", each])
                    except:
                        print('Unexpected error in Main function', each ,i)
                        time.sleep(8)

                m_subject = msg.get('Subject')
                d_subject, enc = email.header.decode_header(m_subject)[0]

                if enc is None: enc = 'euc-jp'
                try:
                    u_subject=str(d_subject, enc)
                except:
                     print('Unexpected error in u_subject', d_subject, enc)
                     time.sleep(8)
                print(i, " ", u_subject)
            else:
                print(i)
                last_index=i
                if i==6:
                    pass#quit()

        last_msg_id= len(list_items)# - delete_counter
        out_string.append(str(last_msg_id))
        out_string.append(uidl[1][last_index-1].split()[1].decode('utf-8','ignore'))

        try:
            server.quit()
        except:
            print('Unexpected error in server.quit()')

        print('End')
        print(out_string[len(out_string)-1])
    #print out_string

    time.sleep(2)
    for i in range(len(out_string)):
        if i%2: continue
        print (out_string[i])
        print (out_string[i+1])

    f=open('lastmsgid.dat','w')

    for i in range(len(out_string)):
        if i%2: continue
        f.write(out_string[i] + ' ')
        f.write(out_string[i+1] + '\n')

    f.close()


    print('END')
    time.sleep(8)
