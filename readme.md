I run a Raspberry Pi on my home network for three reasons:

* To have a local DNS (dnsmasq) so I don't have to remember or look up numeric IP addresses
* To handle VPN connections (OpenVPN) into my home network when I'm traveling
* To have something where I can play around with Linux

Actually, there's a fourth reason: having grown up before there were anything like home PCs I love having 
an entire computer -- sporting 4GB of memory and 32GB of storage no less -- I can hold in the palm of my hand. 
That costs less than $100 in 2019 dollars. That's Star Trek (original series) stuff, baby, just a few 
centuries early.

That last reason causes me to upgrade the Pi when newer, more powerful models come out...which then forces me 
to scratch my head trying to remember how the services I run on the Pi are configured and recreate the wheel 
as it were. I tried to do this by writing a bash script but quickly determined my bash skills were, umm, 
too rudimentary to even think of doing something like what I wanted.

So I decided it would be a fun introduction to python to write an app which could be used to configure the 
new Pi, suck certain data across from the old Pi, swap their names and DNS entries and make it easier to 
do the upgrade.

The result was maestro.py, whose source files are here. Fair warning, I don't know python all that well yet 
so don't be surprised if you have trouble trying to get it to work as I haven't included 
every file within my project directory.

To read more about this little project check out 
[this writeup](https://jumpforjoysoftware.com/2019/11/a-few-python-insights/). 
