# App to store what one owns

Idea is to make like an inventory, with purchases tied to a purchaser.
For home related expenses - idea is to tie it to the "home / ghar" user.

# Next Steps 
- Create home page to show overall sumary. Should show monthly expense for all, for each month.
- Open Banking integration so that all purchases can also move from bank to our system.
- backup of db and uploads
 
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
- Setup visudo to add sudo commands in server restart script to run with sudo without pass.

# next learning step could be to automate it with ansible
