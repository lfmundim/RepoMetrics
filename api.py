from flask import Flask
from flask_restful import Resource, Api
from git import Repo
import shutil
import json
import GitPyService as gps
import collections

app = Flask(__name__)
api = Api(app)

class RepoStats(object):
    def __init__(self, owner, url):
        self.owner = owner
        self.url = url
    
    owner = ''
    url = ''
    commit_count = 0
    top_committers = {}
    most_modified_files = {}
    no_config_files = {}
        
def get_range(dictionary, size):
    d = collections.OrderedDict()
    count = 0
    for k, v in (dictionary.items()):
        d[k] = v
        count += 1
        if count == size:
            break
    return d



class PublicRepo(Resource):
    def get(self, git_source, user, repo_url):
        if git_source == 'github':
            host = 'https://github.com/'
        else:
            return 'Git Source not yet supported, create a pull request!', 400
        url = host + user + '/' + repo_url + '.git'
        git_service = gps.GitPyService(path='./repo', url=url)
        
        response_object = RepoStats(owner=user, url=url)
        metrics = git_service.get_metrics()
        
        response_object.commit_count = metrics[0]
        response_object.top_committers = get_range(metrics[1], 10)
        response_object.most_modified_files = get_range(metrics[2], 10)
        response_object.no_config_files = get_range(metrics[3], 10)

        shutil.rmtree('./repo', ignore_errors=True)
        response = app.response_class(
            response=json.dumps(response_object.__dict__),
            status=200,
            mimetype='application/json'
        )
        
        return response


api.add_resource(PublicRepo, '/api/<git_source>/<user>/<repo_url>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')