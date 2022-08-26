import requests
from tika import parser
BASE = "http://127.0.0.1:5000/"


# parsed_pdf = parser.from_file('C:\\Users\\HP\\Documents\\fichier\\tpd.pdf')
# data = parsed_pdf['content']

# res=requests.put(BASE+"document/7",{"description":data,"name":"name6"})
# print(res.json())
# input() 







response = requests.get(BASE + "document/search/intrapéritonéale")
print(response.json())

# input()
# response = requests.get(BASE + "document/3")
# print(response.json())