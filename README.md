
#### Migration Handling Commands
```alembic revision --autogenerate -m "Initial migration"```
```alembic upgrade head```
```alembic dowpngrade <revision>```

#### Migrating in production
```docker-compose run --rm migration_service```

#### Updating requirements.txt
```pip freeze```


#### Notes
* Timekeeping is done on Maldives GMT for this app. 