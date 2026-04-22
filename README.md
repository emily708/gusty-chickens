# Let's Titanic! by Gusty Chickens

## Roster
PM Emily Mai  
Devo Amy Shrestha  
Devo Carrie Ko  
Devo James Lei  

## Description  
This game is a Titanic simulation game where your main goal is to save as many Titanic passengers as possible as the captain of the Titanic. The game limits your actions on the ship to 100 moves, which includes moving passengers around the ship, inspecting the passengers’ survival rates, etc. forcing you to take risky guesses and prioritize certain actions. Nothing is free (unless you get a hammer). You can load and save your progress, or play a new game as much as you want. Once you are out of moves, you will be given your survival rate and its related metrics.

__Item Descriptions:__
* Hammer (permanent unless used on a passenger): when entering a miscellaneous room, the player does not lose a move
* Growth Potion (disposable): Increases someone's age by 10 years
* Youth Potion (disposable): Decreases someone’s age by 10 years
* $1000000 Check (disposable): Changes someone to 1st Class
* $1000 Check (disposable): Changes someone to 2nd Class
* Debt Papers (disposable): Changes someone to 3rd Class  

#### Visit our live site at [167.172.24.134](http://167.172.24.134)  

### FEATURE SPOTLIGHT
* Use the $1000000 Check on a passenger.
* Gamble with the compass platform for a chance of instant win or instant death!
* Take a look at db.py for all the sqlite functions.

### KNOWN BUGS/ISSUES
* Using the hammer on a passenger makes it disappear.

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

  a. Linux
  ```
  . venv/bin/activate
  ```
  b. Windows
  ```
  venv\Scripts\activate
  ```
  c. Mac
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
