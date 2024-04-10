# Install
Download files
```
pip install networkx
pip install PuLP
pip install Flask
pip install waitress
python server.py
```
This will start a server on localhost:5001

Use postman to make an optimization request in the following form
POST to localhost:5001/optimize
content-type: application/json
with following JSON body:
```yaml
{
    "pool":"test",
    "maxSteps":2,
    "matchData":[
        {
        "id":"1",
        "from":"A",
        "to":"B",
        "weight": 1
        },
        {
        "id":"2",
        "from":"B",
        "to":"C",
        "weight": 1
        },
        {
        "id":"3",
        "from":"C",
        "to":"A",
        "weight": 1
        }
    ]
}
```
or use postman collection added to the repository


Using docker
```commandline
docker build -t flex_optimize . 
docker compose up
```

export docker image
```commandline
docker save --output flex_optimize.tar flex_optimize
```