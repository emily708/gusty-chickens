# Let's Titanic! by Gusty Chickens

## Roster
PM Emily Mai  
Devo Amy Shrestha  
Devo Carrie Ko  
Devo James Lei  

## Description  
This game is a Titanic simulation game where your main goal is to save as many Titanic passengers as possible as the captain of the Titanic. The game limits your actions on the ship to 100 moves, which includes moving passengers around the ship, inspecting the passengers’ survival rates, etc. forcing you to take risky guesses and prioritize certain actions. Your first inspection for every room is free, so use it wisely! You can load and save your progress, or play a new game as much as you want. Once you are out of moves, you will be given your survival rate and its related metrics.

#### Visit our live site at [167.172.24.134](http://167.172.24.134)

## Install Guide
1) Clone the repo into a local directory:
```
git clone git@github.com:emily708/gusty-chickens.git
```
2) Enter the app directory:
```
cd gusty-chickens
```
3) Open a virtual environment:
```
python3 -m venv venv
```
4) Activate virtual env for Linux, Windows, or Mac:

i. Linux
```
. venv/bin/activate
```
ii. Windows
```
venv\Scripts\activate
```
iii. Mac
```
source venv/bin/activate
```
5) Install necessary modules:
```
pip install -r requirements.txt
```
6) Change into the app directory
```
cd app
```
7) Create databases:
```
python3 build_db.py
```
8) Populate databases:
```
python3 populate.py
```

## Launch codes
1) Run the app through Flask:
```
python3 __init__.py
```
2) Open the link:
```
http://167.172.24.134
```
3) After running the launch codes and utilizing the app, exit the virtual environment:
```
deactivate
```
