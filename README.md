# Install
Download files
```
pip install networkx
pip install PuLP
pip install Flask
python server.py
```
This will start a server on localhost:5000

Use postman to make an optimization request in the following form
POST to localhost:5000/optimize
content-type: aplication/json
with following JSON body:
```yaml
{
    "requestData":[
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
