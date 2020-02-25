# git2cms
Are you looking for a simple CMS?  
Do you just want to easily publish your content right now without messing with configs, themes and PHP first?  
And do you like github btw.? ;-)

Then just use **git2cms** to keep your contents in git repositories and compose them automatically or on demand to static html files combined on a web page.

Multiple authors may publish their contents to a single page.

First reference page as demo: https://hackersweblog.net (in development)

Reference theme: https://github.com/DeatPlayer/hackersweblog.net-page-template (in development)

## Features
* Contents in your git repository
* Markdown
* Tags
* Languages
* Multiple authors
* Templates
* Simple static html pages (No PHP, yaaay!)

## Implementations

### cron-python-html
Creates static html files on demand or by cron.

Requirements:
* markdown, PyPI: `markdown`
* yaml, PyPI: `PyYAML`
