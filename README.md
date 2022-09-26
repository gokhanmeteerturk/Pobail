
# Community Management Platform For Local Businesses
![PYTHON](https://img.shields.io/badge/python%20^3.8-purple?style=flat&logo=python&color=red&logoColor=white)
![DJANGO](https://img.shields.io/badge/Django-^4.0.4-blue?style=flat&logo=django)
![Version](https://img.shields.io/badge/Version-v0.1.03-yellow?style=flat) 
![repo](https://img.shields.io/badge/Status-Active-success?style=flat)

A community building and management system for businesses, NGOs etc. It supports multiple branches, leaders and special coupons / report assignments for community members.

## Setup (Local)
(based on the setup you have, you might need to use python3 and/or pip3 commands instead of python and pip commands below.)



#### First, clone the project using git and create a virtual environment for the project:
```bash
git clone https://github.com/gokhanmeteerturk/Pobail.git
cd Pobail
python -m venv env
```
 
#### Then you should activate the environment:

    For Windows:
```bash
.\env\Scripts\activate
```

    For Linux:
```bash
source env/bin/active
```
 
#### Finally, install dependencies and follow regular django setup steps like this:
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### When done, you can run the development server on `127.0.0.1:8000` with:
```bash
python manage.py runserver
```
Note: From admin panel, you will need to add a leader and a member named 'Guest Leader' and 'Guest Member' for the guest system to work.

## Main Features

Login as admin, and you can create branches, create spaces, add new leaders, new members and assigns them spaces.

Spaces are different groups in the same branch for which you can select a responsible 'leader'. A space can be 'Coffee Workshop Space', 'Premium Members Space', 'Cat Lovers Space' or anything you want. 
Members of the same space can talk to each other. You can assign different coupons to different spaces, and make announcements to a specific space's members.
You can assign different coupons to different spaces, and make sure only the members of that space receives that coupon. 
You can add one member to multiple spaces in the same branch.

Leader of a space is responsible for assigning coupons, making announcements, asking for reports and reviewing them, creating and sharing quizzes with the members of the space, and can take attendances for events(workshops etc).

You can create a special access key for a space.
Members with this access key will be able to join called space.

![schema](/media/pobaildb.png?raw=true)

### License
Read LICENSE file for the details of the MIT LICENSE I am using.



