# COS435-project
Final project for COS 435

## Virtual Environment

Virtual Environments create a seperate environment for your code to run in. To get started, install Python 3. 
The `requirements.txt` file contains all dependencies of our project. To setup the virtual environment for the first time
run the following commands inside the project directory: 

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
This will install all the needed packages. Each time you work on the project, just make sure you run `source venv/bin/activate`
to activate the virtual environment in your terminal session. 

## Development Server

Activate the virtual environment. Run

    python server.py
    
Go to `127.0.0.1:5000/random-tweet` in your browser.