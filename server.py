import http.server
import socketserver
import json
import http.client
import requests

PORT = 8000
headers = {"Content-Type": "application/json"}
SERVER = "https://rest.ensembl.org"
ENDPOINT = ["/info/species", '/info/assembly']
EPORT = 80

TEST_REPORT = False

socketserver.TCPServer.allow_reuse_address = True

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received")

        print("Request line:" + self.requestline)
        print("  Cmd: " + self.command)
        print("  Path: " + self.path)

        writing_report_test("--------------NEW REQUEST----------------")
        writing_report_test("Request line:" + self.requestline)
        writing_report_test("  Cmd: " + self.command)
        writing_report_test("  Path: " + self.path)


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
                writing_report_test("  Endpoint: " + end)
                print ("End =>", end)
                if end == '/listSpecies':
                        contents = self.handle_info_species()
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')


                elif end == '/karyotype':
                    contents = self.handle_info_assembly()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')


                elif end == '/chromosomeLength':
                    contents = self.handle_length()
                    print("CONTENTS FUERA:", contents)
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


    def handle_info_species(self):
        request = SERVER + ENDPOINT[0]
        r = requests.get(request, headers=headers)
        print("Sending request:", request)
        writing_report_test("request: " + request)
        d = r.json()

        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Species List</title></head>' \
                   '<body style="background-color: cornflowerblue;"><h1>List of species</h1><ol>'

        l = self.path.split('=')[1]
        if l == '':
            for index in range(len(d['species'])):
                contents += "<li>"
                contents += d['species'][index]['common_name']
                contents += "</li>"

            contents += "</ol></body></html>"
        else:
            for index in range(len(d['species'][:int(l)])):
                contents += "<li>"
                contents += d['species'][index]['common_name']
                contents += "</li>"
        contents += "</ol></body></html>"

        return contents


    def handle_info_assembly(self):
        specie = self.path.split("=")[1]
        specie = specie.replace("+", "_")
        request = SERVER + ENDPOINT[1] + "/" + specie
        print ("Sending request:", request)
        writing_report_test("request: " + request)

        r = requests.get(request, headers=headers)
        d = r.json()
        print("CONTENT: ")
        print(d)


        contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Karyotype of ' + specie + '</title></head>' \
                   '<body style="background-color: turquoise;"><h1>Karyotype of ' + specie + '</h1><ol>'

        for index, elem in enumerate(d['karyotype']):
            contents += "<li>"
            contents += elem
            contents += "</li>"

        contents += "</ol></body></html>"

        return contents



    def handle_length(self):
        print("\nConnecting to server: {}:{}\n".format(SERVER, EPORT))
        specie = self.path.split("=")[1].split("&")[0]
        specie = specie.replace("+","_")
        if specie[-1] == '_':
            specie = specie[:-1]
        chromo = self.path.split("&")[1].split("=")[1]
        print("chromo='",chromo, "', specie = '", specie, "'", sep="")

        # Send the request message
        request = SERVER + ENDPOINT[1] + "/" + specie
        print(request)
        writing_report_test("request: " + request)
        r = requests.get(request, headers=headers)

        d = r.json()


        length_chromosome = None
        for element in d["top_level_region"]:
            print(element)
            if element['coord_system'] == 'chromosome' and element["name"] == chromo:
                    length_chromosome = element["length"]
        print ("Chromosome lenght =", length_chromosome)

        if length_chromosome == None:
            print("No encontrado!")
            contents = '<!DOCTYPE html><html lang="en" dir="ltr"><head>' \
                       '<meta charset="UTF-8">' \
                       '<title>ERROR</title>' \
                       '</head>' \
                       '<body style="background-color: tomato">' \
                       '<h1>ERROR el nombre "' + chromo + '" no es válido.</h1>' \
                        '<p>Here there are the websites available: </p>' \
                        '<a href="/">[main server]</a></body></html>'
        else:
            contents = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Lenght of chromosomo ' + chromo + ' for specie ' + specie + '</title></head>' \
                   '<body><h1>The length of the chromosome ' + chromo + ' of the specie ' + specie + 'is ' + str(length_chromosome) + '.</h1>'
            contents += '</body></html>'


        return contents

def writing_report_test(info):
    if TEST_REPORT:
        f = open("test_report.txt", "a")
        f.write(info + "\n")
        f.close()


Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stop by the user")
        httpd.server_close()