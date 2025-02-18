# App to store what one owns

Idea is to make like an inventory, with purchases tied to a purchaser.
For home related expenses - idea is to tie it to the "home / ghar" user.

# Next Steps 
- reduce image size on server before processing
- Create home page to show overall sumary
- Add dependabot and other stuff for security
- Open Banking
 
# Deployment
- Git setup and clone repo. Create Venv , install dependencies. Setup .env file
- Install postgres table, migrate and copy data. Add db secrets to .env file
- Install nginx and create symlink to conf in devops/nginx.conf
- Install gunicorn and symlink 2 systemd files in devops to /etc/systemd/system/. Follow documentation here - https://docs.gunicorn.org/en/latest/deploy.html#systemd
- Set services enabled at boot -
    - sudo systemctl start nginx.service 
    - sudo systemctl enable nginx.service
    - sudo systemctl start gunicorn.socket
    - sudo systemctl enable gunicorn.socket
    - sudo systemctl start gunicorn.service
    - sudo systemctl enable gunicorn.service

# next learning step could be to automate it with terraform
