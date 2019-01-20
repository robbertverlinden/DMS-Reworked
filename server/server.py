from flask import Flask, render_template, jsonify
JSONIFY_PRETTYPRINT_REGULAR = True

import os
import docker
from docker import DockerClient

if (os.geteuid() != 0): exit("The server shoudl be started with superuser rights")

client = docker.from_env()

errorMsg = "Something is wrong with the docker API, try to run the server with elevated rights or restart the docker daemon"

app = Flask(__name__, static_folder="../static", template_folder="../static")

   

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/testApi")
def testApi():
    try:
        return jsonify(client.version())
    except docker.errors.APIError: 
        return errorMsg

@app.route("/api/listContainers/")
def listContainers():
    try:
        print("API call to /listContainers has been made")
        return jsonify([({"state": container.status, "id": container.id, "name": container.name} ) for container in client.containers.list(all)])
    except docker.errors.APIError as ex:       
        print(ex.__cause__)
        return errorMsg

@app.route("/api/startNewContainer")
def startNewContainer():
    client.containers.run("hypush/csi", "service mysql start && npm start")
    return "New CSI container has been started"

@app.route("/api/startContainer/<conID>")
def startContainer(conID):
    try:
        container = client.containers.get(conID)
        container.start()
        print(container.id + " has been started")
        return container.id + " has been started"
    except docker.errors.APIError: 
        print("container could not be started")
        return "container could not be started"

@app.route("/api/stopContainer/<conID>")
def stopContainer(conID):
    try:
        container = client.containers.get(conID)
        container.stop()
        print(container.id + " has been stoped")
        return container.id + " has been stoped"
    except docker.errors.APIError: 
        print("container could not be stoped")
        return "container could not be stoped"
            
@app.route("/api/pauseContainer/<conID>")
def pauseContainer(conID):
    try:
        container = client.containers.get(conID)
        container.pause()
        print(container.id + " has been paused")
        return container.id + " has been paused"
    except docker.errors.APIError: 
        print("container could not be paused")
        return "container could not be paused"

@app.route("/api/unpauseContainer/<conID>")
def unpauseContainer(conID):
    try:
        container = client.containers.get(conID)
        container.unpause()
        print(container.id + " has been resumed")
        return container.id + " has been resumed"
    except docker.errors.APIError: 
        print("container could not be resumed")
        return "container could not be resumed"


@app.route("/api/container/<conID>")
def containerID(conID):
    try:
        return jsonify(client.containers.get(conID).attrs)
    except (docker.errors.NotFound, docker.errors.APIError):
        return "Container does not exist or has been mistyped"

@app.route("/api/containerTop/<conID>")
def attachAndRunTop(conID):
    try:
        print("processes of " + conID + "have been returned")
        return jsonify(client.containers.get(conID).top())
    except docker.errors.APIError:
        return errorMsg 

if __name__ == '__main__':
    app.run(host= '0.0.0.0')