import argparse
from git import Repo
import shutil
import json
import GitPyService as gps
import collections

class RepoStats(object):
    def __init__(self, url):
     #   self.owner = owner
        self.url = url
    
    #owner = ''
    url = ''
    commit_count = 0
    top_committers = {}
    most_modified_files = {}
    no_config_files = {}
    commits_by_time = {}
    cra_average_evolution = []
    cta_average_evolution = []
    mca_average_evolution = []
    mostImportantFiles = []
    highest_couplings = []

def get_range(dictionary, size):
    d = collections.OrderedDict()
    count = 0
    for k, v in (dictionary.items()):
        d[k] = v
        count += 1
        if count == size:
            break
    return d

parser = argparse.ArgumentParser(description="Arguments Description")
parser.add_argument('--repo', nargs='?', default='no-repo', help='Repo to use')
parser.add_argument('--folder', nargs='?', default='no-folder', help='Folder to use')

args = parser.parse_args()

# no folder or git repo passed
if (args.repo == 'no-repo' and args.folder == 'no-folder') or (args.repo != 'no-repo' and args.folder != 'no-folder'):
    print ('You must select either a repo OR a folder')

else:
    if args.repo != 'no-repo':
        git_service = gps.GitPyService(path='./repo', url=args.repo)
        repo_name = args.repo.split('/')[-1]
    else:
        git_service = gps.GitPyService(url='[empty]', path=args.folder)
        repo_name = args.folder.split('/')[-1]

    response_object = RepoStats(url=args.repo)

    metrics = git_service.get_metrics()
    
    response_object.commit_count = metrics[0]
    response_object.top_committers = get_range(metrics[1], 10)
    response_object.most_modified_files = get_range(metrics[2], 10)
    response_object.no_config_files = get_range(metrics[3], 10)
    response_object.commits_by_time = metrics[4]
    response_object.cra_average_evolution = metrics[5]
    response_object.cta_average_evolution = metrics[6]
    response_object.mca_average_evolution = metrics[7]
    response_object.mostImportantFiles = metrics[8]
    response_object.highest_couplings = metrics[9]
    if args.repo != 'no-repo':
        shutil.rmtree('./repo', ignore_errors=True)

    #print (json.dumps(response_object.__dict__))
    
    # Prints .json file with all metrics calculated
    output_json = open(repo_name+'.json','w')
    output_json.write(json.dumps(response_object.__dict__))
    output_json.close()