# WCX Backend

## Database Migration

### Migration history
```sh
alembic history
```

### Create migration automatically
```sh
alembic revision --autogenerate -m "first commit"
```

### Upgrade migration
```sh
alembic upgrade head
```

### Downgrade migration

#### Downgrade 1 revision
```sh
alembic downgrade -1
alembic downgrade head-1
```

#### Downgrade to a specific version
```sh
alembic downgrade e97e59dc6f31
```

#### Downgrade all
```sh
alembic downgrade base
```
