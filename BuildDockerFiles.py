# builds all Dockerfiles with a extension
# the extension will be used as the image name.

import os
from os import path
docker_user = "gizzmo123456"

dockerfiles = [ f for f in os.listdir(".") if f.split(".")[0] == "Dockerfile" and len(f.split(".")) > 1]

docker_image_name = "game_server"
docker_image_tag = ""   # the extension
docker_image_hack_tag = "1.0"

print(dockerfiles)

docker_base_build_comm = "docker build -f {file} -t {user}/{iamge}:{tag}-{hacktag} ."
docker_base_push_comm  = "docker push {user}/{image}"

print("Found docker files ("+str(len(dockerfiles))+")")
print((" "*4).join(dockerfiles))

print("Enter files to ignore, space sep")
ignore_files = input()
ignore_files = ignore_files.split(" ")

# remove ignore files
for i in ignore_files:
    if i in dockerfiles:
        dockerfiles.remove(i)

print("Enter Hack Tag")
docker_image_hack_tag = input()

print("Building files," )
print((" "*4).join(dockerfiles))
print("continue?")
cont = input()

if cont.lower() != "y" and cont.lower() != "yes":
    print("Bey Bey!")
    exit()

print("Building...")

for f in dockerfiles:
    docker_image_tag = f.split(".")[1]
    print(docker_base_build_comm.format(file=f, image=docker_image_name, tag=docker_image_tag, hacktag=docker_image_hack_tag))
    os.system( docker_base_build_comm.format(file=f, image=docker_image_name, tag=docker_image_tag, hacktag=docker_image_hack_tag) )

print("\nBuild Done!")
print("\nPush to docker? (warning: this will push all tags for image", docker_image_name, ")")
cont = input()

if cont.lower() != "y" and cont.lower() != "yes":
    print("Bey Bey!")
    exit()

print(docker_base_push_comm.format(user=docker_user, image=docker_image_name))
os.system( docker_base_push_comm.format(user=docker_user, image=docker_image_name) )
