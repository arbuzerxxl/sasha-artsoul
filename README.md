# π³ππππππππππ

### This is bot-helper for nail business as a small CRM.
- Backend: Django
- Database: PostgreSQL
- Frontend: aiogram
- API: DRF
- Docker: βοΈ
- .env: βοΈ

### Bot can CRUD all models within API. Bot-auth is done using JWT.
#### *In this version the bot supports only russian language in chat.*

# π΅πππππππ

### This tool solves the next problems:
- self-registration of new clients and appointment
- financial accounting (total, tax, etc) due to automatic calculation in the database
- accounting for Customers and Employees (Masters)
- introduction of flexible schedule
- smart notification of the Customer
- introduction of all file-log events

# πΌπππππ ππππππ

![Artsoul scheme](https://github.com/arbuzerxxl/images/raw/main/artsoul.png)

# π΅πππππππ

# πΈπππππππππππ
1. Fill **.env.example** with your own data and remove suffix **.example**.

2. Into dir: **deploy/**

        docker-compose up -d --build
3. Docker creates first superuser. If you want to change this data, you need to set: **/backend/entrypoint.sh**.

# π³πππ
## Create user
![Artsoul scheme](https://github.com/arbuzerxxl/images/raw/main/create_user_gif.gif)

## Create master
![Artsoul scheme](https://github.com/arbuzerxxl/images/raw/main/create_master_gif.gif)

## Create visit in schedule
![Artsoul scheme](https://github.com/arbuzerxxl/images/raw/main/create_schedule_gif.gif)

## Create main visit
![Artsoul scheme](https://github.com/arbuzerxxl/images/raw/main/create_visit_gif.gif)