#!/bin/bash

# Create an Upstream for each microservice (none for minIO):
curl -X POST http://localhost:8001/upstreams --data "name=users_upstream"
curl -X POST http://localhost:8001/upstreams --data "name=tracks_upstream"
curl -X POST http://localhost:8001/upstreams --data "name=descriptions_upstream"
curl -X POST http://localhost:8001/upstreams --data "name=playlists_upstream"

# #################################################

# Adding Users Targets to Upstream:
curl -X POST http://localhost:8001/upstreams/users_upstream/targets --data "target=localhost:5000" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/users_upstream/targets --data "target=localhost:5001" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/users_upstream/targets --data "target=localhost:5002" --data "weight=100"

# Adding Users Targets to Upstream:
curl -X POST http://localhost:8001/upstreams/tracks_upstream/targets --data "target=localhost:5100" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/tracks_upstream/targets --data "target=localhost:5101" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/tracks_upstream/targets --data "target=localhost:5102" --data "weight=100"

# Adding Users Targets to Upstream:
curl -X POST http://localhost:8001/upstreams/descriptions_upstream/targets --data "target=localhost:5200" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/descriptions_upstream/targets --data "target=localhost:5201" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/descriptions_upstream/targets --data "target=localhost:5202" --data "weight=100"

# Adding Users Targets to Upstream:
curl -X POST http://localhost:8001/upstreams/playlists_upstream/targets --data "target=localhost:5300" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/playlists_upstream/targets --data "target=localhost:5301" --data "weight=100"
curl -X POST http://localhost:8001/upstreams/playlists_upstream/targets --data "target=localhost:5302" --data "weight=100"

# #################################################

# Add Each Service (Actual Route in our python code):
#homepage/manual add:
curl -X POST http://localhost:8001/services --data 'name=homepage' --data 'url=http://localhost:5000'
# minIO add:
curl -X POST http://localhost:8001/services --data 'name=media_api' --data 'url=http://localhost:9000/tracks'
# microservice adds:
curl -X POST http://localhost:8001/services --data "name=users_api" --data "host=users_upstream" --data "path=/api/v1/resources/musicService/users"
curl -X POST http://localhost:8001/services --data "name=tracks_api" --data "host=tracks_upstream" --data "path=/api/v1/resources/musicService/tracks"
curl -X POST http://localhost:8001/services --data "name=descriptions_api" --data "host=descriptions_upstream" --data "path=/api/v1/resources/musicService/descriptions"
curl -X POST http://localhost:8001/services --data "name=playlists_api" --data "host=playlists_upstream" --data "path=/api/v1/resources/musicService/playlists"

##################################################

# Add Route for the Services:
#homepage/manual add:
curl -X POST http://localhost:8001/services/homepage/routes --data 'hosts[]=localhost' --data 'paths[]=/'
# minIO add:
curl -X POST http://localhost:8001/services/media_api/routes --data 'hosts[]=localhost' --data 'paths[]=/media'
# microservice adds:
curl -X POST http://localhost:8001/services/users_api/routes --data "hosts[]=localhost" --data "paths[]=/users"
curl -X POST http://localhost:8001/services/tracks_api/routes --data "hosts[]=localhost" --data "paths[]=/tracks"
curl -X POST http://localhost:8001/services/descriptions_api/routes --data "hosts[]=localhost" --data "paths[]=/descriptions"
curl -X POST http://localhost:8001/services/playlists_api/routes --data "hosts[]=localhost" --data "paths[]=/playlists"
