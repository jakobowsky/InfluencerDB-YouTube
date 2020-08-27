# InfluencerDB-YouTube
I Coded Instagram Influencers DataBase and Automated it with Python. 
YouTube tutorial — https://youtu.be/IKB0S5mF00s

## Contents

1. [Initial Setup Instructions](#initial-setup-instructions)
1. [Running Server](#running-server)
1. [Running Scripts](#running-scripts)

## Initial Setup Instructions

### Setup Python Virtual Environment
```buildoutcfg
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
```
## Running Server

```buildoutcfg
cd webapp
./mange.py migrate
./mange.py runserver
```
### Go and check for endpoints `http://127.0.0.1:8000/api/`

## Running Scripts
### Your Django server should be running in background.
```buildoutcfg
cd scripts
```
#### First Edit your `add_hashtags_to_categories.py` file.
You can change `new_category` for whatever you want eg. Tech. <br>
Same with`basic_hashtags`.
```python

if __name__ == '__main__':
    new_category = "Beauty"
    basic_hashtags = ['fashion', 'beauty']
    script = HashtagScript(new_category, basic_hashtags)
    script()

```
##### Then run commands in this order.
`python3 add_hashtags_to_categories.py`
`python3 discover_script.py`
`python3 update_script.py`

### Info about scripts.
`discover_script.py` <-- Finds new influencers. You can run it every few hours. <br>
`update_script.py` <-- Updates current influencers in database. You can run it every 2 hours. <br>
