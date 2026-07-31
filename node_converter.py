import json
import base64
import urllib.parse



def build_config(node):


    if node.startswith("vless://"):

        return vless_config(node)



    if node.startswith("trojan://"):

        return trojan_config(node)



    if node.startswith("vmess://"):

        return vmess_config(node)



    return None






def base_config(outbound):


    return {


        "log":{

            "loglevel":"warning"

        },


        "inbounds":[

            {

            "port":10808,

            "listen":"127.0.0.1",

            "protocol":"socks",

            "settings":{

                "udp":True

            }

            }

        ],


        "outbounds":[

            outbound

        ]

    }








def vless_config(node):


    url=urllib.parse.urlparse(node)


    uuid=url.username


    host=url.hostname


    port=url.port



    outbound={


        "protocol":"vless",


        "settings":{


            "vnext":[

                {

                "address":host,

                "port":port,

                "users":[

                    {

                    "id":uuid,

                    "encryption":"none"

                    }

                ]

                }

            ]

        }

    }



    return base_config(outbound)







def trojan_config(node):


    url=urllib.parse.urlparse(node)


    outbound={


        "protocol":"trojan",


        "settings":{


            "servers":[

                {

                "address":url.hostname,

                "port":url.port,

                "password":url.username

                }

            ]

        }

    }


    return base_config(outbound)







def vmess_config(node):


    try:


        raw=node.replace(

            "vmess://",

            ""

        )


        data=json.loads(

            base64.b64decode(

                raw+"=="

            )

        )


        outbound={


        "protocol":"vmess",


        "settings":{


            "vnext":[

                {

                "address":data["add"],

                "port":int(data["port"]),

                "users":[

                    {

                    "id":data["id"]

                    }

                ]

                }

            ]

        }

        }


        return base_config(outbound)



    except:


        return None
