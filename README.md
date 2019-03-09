# Project: Linux Server Configuration

### Goal : Set up a Linux server with good security settings, a running web server, & deployment of former Item Catalog project. Use a baseline installation of a Linux distribution on a virtual machine & prepare it to host a web application, to include installing updates, securing it from a number of attack vectors as well as installing/configuring web & database servers.

### Steps to properly submit this project:
1. Create a new GitHub repository & add a file named README.md.

2. Your README.md file should include all of the following:
  i. The IP address & SSH port so your server can be accessed by the reviewer. `ssh ubuntu@34.222.2.40 -p 2200`
  ii. The complete URL to your hosted web application. [http://34.222.2.40.xip.io/](http://34.222.2.40.xip.io/)
  iii. A summary of software you installed & configuration changes made. See `requirements.txt` in addition to `apache2, libapache2-mod-wsgi & postgresql`
  iv. A list of any third-party resources you made use of to complete this project. Listed below:
    - [Digital Ocean - SSH Key-Based Auth](https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server)
    - [Flask documentation](http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/)
    - [*NEW* OAuth2.0 for Web Server App](https://developers.google.com/api-client-library/python/auth/web-app)
    - [Digital Ocean - Setup UFW Firewall](https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server)

3. Locate the SSH key you created for the grader user. *Complete*

4. During the submission process, paste the contents of the grader user's SSH key into the "Notes to Reviewer" field. *Complete*


### Other items from rubric:
#### User Management:
1. Can you log into the server as the user `grader` using the submitted key? *Complete*
2.Is remote login of the `root` user disabled? *Complete, configured in `/etc/ssh/sshd_config`*
3. Is the `grader` user given `sudo` access? *Complete, configured in `/etc/sudoers.d/grader`*

#### Security:
1. Is the firewall configured to only allow for `SSH`, `HTTP`, & `NTP`? *Complete, configured with `sudo ufw allow 2200/tcp`, `sudo ufw allow 80`, `sudo ufw allow 123/udp`. Also, had to change lightsail instance in networking console to allow custom , TCP, on port `2200`.
2. Are users required to authenticate using `RSA` keys? *Complete, configred in `/etc/ssh/sshd_config`.
3. Are the applications up-to-date? *Complete, using `sudo apt-get update`, then `sudo apt-get upgrade`.
4. Is `SSH` hosted on a non-default port? *Complete, `ssh` configured for port `2200`, default is `22`. Also, had to configure in `/etc/ssh/sshd_config`.

#### Application Functionality:
1. Is there a web server running on port `80`? *Complete, default `HTTP` port `80` also specified in `.wsgi` file.
2. Has the database server been configured to properly server data? *Complete, PostgreSQL*
3. Has the web server been configured to serve the Item Catalog application? *Complete, configured at `/var/www/myapp.wsgi`

#### Documentation:
1. Is the README file included in the GitHub repo containing all specified information? *Complete, [https://github.com/tjmac/item-catalog](https://github.com/tjmac/item-catalog).


