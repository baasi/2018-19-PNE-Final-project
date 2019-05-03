import http.server
import socketserver
import http.client
import requests

PORT = 8000
headers = {"Content-Type": "application/json"}
SERVER = "https://rest.ensembl.org"
ENDPOINT = ["/info/species", '/info/assembly']
EPORT = 80


socketserver.TCPServer.allow_reuse_address = True


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received")

        print("Request line:" + self.requestline)
        print("  Cmd: " + self.command)
        print("  Path: " + self.path)

        contents = ""
        try:
            if self.path == '/':
                with open('index.html', 'r') as f:
                    for i in f:
                        contents += i
                        contents = str(contents)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

            else:
                end = self.path.split("?")[0]
                if end == '/listSpecies':
                        contents = self.info_species()
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')

                elif end == '/karyotype':
                    contents = self.info_assembly()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                elif end == '/chromosomeLength':
                    contents = self.length_specie()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                else:
                    with open('error.html', 'r') as f:
                        for i in f:
                            contents += i
                            contents = str(contents)
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/html')
        except Exception:
            self.send_response(404)
            with open('error.html', 'r') as f:
                for i in f:
                    contents += i
                    contents = str(contents)
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')

        self.send_header("Content-Length", len(str.encode(str(contents))))

        self.end_headers()

        self.wfile.write(str.encode(contents))

        return

    def info_species(self):
        req = SERVER + ENDPOINT[0]
        r = requests.get(req, headers=headers)
        d = r.json()

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Species List</title></head>' \
                   '<body style="background-color: cornflowerblue;"><h1>List of species</h1><ol>'

        try:
            limit = self.path.split('=')[1].split('&')[0]
        except IndexError:
            limit = 199

        if limit == '':
            for index in range(len(d['species'])):
                contents += "<li>"
                contents += d['species'][index]['common_name']
                contents += "</li>"

            contents += "</ol></body></html>"
        else:
            for index in range(len(d['species'][:int(limit)])):
                contents += "<li>"
                contents += d['species'][index]['common_name']
                contents += "</li>"

        contents += "</ol></body></html>"

        return contents

    def info_assembly(self):
        specie = self.path.split("=")[1]
        specie = specie.replace("+", "_")
        req = SERVER + ENDPOINT[1] + "/" + specie

        r = requests.get(req, headers=headers)
        d = r.json()

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Karyotype of ' + specie + '</title></head>' \
                   '<body style="background-color: turquoise;"><h1>Karyotype of ' + specie + '</h1><ol>'

        for i, elem in enumerate(d['karyotype']):
            contents += "<li>"
            contents += elem
            contents += "</li>"

        contents += "</ol></body></html>"

        return contents

    def length_specie(self):
        specie = self.path.split("=")[1].split("&")[0]
        specie = specie.replace("+","_")
        if specie[-1] == '_':
            specie = specie[:-1]
        chromo = self.path.split("&")[1].split("=")[1]

        req = SERVER + ENDPOINT[1] + "/" + specie
        r = requests.get(req, headers=headers)

        d = r.json()

        length = None
        for element in d["top_level_region"]:
            if element['coord_system'] == 'chromosome' and element["name"] == chromo:
                    length = element["length"]

        if length == None:
            contents = '<!DOCTYPE html><html lang="en" dir="ltr"><head>' \
                       '<meta charset="UTF-8">' \
                       '<title>ERROR</title>' \
                       '</head>' \
                       '<body style="background-color: tomato">' \
                       '<h1>ERROR that chromosome "' + chromo + '" does not exist.</h1>' \
                        '<p>Here there are the websites available: </p>' \
                        '<a href="/">[main server]</a></body></html>'
        else:
            contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Lenght of chromosomo ' + chromo + ' for specie ' + specie + '</title></head>' \
                   '<body><h1>The length of the chromosome ' + chromo + ' of the specie ' + specie + ' is ' + str(length) + '.</h1>'
            contents += '</body></html>'

        return contents


Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by the user.")
        httpd.server_close()
