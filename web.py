from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import webbrowser

from lobby import start_lobby

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Read and render the contents of index.html
        with open('index.html', 'r') as file:
            content = file.read()
            self.wfile.write(content.encode())
    def do_POST(self):

        global wallet_address
        
        if self.path == '/send_value':
            content_length = int(self.headers['Content-Length'])
            form_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(form_data)

            for key in parsed_data.keys():
                last_key = key
            my_input = (parsed_data[last_key][0]).split('\n')

            for item in my_input:
                #if str('0x') in str(item):
                if str(item).startswith(str('0x')):
                    wallet_address = str(item)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


        if self.path == '/rungame':
        
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            start_lobby(wallet_address)

        else:
            pass

def run(server_class = HTTPServer, handler_class = MyRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    # Open the web page in the default web browser
    webbrowser.open('http://localhost:8000')

    run()
