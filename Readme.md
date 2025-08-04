# App to store what one owns

Idea is to make like an inventory, with purchases tied to a purchaser.
For home related expenses - idea is to tie it to the "home / ghar" user.

# Next Steps 
- Create home page to show overall sumary. Should show monthly expense for all, for each month.
- Open Banking integration so that all purchases can also move from bank to our system.
- backup of db and uploads
 
# Deployment

## Automated Setup Using Ansible ( on Ubuntu machine )
```bash
sudo apt install ansible

git clone <your-repo-url>

# Run the playbook
ansible-playbook devops/ansible-playbook.yml --ask-become-pass

# You'll need to provide database password as extra vars:
ansible-playbook devops/ansible-playbook.yml --ask-become-pass -e "db_password=your_secure_password"
```

## Post-Setup Steps
1. Edit `.env` file with your actual values
2. Create Django superuser: `python manage.py createsuperuser`
3. Test the application at your configured domain

