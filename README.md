# Summary
Flex_optimize provides functionality to select the highest number of swap matches out of a set of possible matches.
The project has three 'optimization' options.
- bipartite: fast one-on-one (cycle length 2) matching
- variable: Variable maximum cycle length by setting 'maxSteps' option
- unlimited: optimization without maximum cycle length

Bipartite uses networkx python library. Variable uses networkx and PuLP libraries. It uses https://github.com/coin-or/Cbc as solver.
Unlimited uses PuLP library and also the cbc solver.

# Install
Download files or clone repository
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
    "optimizer":"variable",
    "pool":"test",
    "maxSteps":3,
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


## Using docker
Save compose.yaml and run following command in the same folder
```commandline
docker compose up
```

Other docker commands
```commandline
docker build --no-cache -t flex_optimize .
docker build --no-cache -t flex_optimize_amd . --platform linux/amd64
docker save --output flex_optimize.tar flex_optimize
```