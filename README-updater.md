# cron-python-html
Creates static html pages from various git repositories combined on one page.

Content updates can be trigged by cron.

## Create non privileged user to run script with
Running the script as root is possible but absolutely not recommended. Better create a dedicated user for it.

Let's create a new user now, for example `git2cms`:

`sudo useradd git2cms -Um`

Keep all project files in it's just created home directory:

`/home/git2cms`

For testing, maintaining and running `update.py` by hand, always open an interactive shell as that user:  
`sudo -i -u git2cms`

or run `update.py` directly:

`sudo -u git2cms python3 update.py`  
Add paths if you are in another directory, of course.


## cron
You can use a cron service to automatically check for new contents and recreate all contents.

Edit unprivileged user's crontable:

`sudo crontab -u git2cms -e` 

or open interactive shell as user and then edit it's crontab:  
```
sudo -i -u git2cms
crontab -e
```

Choose a random minute and always use absolute paths to programs and scripts.  
Don't rush git provider with too much git requests. Hourly is a good start.
```
#minute  hour  day_of_month  month  day_of_week  command
12       *     *             *      *            /usr/bin/python3 /home/git2cms/dir/update.py --cron --allpages
```

## dev status

TODO Adrian:

* Linking and indexing content *(in progress)*
* Translate markdown to html
* Replacing template vars to global vars with Jitsi
* Optimize, organize project structure and outsource common classes and functions
* Create PyPI package

TODO Tim:

* Organisations-Repo? (ohne Contents und Templates von hackersweblog.net)
* Alle drei Template-Models mit aktuellen Varnames
* Besser keine Ordner in templates
* Geht Seitenzoom mit anpassendem Fließtext auf Mobile? Da gibt's irgendein html meta für...
* Copyright und fixtexte als Variable (-> config schauen und ggf. erweitern)
* HTML5 Googlekonform:
    * Seitensprache in HTML-Meta
    * Twitter und co. inkl. Image-Link
    * Datum einer Page aus Meta oder Dateidatum wichtig?
    * Robots.txt (könnte updater mit generieren)
    * Gibt doch so Spezial-Tags wie `<author>` oder? Alles mögliche nutzen.
* Basis-Contents wie Impressum, Datenschutzerklärung.
* Länderflaggen und social-icons (lokal speichern)
* Wenn unser Template fertig: Basis 08/15 Template-Version für andere User
