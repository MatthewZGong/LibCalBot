
# Development
- This is only made for NYU
## Python Environment
- To create a virtual environment type run `python -m venv lib-venv` 
- To activate the environment run 
    - Windows: `lib-venv\Scripts\activate.bat`
    - Unix/MacOs:  `source lib-venv/bin/activate`
- To install all the python packages run `python -m pip install -r req.txt`

## Chrome Driver 
- the script uses Selenium to scrap the web, so you will need to download a Chrome Driver 
- https://chromedriver.chromium.org/downloads

## Environment Variables 
- there are currently 3 environment variables
- easiest way to set the variables is to create a .env file locally in the repo
```
NYU_USERNAME=
NYU_PASSWORD=
DRIVER_PATH=
```



