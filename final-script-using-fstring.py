#!/usr/bin/env python3
import requests
import json
from argparse import ArgumentParser
from distutils.util import strtobool
from os.path import isfile
from sys import exit

GITHUB_API_URL = "https://api.github.com/"
GITHUB_REPOS_URL = f"{GITHUB_API_URL}repos"
GITHUB_API_VERSION={"Accept": "application/vnd.github.v3+json"}


def import_labels(repo_url, file_name, user, passwd):
    headers = {
        "Content-Type": "application/json",
        **GITHUB_API_VERSION
    }
    errors = []
    labels = []
    with open(file_name) as f:
        try:
            labels = json.load(f)
        except json.JSONDecodeError:
            print("File is not a valid JSON")
            exit(1)
    for label in labels:
            # label_dict = json.loads(label)
            # labels.append(label_dict['name'])
            response = requests.post(f"{GITHUB_REPOS_URL}/{repo_url}/labels",
                                     headers=headers, data=label, auth=(user, passwd))
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                errors.append(label['name'])
    
    if errors:
        num_errors = len(errors)
        num_labels = len(labels)
        if num_errors == num_labels:
            print("All labels creation failed")
            exit(1)
        print(f"{num_errors} out of {num_labels} failed. Labels which failed: ", errors)
    else:
        print("All labels imported successfully")


def clean(repo_url, user, passwd):
    existing_labels = export(repo_url)
    errors = []
    for label in existing_labels:
        response = requests.delete(f"{GITHUB_REPOS_URL}/{repo_url}/labels/{label['name']}", auth=(user, passwd))
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            errors.append(label['name'])
    
    if errors:
        num_errors = len(errors)
        num_labels = len(existing_labels)
        if num_errors == num_labels:
            print("Labels clean failed")
            exit(1)
        print(f"{len(errors)} out of {len(labels)} failed. Labels which failed: ", errors)
    else:
        print("All labels were deleted successfully") 


def export(repo_url, file_name='', display=False):
    response = requests.get(f"{GITHUB_REPOS_URL}/{repo_url}/labels",
                            headers=GITHUB_API_VERSION)
    try:
        response.raise_for_status()
        data = response.json()
    except (ValueError, requests.exceptions.HTTPError):
        print('Invalid request')
        exit(1)
    if not data:
        print('Empty response')
        exit(1)
    
    try:    
        labels = ({"name": label["name"], "color": label["color"]} for label in data)
    except KeyError:
        print('Invalid response')
        exit(1)
        
    if not file_name:
        if display:
            print(list(labels))
            return None
        else:
            return labels

    if isfile(file_name):
        if not strtobool(input('File already exists, do you want to overwrite it? [y|n]: ')):
            print('Aborting...')
            exit(1)

    with open(file_name, "w") as f:
        json.dump(list(labels), f, indent=2, sort_keys=True)
    

if __name__ == "__main__":

    # Define arguments
    parser = ArgumentParser(description='Export and import issue labels from Github repositories')
    subparsers = parser.add_subparsers(help='Available actions to apply on the repository', dest='action')
    # This is needed because of a known issue in certain version of Python which won't allow require in add_suparsers
    subparsers.required = True

    # Subparser for export
    parser_export = subparsers.add_parser('export', description='export issue labels')
    parser_export.add_argument('repository', help='the Github repo to perform the action on')
    parser_export.add_argument('-o', metavar='FILE', help='JSON file for output labels export', dest='file')

    # Subparser for clean
    parser_clean = subparsers.add_parser('clean', description='clean existing issue labels')
    parser_clean.add_argument('repository', help='the Github repo to perform the action on')
    parser_clean.add_argument('-u', metavar='USER', required=True, help='Github account user', dest='user')
    parser_clean.add_argument('-p', metavar='PASSWORD', required=True, help='Github account passowrd', dest='passwd')

    # Subparser for import
    parser_import = subparsers.add_parser('import', description='import issue labels from JSON file')
    parser_import.add_argument('repository', help='the Github repo to perform the action on')
    parser_import.add_argument('-u', metavar='USER', required=True, help='Github account user', dest='user')
    parser_import.add_argument('-p', metavar='PASSWORD', required=True, help='Github account passowrd', dest='passwd')
    parser_import.add_argument('-i', metavar='FILE', required=True, help='JSON file for importing labels', dest='file')

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(0)

    if args.action == 'export':
        export(args.repository, args.file, display=True)
    elif args.action == 'import':
        import_labels(args.repository, args.file, args.user, args.passwd)
    elif args.action == 'clean':
        clean(args.repository, args.user, args.passwd)
    
    print("\nTask completed")
