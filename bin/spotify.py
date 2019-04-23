import sys
import xml.dom.minidom, xml.sax.saxutils
import json
import logging
import os
import md5
import requests
import base64

SCHEME = """<scheme>
    <title>Spotify</title>
    <description>Index all tracks (and associated meta-data) you listen to on Spotify.</description>
    <use_external_validation>true</use_external_validation>
    <streaming_mode>simple</streaming_mode>
    <endpoint>
        <args>
            <arg name="name">
                <title>Name</title>
                <description>Unique identifier for this Modular Input instance (e.g. Spotify user name).</description>
            </arg>
            <arg name="client_id">
                <title>Client ID</title>
                <description>Your Spotify Application Client ID. See docs for details.</description>
            </arg>
            <arg name="client_secret">
                <title>Client Secret</title>
                <description>Your Spotify Application Client Secret. See docs for details.</description>
            </arg>
            <arg name="redirect_uri">
                <title>Redirect URI</title>
                <description>A valid redirect URI that you have added to your Spotify Application. See docs for details.</description>
            </arg>
            <arg name="code">
                <title>Authorization Code</title>
                <description>The authorization code you received on your redirect URI. See docs for details.</description>
            </arg>
        </args>
    </endpoint>
</scheme>
"""

def do_scheme():
    print SCHEME


def validate_arguments():
    val_data = get_validation_data()

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': val_data['code'],
        'redirect_uri': val_data['redirect_uri'],
        'client_id': val_data['client_id'],
        'client_secret': val_data['client_secret']
    }
    url = 'https://accounts.spotify.com/api/token'
    response = requests.post(url, headers=headers, data=data)
    data = response.json()
    refresh_token = data['refresh_token']

    file_path = get_encoded_file_path(val_data['checkpoint_dir'], val_data['client_id'], "token")
    with open(file_path, 'w+') as f:
        f.write(str(refresh_token))
    f.close()
    pass


# Routine to index data
def run_script(): 

    config = get_config()

    client_id = config["client_id"]
    client_secret = config['client_secret']

    refresh_token = read_refresh_token(config)

    refresh_headers = {'Authorization': 'Basic '+base64.b64encode(client_id+":"+client_secret)}
    refresh_data = {'grant_type': 'refresh_token','refresh_token': refresh_token}
    
    refresh_response = requests.post('https://accounts.spotify.com/api/token', headers=refresh_headers, data=refresh_data)
    
    refresh_data = refresh_response.json()
    access_token = refresh_data['access_token']
    #scope = refresh_data['scope']
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+access_token,
    }

    after = read_checkpoint(config)

    # the first the script is executed, we read the user's history. this returns the last 50 tracks the user played.
    # this specific API endpoint does NOT contain any playback device information.
    if (after is None):
        response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers)
        data = response.json()
        
        for item in data['items']:
            item['_time'] = item.pop('played_at')

            del item['track']['available_markets']
            del item['track']['disc_number']
            del item['track']['external_ids']
            del item['track']['href']
            del item['track']['is_local']
            del item['track']['type']
            del item['track']['album']['available_markets']
            del item['track']['album']['href']
            del item['track']['album']['type']

            for idx,artist in enumerate(item['track']['album']['artists']):
                del artist['href']
                del artist['type']
                item['track']['album']['artists'][idx] = artist

            audio_features_response = requests.get("https://api.spotify.com/v1/audio-features/%s" % str(item['track']['id']), headers=headers)
            audio_features_data = audio_features_response.json()
            del audio_features_data['type']
            del audio_features_data['analysis_url']
            item['track']['audio_features'] = audio_features_data

            for idx,artist in enumerate(item['track']['artists']):
                del artist['href']
                del artist['type']
                artist_response = requests.get("https://api.spotify.com/v1/artists/%s" % str(artist['id']), headers=headers)
                artist_data = artist_response.json()
                del artist_data['followers']['href']            
                artist['genres'] = artist_data['genres']
                artist['popularity'] = artist_data['popularity']
                artist['followers'] = artist_data['followers']
                item['track']['artists'][idx] = artist

            if item['context'] != "null":
                if 'href' in item['context']:
                    del item['context']['href']

            print(json.dumps(item, sort_keys=True))
            save_checkpoint(config, "after", item['track']['id'])

    # on the second and all following executions of the script we get the currently playing track. 
    # this API endpoint DOES contain playback device information.
    else: 
        response = requests.get('https://api.spotify.com/v1/me/player', headers=headers)
        data = response.json()

        if (data['item']['id'] != after):
            track = data['item']
            del track['available_markets']
            del track['disc_number']
            del track['external_ids']
            del track['href']
            del track['is_local']
            del track['type']

            del track['album']['available_markets']
            del track['album']['href']
            del track['album']['type']

            for idx,artist in enumerate(track['artists']):
                del artist['href']
                del artist['type']
                artist_response = requests.get("https://api.spotify.com/v1/artists/%s" % str(artist['id']), headers=headers)
                artist_data = artist_response.json()
                artist['genres'] = artist_data['genres']
                artist['popularity'] = artist_data['popularity']
                del artist_data['followers']['href']
                artist['followers'] = artist_data['followers']
                track['artists'][idx] = artist

            for idx,artist in enumerate(track['album']['artists']):
                del artist['href']
                del artist['type']
                track['album']['artists'][idx] = artist

            audio_features_response = requests.get("https://api.spotify.com/v1/audio-features/%s" % str(track['id']), headers=headers)
            audio_features_data = audio_features_response.json()
            del audio_features_data['type']
            del audio_features_data['analysis_url']
            track['audio_features'] = audio_features_data

            del data['item']
            data['track'] = track

            data['_time'] = data.pop('timestamp')
            del data['actions']
            del data['currently_playing_type']
            del data['is_playing']
            del data['progress_ms']

            if data['context'] != "null":
        	    if 'href' in data['context']:
        	        del data['context']['href']

            print(json.dumps(data, sort_keys=True))
            save_checkpoint(config, "after", track['id'])


