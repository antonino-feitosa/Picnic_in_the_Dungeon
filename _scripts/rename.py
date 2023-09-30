import os

path = "../_resources/Avatar"


for name in os.listdir(path):
    if name.startswith("White"):
        output = "sprite.avatar." + name.replace(" - ", ".").lower()
        os.rename(path + "/" + name, path + "/" + output)
