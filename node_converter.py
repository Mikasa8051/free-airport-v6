import urllib.parse


def build_config(node):

    if node.startswith("trojan://"):
        return trojan_config(node)

    return None



def base_config(outbound):

    return {

        "log": {
            "loglevel": "warning"
        },

        "inbounds": [

            {
                "listen": "127.0.0.1",
                "port": 2080,
                "protocol": "socks",
                "settings": {
                    "udp": True
                }
            }

        ],

        "outbounds": [

            outbound

        ]

    }



def clean_sni(sni):

    """
    修复免费节点错误SNI

    例如:
    t.me/ripaojiedian

    转换:
    t.me
    """

    if not sni:

        return None


    sni = urllib.parse.unquote(sni)


    if "/" in sni:

        sni = sni.split("/")[0]


    return sni



def trojan_config(node):

    url = urllib.parse.urlparse(node)


    params = urllib.parse.parse_qs(
        url.query
    )


    password = url.username


    address = url.hostname


    port = int(url.port)



    outbound = {

        "protocol": "trojan",

        "settings": {

            "servers": [

                {

                    "address": address,

                    "port": port,

                    "password": password

                }

            ]

        }

    }



    stream = {

        "network":

            params.get(
                "type",
                ["tcp"]
            )[0],


        "security":

            "tls"

    }



    tls = {}



    sni = params.get(
        "sni",
        [address]
    )[0]



    sni = clean_sni(sni)



    if sni:

        tls["serverName"] = sni



    # 关键修复
    if params.get("allowInsecure"):

        if params["allowInsecure"][0] == "1":

            tls["allowInsecure"] = True



    stream["tlsSettings"] = tls



    outbound["streamSettings"] = stream



    return base_config(outbound)
