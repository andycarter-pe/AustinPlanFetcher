import base64
with open("Get_Plans_256.ico", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
print(encoded_string)#print string to copy it (see step 2)