# :headphones::electric_plug: Spotify TA for Splunk
> **WARNING**: This TA is still under construction. Future updates might break existing setups so proceed with care! 

## Installation
#### via GIT:
Clone this repository to $SPLUNK_HOME/etc/apps/ on an Indexer or Heavy Forwarder and restart Splunk.

````
$ git clone https://github.com/st4ple/splunk-spotify-add-on.git
$ splunk restart
````

#### via Splunk UI:

Download the [.zip of this repository](https://github.com/st4ple/splunk-spotify-add-on/archive/master.zip) and upload it to your Splunk instance via 

`Apps -> Manage Apps -> Install App from File`.


## Configuration 

Follow the step-by-step guide here: [:headphones::key: Spotify for Splunk * auth-helper](https://st4ple.github.io/splunk-spotify-auth-helper/)

## Example event:
```json
{
   "_time":1570815472344,
   "context":{
      "external_urls":{
         "spotify":"https://open.spotify.com/playlist/xyz"
      },
      "type":"playlist",
      "uri":"spotify:user:abc:playlist:xyz"
   },
   "device":{
      "id":"111111111",
      "is_active":true,
      "is_private_session":false,
      "is_restricted":false,
      "name":"Oliver\u2018s iPhone",
      "type":"Smartphone",
      "volume_percent":100
   },
   "repeat_state":"off",
   "shuffle_state":false,
   "track":{
      "album":{
         "album_type":"single",
         "artists":[
            {
               "external_urls":{
                  "spotify":"https://open.spotify.com/artist/5wMlMjOLeJfS5DfxqGfm83"
               },
               "id":"5wMlMjOLeJfS5DfxqGfm83",
               "name":"Jan Blomqvist",
               "uri":"spotify:artist:5wMlMjOLeJfS5DfxqGfm83"
            }
         ],
         "external_urls":{
            "spotify":"https://open.spotify.com/album/0pkzFgmpIYTbUwVbn9hpdh"
         },
         "id":"0pkzFgmpIYTbUwVbn9hpdh",
         "images":[
            {
               "height":640,
               "url":"https://i.scdn.co/image/ab67616d0000b273540c6aebe995b29833e73c35",
               "width":640
            },
            {
               "height":300,
               "url":"https://i.scdn.co/image/ab67616d00001e02540c6aebe995b29833e73c35",
               "width":300
            },
            {
               "height":64,
               "url":"https://i.scdn.co/image/ab67616d00004851540c6aebe995b29833e73c35",
               "width":64
            }
         ],
         "name":"Big Jet Plane",
         "release_date":"2011-11-22",
         "release_date_precision":"day",
         "total_tracks":3,
         "uri":"spotify:album:0pkzFgmpIYTbUwVbn9hpdh"
      },
      "artists":[
         {
            "external_urls":{
               "spotify":"https://open.spotify.com/artist/5wMlMjOLeJfS5DfxqGfm83"
            },
            "followers":{
               "total":91246
            },
            "genres":[
               "deep euro house",
               "deep melodic euro house",
               "electronica",
               "minimal techno",
               "new french touch",
               "tech house",
               "tropical house"
            ],
            "id":"5wMlMjOLeJfS5DfxqGfm83",
            "name":"Jan Blomqvist",
            "popularity":56,
            "uri":"spotify:artist:5wMlMjOLeJfS5DfxqGfm83"
         },
         {
            "external_urls":{
               "spotify":"https://open.spotify.com/artist/2bfx0bw0uVRyfikzS3h5Mg"
            },
            "followers":{
               "total":13116
            },
            "genres":[
               "deep euro house",
               "deep melodic euro house",
               "tech house"
            ],
            "id":"2bfx0bw0uVRyfikzS3h5Mg",
            "name":"Animal Trainer",
            "popularity":42,
            "uri":"spotify:artist:2bfx0bw0uVRyfikzS3h5Mg"
         }
      ],
      "audio_features":{
         "acousticness":0.0372,
         "danceability":0.89,
         "duration_ms":400926,
         "energy":0.443,
         "id":"18mfe5YtwXeqhbuSABYVCK",
         "instrumentalness":0.385,
         "key":0,
         "liveness":0.369,
         "loudness":-8.654,
         "mode":1,
         "speechiness":0.0497,
         "tempo":122.002,
         "time_signature":4,
         "track_href":"https://api.spotify.com/v1/tracks/18mfe5YtwXeqhbuSABYVCK",
         "uri":"spotify:track:18mfe5YtwXeqhbuSABYVCK",
         "valence":0.199
      },
      "duration_ms":400926,
      "explicit":false,
      "external_urls":{
         "spotify":"https://open.spotify.com/track/18mfe5YtwXeqhbuSABYVCK"
      },
      "id":"18mfe5YtwXeqhbuSABYVCK",
      "name":"Big Jet Plane - Animal Trainer Remix",
      "popularity":51,
      "preview_url":"https://p.scdn.co/mp3-preview/7423726f66157f4e20bcc2fe75a48a878204cdaf?cid=297bdf6eacd94031bcad131170c5196a",
      "track_number":3,
      "uri":"spotify:track:18mfe5YtwXeqhbuSABYVCK"
   }
}
```
