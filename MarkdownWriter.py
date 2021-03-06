import io
import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

import os

from os import path
from wordcloud import WordCloud

class MarkdownWriter:
    def __init__(self, repo_metrics, graph):
        self.repo_metrics = repo_metrics
        self.graph = graph

    def Save_Word_Cloud(self, dictionary, filename):
        text = ""
        for key in dictionary:
            for i in range(dictionary[key]):
                text += "{} ".format(key)

        wordcloud = WordCloud().generate(text)

        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        wordcloud = WordCloud(max_font_size=40).generate(text)
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig('output/{}.png'.format(filename), aspect='auto',  bbox_inches = 'tight')
        plt.close()

    def Save_Line_Plot(self, xsource, ysource, filename, xlabel, ylabel):
        plt.plot(xsource, ysource)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.tight_layout()
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.5)
        plt.savefig('output/{}.png'.format(filename), aspect='auto',  bbox_inches = 'tight')
        plt.close()    

    def Save_Line_Plot_1D(self, xsource, filename, xlabel, ylabel):
        plt.plot(xsource)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.tight_layout()
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.5)
        plt.savefig('output/{}.png'.format(filename), aspect='auto',  bbox_inches = 'tight')
        plt.close()

    def Save_Horizontal_Bar_Plot(self, xsource, ysource, filename, xlabel, ylabel):
        plt.rcdefaults()
        fig, ax = plt.subplots()
        y_pos = np.arange(len(xsource))
        ax.barh(y_pos, ysource, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(xsource)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel)
        ax.set_xlabel(ylabel)
        plt.savefig('output/{}.png'.format(filename), aspect='auto',  bbox_inches = 'tight')
        plt.close()
        del fig

    def Save_Bar_Plot(self, xsource, ysource, filename, xlabel, ylabel):
        plt.bar(xsource, ysource)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.tight_layout()
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.5)
        plt.savefig('output/{}.png'.format(filename), aspect='auto',  bbox_inches = 'tight')
        plt.close()    

    def Plot_Coupling_Graph(self):
        fig = plt.figure(figsize=(20, 20))

        elarge = [(u, v) for (u, v, d) in self.graph.edges(data=True) if d['weight'] > 7]
        esmall = [(u, v) for (u, v, d) in self.graph.edges(data=True) if d['weight'] <= 7]

        pos = nx.spring_layout(self.graph, k=2)  # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=70)

        # edges
        nx.draw_networkx_edges(self.graph, pos, edgelist=elarge,
                            width=2)
        nx.draw_networkx_edges(self.graph, pos, edgelist=esmall,
                            width=2, alpha=0.5, edge_color='b', style='dashed')

        # labels
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_family='sans-serif')

        plt.axis('off')
        plt.savefig('output/coupling.png', aspect='auto',  bbox_inches = 'tight')
        plt.close()

    def Write(self):
        markdown = open('output/{}.md'.format(self.repo_metrics.name), 'w')

        self.Save_Line_Plot(list(self.repo_metrics.commits_by_time.keys()), list(self.repo_metrics.commits_by_time.values()), 'commits', 'period', 'commits')
        self.Save_Bar_Plot(list(self.repo_metrics.top_committers.keys()), list(self.repo_metrics.top_committers.values()), 'top_committers', 'commits', 'committer')
        self.Save_Bar_Plot(list(self.repo_metrics.most_modified_files.keys()), list(self.repo_metrics.most_modified_files.values()), 'most_modified_files', 'mods', 'file')
        self.Save_Line_Plot_1D(self.repo_metrics.cra_average_evolution, filename='cra', xlabel='period', ylabel='CRA')
        self.Save_Line_Plot_1D(self.repo_metrics.cta_average_evolution, filename='cta', xlabel='period', ylabel='CTA')
        self.Save_Line_Plot_1D(self.repo_metrics.mca_average_evolution, filename='mca', xlabel='period', ylabel='MCA')
        self.Save_Horizontal_Bar_Plot(list([x[0] for x in self.repo_metrics.mostImportantFiles]), list([x[1] for x in self.repo_metrics.mostImportantFiles]), 'most_important_files', 'file', 'commits')
        self.Save_Word_Cloud(self.repo_metrics.filesAuthorList, 'authorsWordCloud')
        self.Plot_Coupling_Graph()

        markdown.write('# ' + self.repo_metrics.name + '\n')
        markdown.write('## Basics\n')
        markdown.write('### Total commits: ' + str(self.repo_metrics.commit_count) + '\n\n')
        markdown.write('### Commits by time:\n')
        markdown.write('![](commits.png)\n')
        markdown.write('### Top committers:\n')
        markdown.write('![](top_committers.png)\n')
        markdown.write('---\n')
        if(len(self.repo_metrics.truckFactor) > 0):
            markdown.write('### Truck Factors:\n')
            for author in self.repo_metrics.truckFactor:
                markdown.write('#### - {}\n'.format(author))
            markdown.write('---\n')
        markdown.write('### Authors:\n')
        markdown.write('![](authorsWordCloud.png)\n')
        markdown.write('## Advanced Metrics\n')
        markdown.write('### Most modified files:\n')
        markdown.write('![](most_modified_files.png)\n')
        markdown.write('### Highest couplings\n')
        markdown.write('_Coupling means that the files have been modified together frequently_\n')
        markdown.write('![](coupling.png)\n')
        markdown.write('### Average CRA\n')    
        markdown.write('CRA stands for *Relative File Complexity*\n')
        markdown.write('![](cra.png)\n')
        markdown.write('### Average CTA\n')    
        markdown.write('CTA stands for *Total File Complexity*\n')
        markdown.write('![](cta.png)\n')
        markdown.write('### Average MCA\n')    
        markdown.write('MCA stands for *Biggest file complexity*\n')
        markdown.write('![](mca.png)\n')
        markdown.write('### Most \"important\" files\n')    
        markdown.write('![](most_important_files.png)\n')

        markdown.close()