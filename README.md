# Mancaveman API

### What is this?

This is an API written in Python and FastAPI for managing Mancave contents. These can include games, software, collectibles, car equipment, tools, electronics, musical equipment... and much more.

### Why?

I looked for a solution to help manage my own Mancave and couldn’t find a good one, so I decided to make one for myself. Then I thought maybe other people would use it, and here we are. You now have full access to it.

### So, where is the WebUI?

There isn’t one, unfortunately. The reason is very simple: I can’t do it. I don’t have the skills to make one. I tried, but I just couldn’t understand how all the web stuff works, and I found it very stressful. If you feel like making one, I’d be happy to work with you.

### Are you a software dev?

No, I’m not a software dev. I’m just a Linux Sysadmin/Cloud Infra Engineer type of guy with some basic programming skills. I did my best, but I’m sure when you look at the project, you’ll see an absolute mess. This isn’t intentional, but it’s the best I can do.

### Mancaveman, what's up with the name?

I just thought it would be funny to mix "Mancave" and "Caveman" together. That’s it. Although my beautiful fiancée says the name should be Nerdcave or something, since not all nerds are male.

### How to run the application?

It’s fairly simple. You can download the latest version from the releases, unzip it to a host with Docker (Compose) installed, and then run the ./start command in the mancaveman folder. It will auto-generate an .env file with random keys and credentials. The start script will download the latest Mancaveman, PostgreSQL, and Redis containers and then start them in the Mancaveman network.

The .env file looks like that:
```
### Database Config ###
POSTGRES_DB=cavedb
POSTGRES_USER=wgvxTIOs
POSTGRES_PASSWORD=q6U3gfn0dImc
SQLALCHEMY_DATABASE_URL=postgresql://wgvxTIOs:q6U3gfn0dImc@postgres/cavedb
REDIS_URL=redis://redis
### Keys and Authentication ###
SECRET_KEY=bbgv9hsdyIwCnZb3gXRcTWSmMkP5YLdz76GXs314MSqk6CInzasonMBoMIm0oISx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_HOURS=72
### Server Config (See README.md) ###
PORT=3131
MODE=multi
CORE_LIMIT=True
```

In the .env file, there are a couple of things you can change. The first one is obviously the PORT option. The port number is for accessing the API. In the default configuration, you can access the API at:

```http://[YOUR_HOST_IP]:3131```

This will give you an output similar to:

```
{
"appName": "Mancaveman API",
"version": "1.0.0",
"database": "PostgreSQL",
"buildDate": "2024-12-01",
"buildName": "Toto Santos",
"buildID": "045529ab9c2bdf7f901ec13b",
"buildNumber": "74"
}
```

The other two variables are MODE and CORE_LIMIT. Here you can decide if you want to run the API as a single or multi-core application. The CORE_LIMIT limits the multi-core option to a maximum of 4 cores, and if you set it to False, then all your cores will be used. These settings are very unlikely to need changing, but I was experimenting with them and thought it might be useful to share the code. It could help others trying to do something similar. I tested the application on my 56-core home server, and it works fine. I also benchmarked the multi-core setup, and it definitely increases performance, but I doubt this application would ever have more than a couple of users at any given time.


### What do I do after starting the application? 

Please access it at:

```http://[YOUR_HOST_IP]:3131/docs```

This will open the Swagger UI, where you can interact with the API. Probably the first thing you’ll notice is that almost everything requires authentication. Please use the admin/first_run endpoint to create the admin user. You will only need to do this once.

![Create admin user](https://i.gyazo.com/ee19cb20df47dd431d7d6df884cb5b51.png)

```
default credentials:

username: admin
password: admin

```

After that, you can log in with the admin user, change the password, create new users, and use the API.


### I want to build my own container with the code. How do I do that?

It’s fairly simple. I will assume you are using Linux to build the image.

First, download the code. Edit your /etc/hosts file and add postgres after your 127.0.0.1 entry. During the build process, some Alembic stuff happens, and it needs PostgreSQL.

```
127.0.0.1       localhost       postgres
```

Once you’ve done that, you can run:

```
scripts/build
```

This will start the build. If you want to push this container into your Docker Hub, you need to log in to your Docker Hub account in the terminal and run the build command as:

```
scripts/build --push
```

This will first build the container and then push it to your Docker Hub.

### I would like to contribute, add/remove stuff. How do I do that?

Just contact me, and we can figure something out. I might need to check some documents, I guess.

### I have other questions! Where do I ask?

The best option is probably to create an issue on GitHub. I’m around often, and you’ll get a reply quickly.