from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import urllib.parse as urllib
import os
import re
import time
from searchengine import SearchEngine
"""
This is a response, that server sends back to the client
1st peace without from and data
"""

database_name = 'database\\database'
resp = """<html>
    <head>
        <title>ASXER (Anya's Super indeXER)</title>
        <style>
            body{background-color: #2F4F4F;font-family: sans-serif; color: #B8860B;}
            h1{border-bottom: 3px solid #DAA520;padding-bottom: 5px;}
            input{font-size: 14px; border: 3px solid #C71585;border-radius: 20px;padding: 6px; background-color: #2F4F4F;color:#FFB6C1;;width: 70%}
            input:focus{outline: none;}
            input[type=submit]{background-color: #C71585;width: auto;}
            strong{color:#DC143C;}
            ol{text-align: left;}
        </style>
    </head>"""
data = """<body>
        <div align="center">
            <form method="post">
                <h1>Enter query to search</h1>
                <input type="text" name="query" value="{0}"><br>
                <input type="submit" value="SEARCH"><br>
                {1}
            </form>
            <br><br>
            <sub>&copy; ASXER (Anya's Super indeXER)</sub>
        </div>
    </body>
</html>
"""

class WebServer(BaseHTTPRequestHandler):
    """
    This class is used for request handling in our searchengine
    """
    def do_GET(self):
        """
        Defaut get request from client to get site
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        response = """
        Documents Limit<br><input type="text" name="limit" value="0"><br>
        Documents Offset<br><input type="text" name="offset" value="0"><br>
        """
        files = os.listdir("books\\")
        i = 0
        for file in files:
            response += (file + "<br>")
            response += 'Limit<br><input type="text" name=doc'+str(i)+'limit value="0"><br>'
            response += 'Offset<br><input type="text" name=doc'+str(i)+'offset value="0"><br>'
            response += '<input type="submit" name=action'+str(i)+' value="perv">'
            response += '<input type="submit" name=action'+str(i)+' value="back">'
            response += '<input type="submit" name=action'+str(i)+' value="next"> <br>'
            i = i + 1
        self.wfile.write(bytes((resp + data.format('', response)), "utf-8"))


    def get_new_offset_limit(self, action='', action_doc='', offsets=[], limits=[]):
        '''
        function for getting next/prev results of research
        :param action: next or back or perv
        :param action_doc: for which document
        :param offsets: offsets list
        :param limits: limits list
        :return: new offsets list
        '''
        doc_num = int(action_doc.replace('action', ''))
        print(action)
        if action == 'next':
            offsets[doc_num] = str(int(offsets[doc_num]) + int(limits[doc_num]))
        if action == 'back':
            offsets[doc_num] = str(int(offsets[doc_num]) - int(limits[doc_num]))
            if int(offsets[doc_num]) < 0:
                offsets[doc_num] = str(0)
        if action == 'perv':
            offsets[doc_num] = str(0)
        return offsets


    def parse_url(self, body=''):
        '''
        function for parsing request string
        :param body: string with parameters of request
        :return: parsed parameters
        '''
        s = unquote(urllib.urlparse(body)[2], "utf-8").replace("b'", "").replace("'", "").replace("\"", '')
        query_data = urllib.parse_qs(s)
        print("data = " + str(query_data))
        query = str(query_data['query'][0])
        limit = str(query_data['limit'][0])
        offset = str(query_data['offset'][0])
        if (re.match('\D', limit)) or (re.match('\D', offset)):
            raise TypeError
        if int(limit) < 0 or int(offset) < 0:
            raise TypeError
        action = ''
        action_doc = ''
        limits = []
        offsets = []
        action_exists = False
        for key in query_data.keys():
            if re.match('action.', key):
                action = str(query_data[key][0])
                action_doc = str(key)
                action_exists = True
            if re.match('doc.limit', key):
                if (re.match('\D', query_data[key][0])) or (int(query_data[key][0]) < 0):
                    raise TypeError
                limits.append(unquote(query_data[key][0]))
            if re.match('doc.offset', key):
                if (re.match('\D', query_data[key][0])) or (int(query_data[key][0]) < 0):
                    raise TypeError
                offsets.append(unquote(query_data[key][0]))
        return query, limit, offset, limits, offsets, action, action_doc, action_exists

    def do_POST(self):
        """
        POST handler for query
        """
        #try:
        content_length = int(self.headers['Content-Length'])
        body = str(self.rfile.read(content_length))
        print("body = " + body)
        query, limit, offset, limits, offsets, action, action_doc, action_exists = self.parse_url(body)
        print("query = " + query)
        print("doclimit = " + limit)
        print("docoffset = " + offset)
        print("action = " + action)
        print("actiondoc = " + action_doc)
        if action_exists:
            offsets = self.get_new_offset_limit(action, action_doc, offsets, limits)
        print('limits = ' + str(limits))
        print('offsets = ' + str(offsets))
        search_engine = SearchEngine(database_name)
        start_time = time.time()
        # For testing time of response change comment string

        # this string filter result in the end
        #r = search_engine.search_limit_offset(query, 4, limit, offset, limits, offsets)

        # this string filter in beginning
        r = search_engine.search_to_highlight_limit_offset(query, 3, limit, offset, limits, offsets)
        print('time: ', time.time() - start_time)
        myresp = ''
        myresp += 'Documents Limit<br><input type="text" name="limit" value="' + str(limit) + '"><br>'
        myresp += 'Documents Offset<br><input type="text" name="offset" value="' + str(offset) + '"><br>'
        key_list = list(r.keys())
        key_list.sort()
        j = 0
        for key in key_list:
            myresp += '<ol>\n'
            myresp += '<li>' + key + '</li>\n<ul>'
            myresp += 'Limit<br><input type="text" name="doc' + str(j) + 'limit" value="' + limits[j] + '"><br>'
            myresp += 'Offset<br><input type="text" name=doc' + str(j) + 'offset" value="' + offsets[j] + '"><br>'
            myresp += '<input type="submit" name=action' + str(j) + ' value="perv">'
            myresp += '<input type="submit" name=action' + str(j) + ' value="back">'
            myresp += '<input type="submit" name=action' + str(j) + ' value="next"> <br>'
            for val in r[key]:
                myresp += '<li>'+val+'</li>'
            myresp += '</ul>'
            j = j + 1
            myresp += '</ol>'
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(bytes((resp + data.format(query, myresp)), "utf-8"))
        # except TypeError as te:
        #     response = 'fields "limit" and "offset" can not take a negative or fractional values'
        #     self.wfile.write(bytes((resp + data.format('', response)), "utf-8"))
        #     print(te)
        # except Exception as ex:
        #     response = '<br>Uuups. Something went wrong. Error message: ' + str(ex) + '<br>'
        #     self.send_response(200)
        #     self.send_header("Content-type", "text/html; charset=utf-8")
        #     self.end_headers()
        #     files = os.listdir(".\\")
        #     i = 0
        #     for file in files:
        #         if re.match(".*\.txt", file):
        #             response += (file + "<br>")
        #             response += 'Limit<br><input type="text" name=doc' + str(i) + 'limit value="0"><br>'
        #             response += 'Offset<br><input type="text" name=doc' + str(i) + 'offset value="0"><br>'
        #             response += '<input type="submit" name=action' + str(i) + ' value="perv">'
        #             response += '<input type="submit" name=action' + str(i) + ' value="back">'
        #             response += '<input type="submit" name=action' + str(i) + ' value="next"> <br>'
        #             i = i + 1
        #     self.wfile.write(bytes((resp + data.format('', 'Not Found<br>' + response)), "utf-8"))


ws = HTTPServer(('0.0.0.0', 80), WebServer)

# Server running until Ctrl-C pressed
try:
    ws.serve_forever()
except KeyboardInterrupt:
    pass

ws.server_close()
