#!/usr/bin/env python3
import requests
import json
import pickle


# Base data
USER="username"
PASS="userpass"
USER_CLONE_SRC="user-repo"
REPO_CLONE_SRC="repo-to-clone"
USER_CLONE_DEST=USER
REPO_CLONE_DEST="test"
GITHUB_API_VERSION={"Accept": "application/vnd.github.v3+json"}

# Getting labels, store them as tuple of tuples in result.txt
response = requests.get(f"https://api.github.com/repos/{USER_CLONE_SRC}/{REPO_CLONE_SRC}/labels",
                        headers=GITHUB_API_VERSION)
labels = ({"name": label["name"], "color": label["color"]} for label in response.json())
# prefering this for the sake of explicity instead of relying on pickle
with open("result.txt", "w") as f:
    for label in labels:
        print(json.dumps(label), file=f)


# Delete default labels
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/bug", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/duplicate", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/enhancement", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/invalid", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/question", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/wontfix", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/good%20first%20issue", auth=(USER, PASS))
requests.delete(f"https://api.github.com/repos/{USER}/{REPO_CLONE_DEST}/labels/help%20wanted", auth=(USER, PASS))


# Adding the labels from result.txt
headers = {
    "Content-Type": "application/json",
    **GITHUB_API_VERSION
}
with open("result.txt") as f:
    for label in f:
        response = requests.post(f"https://api.github.com/repos/{USER_CLONE_DEST}/{REPO_CLONE_DEST}/labels",
                                 headers=headers, data=label, auth=(USER, PASS))
        print(response.text)
