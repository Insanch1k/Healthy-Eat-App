# Healthy-Eat-App
Application for healthy eating, written in Python using framework Django.


## The main technologies that I used in my project:
- Django (2.2)
- Celery 4.4.7
- Redis 5.5.2
- Twilio 
- Chart.js 
- JavaScript
- HTML5
- CSS3

### Main application possibilities:
- Calculation of daily calories based on user's height, weight and activity
- Calculate of index body weight 
- After calculating user can see all results 
- Based on the calculated calories, calculate the diet for lose weight
- Based on the calculated calories, calculate the diet for stable weight
- Based on the calculated calories, calculate the diet for gain weight
- For example user liked lose weight program, he can subscribe it
- Subscribed program will be display in his profile page
- After subscribe on program user will get sms confirm on his phone (Twilio)
- Every day user will get sms with reminder before eating (Twilio, Celery, Redis)
- In any moment user can unsubscribe chosen program 
- In profile page user can see his weight progress on awesome graph (Chart.js)

