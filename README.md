# Shortly
Shortly is a test rest api url shortener

## Prerequisites
* Python 3.11
* Poetry ^1.4.0
* FastAPI 0.95
* Postgresql 15

## Setup
```bash
git clone https://github.com/kyofu95/shortly
cd shortly
cp .env.sample .env
Edit your .env file and set the variables
docker-compose -f docker-compose.yml up
check localhost:8000/docs
```

## API Documentation
View the API endpoint docs by visiting 👉 http://localhost:8000/docs
![api.png](https://github.com/kyofu95/shortly/blob/main/.github/api.png)