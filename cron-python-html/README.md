# cron-python-html
Creates static html pages from various git repositories combined on one page.

Content updates be trigged by cron.


## Non privileged user
Create a non privileged user for executing scripts and writing content.  
`useradd git2cms -Um`


Keep all project files in it's home directory.
For testing, maintaining and running, always open an interactive shell as that user:  
`sudo -i -u git2cms`

## cron
Open interactive shell as user and edit it's crontab:  
`sudo -i -u git2cms`

Edit user's crontab:  
`crontab -e`

Choose a random minute and always use absolute paths to programs and scripts.  
Don't rush git provider with too much git requests. Hourly is a good start.
```
#minute  hour  day_of_month  month  day_of_week  command
12       *     *             *      *            /usr/bin/python3 /home/git2cms/dir/update.py --cron --allpages
```

## dev status

TODO:

* Merging content repos *(in progress)*
* Linking and indexing content
* Translate markdown to html
* Replacing vars in templates with Jitsi
* Optimize, organize project structure and outsource common classes and functions
* Create PyPI package
