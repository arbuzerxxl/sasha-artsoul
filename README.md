# 𝙳𝚎𝚜𝚌𝚛𝚒𝚙𝚝𝚒𝚘𝚗

### This is bot-helper for nail business as a small CRM.
- Backend: Django
- Database: PostgreSQL
- Frontend: aiogram
- API: DRF
- Docker: ✅️
- .env: ✅️

### Bot can CRUD all models within API. Bot-auth is done using JWT.
#### *In this version the bot supports only russian language in chat.*

# 𝙵𝚎𝚊𝚝𝚞𝚛𝚎𝚜

### This tool solves the next problems:
- self-registration of new clients and appointment
- financial accounting (total, tax, etc) due to automatic calculation in the database
- accounting for Customers and Employees (Masters)
- introduction of flexible schedule
- smart notification of the Customer
- introduction of all file-log events

# 𝙼𝚘𝚍𝚎𝚕𝚜 𝚜𝚌𝚑𝚎𝚖𝚎

![Artsoul scheme](https://github.com/arbuzerxxl/images/raw/main/artsoul.png)

# 𝙵𝚎𝚊𝚝𝚞𝚛𝚎𝚜

# 𝙸𝚗𝚜𝚝𝚊𝚕𝚕𝚊𝚝𝚒𝚘𝚗
1. Fill **.env.example** with your own data and remove suffix **.example**.

2. Into dir: **deploy/**

        docker-compose up -d --build
3. Docker creates first superuser. If you want to change this data, you need to set: **/backend/entrypoint.sh**.

# 𝙳𝚎𝚖𝚘
