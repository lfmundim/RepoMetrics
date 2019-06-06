import io
import json

class MarkdownWriter:
    def __init__(self, repo_metrics):
        self.repo_metrics = repo_metrics

    def Write(self):
        markdown = open(self.repo_metrics.url+'.md', 'w')

        markdown.write('# ' + self.repo_metrics.url + '\n')
        markdown.write('```json\n' + json.dumps(self.repo_metrics.__dict__) + '\n```')

        markdown.close()