# sasha-artsoul
It's web-site for nail business

start docker compose

<!-- from /deploy -->
docker-compose --compatibility -f docker-compose.yml up -d --force-recreate --build

with env

<!-- OLD DOCKER -->
docker-compose --env-file .env --compatibility -p artsoul -f ./deploy/docker-compose.local.old.yml up --build --remove-orphans -d

<!-- NEW DOCKER -->
docker-compose --env-file .env --compatibility -p artsoul -f ./deploy/docker-compose.local.yml up --build --remove-orphans -d

<!-- install python libs -->
python3 -m pip install -r requirements.txt

<!-- create migrations -->
python3 manage.py makemigrations

<!-- migrate to DB -->
python3 manage.py migrate

<!-- run nextjs -->
npm run dev

<!-- run django -->
python3 manage.py runserver

<!-- create ADMIN -->
python3 manage.py createsuperuser


<!-- GIT usefull commands -->
git commit -am "..."  # take all files to commit

git branch -av  # show all local and deleted branches 

git branch  # show local branches

git branch new_branch  # create new branch

git checkout any_branch  # turn off to branch

git fetch  # get last update from git without merge

git pull --rebase  # # get last update from git and rebase

git checkout main
git merge develop  # merge all changes from DEVELOP to MAIN

git log --oneline  # show all commits

<!-- delete db -->
sudo rm _tmp -r

<!-- DOCKER -->
docker rm $(docker ps -qa)
docker rmi $(docker images -q)
docker-compose up -d --build  # from dir deploy/
docker network rm <network_id>

<!-- cmd -->
nano ~/.bashrc