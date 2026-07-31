import json
import base64
import urllib.parse



def build_config(node):

    """
    节点统一入口
    """

    try:

        if node.startswith("vless://"):

            return vless_config(node)



        if node.startswith("vmess://"):

            return vmess_config(node)



        if node.startswith("trojan://"):

            return trojan_config(node)



        return None


    except Exception:

        return None





def base_config(outbound):


    return {


        "log":{

            "loglevel":"warning"

        },


        "inbounds":[

            {

                "listen":"127.0.0.1",

                "port":10808,

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





# =========================
# VLESS
# =========================

def vless_config(node):


    url=urllib.parse.urlparse(node)


    host=url.hostname

    port=url.port

    uuid=url.username



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







# =========================
# Trojan
# =========================

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







# =========================
# VMess
# =========================

def vmess_config(node):


    try:


        data=node.replace(

            "vmess://",

            ""

        )


        raw=base64.b64decode(

            data+"=="

        )


        info=json.loads(

            raw.decode()

        )



        outbound={


            "protocol":"vmess",


            "settings":{


                "vnext":[

                    {


                        "address":info["add"],


                        "port":int(info["port"]),


                        "users":[

                            {

                                "id":info["id"]

                            }

                        ]

                    }

                ]

            }

        }



        return base_config(outbound)



    except Exception:


        return None
