import json
import base64
import urllib.parse



def decode_node(node):

    try:

        if node.startswith("vmess://"):

            data=node[8:]

            raw=base64.b64decode(
                data+"=="
            )

            return json.loads(
                raw
            )


        elif node.startswith("vless://"):

            return parse_vless(node)


        elif node.startswith("trojan://"):

            return parse_trojan(node)


        elif node.startswith("ss://"):

            return parse_ss(node)


    except:

        return None




def parse_vless(node):

    url=urllib.parse.urlparse(node)

    return {

        "type":"vless",

        "host":url.hostname,

        "port":url.port,

        "uuid":url.username

    }




def parse_trojan(node):

    url=urllib.parse.urlparse(node)

    return {

        "type":"trojan",

        "host":url.hostname,

        "port":url.port,

        "password":url.username

    }




def parse_ss(node):

    return {

        "type":"ss",

        "raw":node

    }
