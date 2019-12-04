
## This seedapi.sh gets called from the make file, by calling `make seedapi`.



#
## Start of the POST request scripts to populate the database with tracks,
## using the tracks microservice
#

track_titles=(
  "Glow Like Dat"
  "Let Go Feat. Grabbitz"
  "Big Pimpin"
  "Slow dancing in the dark"
  "Led Spirals"
  "Under Pressure"
  "Stan"
  "Sunflower"
  )

album_titles=(
  "Amen"
  "W:/2016ALBUM/"
  "Vol. 3... Life and Times of S. Carter"
  "Ballads 1"
  "John Wick: Original Motion Picture Soundtrack"
  "Hot Space"
  "The Marshall Mathers LP"
  "Spiderman:Spiderverse"
  )

artists=(
  "Rich Brian"
  "deadmau5"
  "Jay-Z"
  "Joji"
  "Le Castle Vania"
  "Queen"
  "Eminem"
  "Post Malone"
  )

length_seconds=("230" "120" "140" "120" "130" "191" "180" "187")
media_urls=(
  "http://localhost:8000/media/GlowLikeDat_RichBrian.mp3"
  "http://localhost:8000/media/LetGoFeat.Grabbitz_deadmau5.mp3"
  "http://localhost:8000/media/BigPimpin_JayZ.mp3"
  "http://localhost:8000/media/SLOWDANCINGINTHEDARK_Joji.mp3"
  "http://localhost:8000/media/LedSpirals_LeCastleVania.mp3"
  "http://localhost:8000/media/UnderPressure_Queen.mp3"
  "http://localhost:8000/media/Stan_Eminem.mp3"
  "http://localhost:8000/media/Sunflower_PostMalone.mp3"
  )

len=${#track_titles[@]}

 for (( i = 0; i<$len; i++ )); do
   curl -X POST \
   -H "Content-Type: application/json" \
   --data '{"track_title":"'"${track_titles[i]}"'","album_title":"'"${album_titles[i]}"'","artist":"'"${artists[i]}"'","length_seconds":"'"${length_seconds[i]}"'","url_media":"'"${media_urls[i]}"'"}' \
   http://127.0.0.1:5101/api/v1/resources/musicService/tracks
 done


#
## Start of the POST request scripts to populate the database with users, using
## the user microservice
#


users=("avery123" "stroustrup123" "lovelace123")
passwords=("password123" "goodpass" "badpass")
names=("kenytt" "bjorne" "ada")
emails=("avery@mail.com" "c++@mail.com" "programmerOG@mail.com")
len=${#users[@]}


 for (( i = 0; i<$len; i++ )); do
   curl -X POST \
   -H "Content-Type: application/json" \
   --data '{"username":"'"${users[i]}"'","password":"'"${passwords[i]}"'","display_name":"'"${names[i]}"'","email":"'" ${emails[i]} "'"}' \
   http://127.0.0.1:5000/api/v1/resources/musicService/users
 done



#
## Start of the POST request scripts to add descriptions to the database, using the descriptions microservice
#

# Since track_ids are generated randomly, we must know those track_ids ahead of time before descriptions can be populated
# curl -d '{"username" : "lovelace123", "track_id" : "1", "description_text" : "This song cured my depression."}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5002/api/v1/resources/musicService/descriptions
# curl -d '{"username" : "lovelace123", "track_id" : "3", "description_text" : "You get a sunflower, and YOU get a sunflower!"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5002/api/v1/resources/musicService/descriptions



#
## Start of the POST request scripts to add playlists to the database, using the playlists microservice
#


curl -v -d '{"playlist_title" : "The Feels Train", "description" : "Curl up and cry.", "username_id" : "ian123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5300/api/v1/resources/musicService/playlists
curl -v -d '{"playlist_title" : "Tunes to Program to", "description" : "We hackin now boiz.  Im in.", "username_id" : "brendan123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5300/api/v1/resources/musicService/playlists
