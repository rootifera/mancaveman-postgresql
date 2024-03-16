# mancaveman

```
./start               # runs docker compose up -d
./stop                # runs docker compose down
./stop --wipe         # wipes data, REMOVED DB and EVERYTHING!
scripts/wipe          # deletes EVERYTHING, containers, networks, images, volumes. Don't use unless you have to
scripts/create_env    # creates .env file with defaults and random passwords. Other scripts call this script.
scripts/backuip       # backs up database, env file and the uploads folder.
scripts/run.sh        # mancaveman container startup script, you won't need to do anything with it
scripts/build         # builds mancaveman image
scripts/build --push  # builds mancaveman image and pushes into the repo\
```
