# dependencies  
   
- certifi==2022.12.7  
- charset-normalizer==3.1.0  
- idna==3.4  
- loguru==0.6.0  
- peewee==3.16.0  
- pyTelegramBotAPI==4.10.0  
- python-dateutil==2.8.2  
- python-dotenv==1.0.0  
- python-telegram-bot-calendar==1.0.5  
- requests==2.28.2  
- six==1.16.0  
- urllib3==1.26.15  
  
### bot start/install 

install dependencies - pip install -r requirements.txt  

create .env in main directory.

BOT_TOKEN="**"

API_KEY="**"

start bot - python main.py 

### Docker build/start

start docker - docker-compose up -d
 
### Bot commands 
  
+ /start <br>
Greeting Output
+ /help <br>
Displaying a list of commands for the bot
+ /cancel <br>
Completing any bot command
+ /lowprice <br>
Search hotels with low price
+ /highprice <br>
Search for hotels with a high price
+ /bestdeal <br>
Search for hotels with price and distance to the city center.
+ /history <br>
Displays the results of the user's last query.  