def validate_conf(config, name): 
    # TODO
    pass


def get_config():
    config = {}

    try:
        # read everything from stdin
        config_str = sys.stdin.read()

        # parse the config XML
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        conf_node = root.getElementsByTagName("configuration")[0]
        if conf_node:
            stanza = conf_node.getElementsByTagName("stanza")[0]
            if stanza:
                stanza_name = stanza.getAttribute("name")
                if stanza_name:
                    params = stanza.getElementsByTagName("param")
                    for param in params:
                        param_name = param.getAttribute("name")
                        if param_name and param.firstChild and \
                           param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                            data = param.firstChild.data
                            config[param_name] = data
                            #logging.debug("XML: '%s' -> '%s'" % (param_name, data))

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
           checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            config["checkpoint_dir"] = checkpnt_node.firstChild.data

        if not config:
            raise Exception, "Invalid configuration received from Splunk."

        # just some validation: make sure these keys are present (required)
        validate_conf(config, "client_id")
        validate_conf(config, "client_secret")
        validate_conf(config, "redirect_uri")
        validate_conf(config, "code")
        validate_conf(config, "checkpoint_dir")

    except Exception, e:
        raise Exception, "Error getting Splunk configuration via STDIN: %s" % str(e)

    return config


def get_validation_data():
    val_data = {}

    # read everything from stdin
    val_str = sys.stdin.read()

    # parse the validation XML
    doc = xml.dom.minidom.parseString(val_str)
    root = doc.documentElement

    logging.debug("XML: found items")
    item_node = root.getElementsByTagName("item")[0]
    if item_node:
        logging.debug("XML: found item")

        name = item_node.getAttribute("name")
        val_data["stanza"] = name

        params_node = item_node.getElementsByTagName("param")
        for param in params_node:
            name = param.getAttribute("name")
            logging.debug("Found param %s" % name)
            if name and param.firstChild and \
               param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                val_data[name] = param.firstChild.data

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
          checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            val_data["checkpoint_dir"] = checkpnt_node.firstChild.data

    return val_data


def get_encoded_file_path(checkpoint_dir, client_id, filetype):
    identifier = filetype+"_"+client_id
    return os.path.join(checkpoint_dir, identifier)


def save_checkpoint(config, filetype, value):
    chk_file = get_encoded_file_path(config["checkpoint_dir"], config['client_id'], filetype)
    with open(chk_file, 'w+') as f:
        f.write(str(value))
    f.close()


def read_checkpoint(config):
    chk_file = get_encoded_file_path(config["checkpoint_dir"], config['client_id'], "after")
    if (os.path.exists(chk_file)):
        with open(chk_file, 'r') as f:
            after = str(f.read())
        f.close()
        return after
    else:
        return None


def read_refresh_token(config):
    chk_file = get_encoded_file_path(config["checkpoint_dir"], config['client_id'], "token")
    refresh_token = None
    if (os.path.exists(chk_file)):
        with open(chk_file, 'r') as f:
            refresh_token = f.read()
        f.close()
    return refresh_token


# Script must implement these args: scheme, validate-arguments
if __name__ == '__main__':
    script_dirpath = os.path.dirname(os.path.join(os.getcwd(), __file__))

    if len(sys.argv) > 1:
        if sys.argv[1] == "--scheme":
            do_scheme()
        elif sys.argv[1] == "--validate-arguments":
            validate_arguments()
        else:
            pass
    else:
        run_script()

    sys.exit(0)