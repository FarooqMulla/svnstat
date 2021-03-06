#!/usr/bin/python

# sudo pip install numpy matplotlib

import os
import re
from pylab import *
import dateutil

prog = re.compile(r"r(\d+) \| (.+) \| (\d+-\d+-\d+)")

# author, date, commits, additions, deletions
c = {}


def get_contribution(last, revision):
    additions = 0
    deletions = 0

    cmd = "svn diff -r" + last + ":" + revision

    p = os.popen(cmd, "r")
    for line in p:
        if line[0] == "-":
            if line[0:2] != "---":
                deletions += 1
        elif line[0] == "+":
            if line[0:2] != "+++":
                additions += 1

    p.close()

    return additions, deletions


def draw_commits(author, dates, commits):
    X = [dateutil.parser.parse(s) for s in dates]
    fig = figure(figsize=(30, 6), dpi=96)
    ax = fig.add_subplot(1, 1, 1)
    lc = "total commits = " + str(sum(commits))
    ylim(0, max(commits) * 1.2)

    #ax.fill_between(X, 0, commits, color='blue', alpha=0.5)
    #ax.plot(X, commits, 'o-', color='blue', label=lc)

    ax.bar(X, commits, color='blue', label=lc, alpha=0.5)

    legend(loc="upper right")
    fig.savefig(author + '_commits.png')


def limit(A, D):
    m = 0
    for a, d in zip(A, D):
        m = max(m, a + d)
    return m


def draw_lines(author, dates, additions, deletions):
    X = [dateutil.parser.parse(s) for s in dates]
    fig = figure(figsize=(30, 6), dpi=96)
    ax = fig.add_subplot(1, 1, 1)
    la = "total additions = " + str(sum(additions))
    ld = "total deletions = " + str(sum(deletions))

    #ylim(0, max(max(additions), max(deletions)) * 1.1)
    #ax.fill_between(X, 0, additions, color='green', alpha=0.25)
    #ax.fill_between(X, 0, deletions, color='red', alpha=0.25)
    #ax.plot(X, additions, 'o-', color='green', label=la)
    #ax.plot(X, deletions, 'o-', color='red', label=ld)

    ylim(0, limit(additions, deletions) * 1.1)
    ax.bar(X, additions, color='green', label=la, bottom=deletions, alpha=0.6)
    ax.bar(X, deletions, color='red', label=ld, alpha=0.6)

    legend(loc="upper right")
    fig.savefig(author + '_lines.png')


first = True
author = ""
last = ""
revision = ""

p = os.popen("svn log", "r")
for line in p:
    result = prog.match(line)
    if result:
        if first:
            revision, author, date = result.groups(1)
            first = False
        else:
            last = result.groups(1)[0]
            additions, deletions = get_contribution(last, revision)

            if author in c:
                if date not in c[author]:
                    c[author][date] = {'commits': 1, 'additions': additions,
                                       'deletions': deletions}
                else:
                    c[author][date]['commits'] += 1
                    c[author][date]['additions'] += additions
                    c[author][date]['deletions'] += deletions
            else:
                c[author] = {}
                c[author][date] = {'commits': 1, 'additions': additions,
                                   'deletions': deletions}

            revision, author, date = result.groups(1)

p.close()

for author in c:
    dates = []
    commits = []
    additions = []
    deletions = []
    for date in sorted(c[author].iterkeys()):
        dates.append(date)
        commits.append(c[author][date]['commits'])
        additions.append(c[author][date]['additions'])
        deletions.append(c[author][date]['deletions'])
        print author, date, c[author][date]['commits'],
        print c[author][date]['additions'], c[author][date]['deletions']
    draw_commits(author, dates, commits)
    draw_lines(author, dates, additions, deletions)
