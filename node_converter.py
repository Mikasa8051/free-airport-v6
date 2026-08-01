import json
import base64
import urllib.parse



def build_config(node):

    try:

        if node.startswith("vless://"):

            return vless_config(node)


        if node.startswith("vmess://"):

            return vmess_config(node)


        if node.startswith("trojan://"):

            return trojan_config(node)


    except Exception:

        return None


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


    params=urllib.parse.parse_qs(

        url.query

    )



    security=params.get(

        "security",

        [""]

    )[0]



    network=params.get(

        "type",

        ["tcp"]

    )[0]



    user={


        "id":url.username,


        "encryption":"none"

    }




    if "flow" in params:


        user["flow"]=params["flow"][0]





    stream={

        "network":network

    }





    # TLS


    if security=="tls":


        stream["security"]="tls"


        stream["tlsSettings"]={

            "serverName":

            params.get(

                "sni",

                [url.hostname]

            )[0]

        }





    # Reality


    elif security=="reality":


        stream["security"]="reality"


        stream["realitySettings"]={


            "serverName":

            params.get(

                "sni",

                [""]

            )[0],


            "fingerprint":

            params.get(

                "fp",

                ["chrome"]

            )[0],


            "publicKey":

            params.get(

                "pbk",

                [""]

            )[0],


            "shortId":

            params.get(

                "sid",

                [""]

            )[0]


        }





    # WebSocket


    if network=="ws":


        stream["wsSettings"]={


            "path":

            params.get(

                "path",

                ["/"]

            )[0],



            "headers":{


                "Host":

                params.get(

                    "host",

                    [url.hostname]

                )[0]

            }

        }





    # gRPC


    if network=="grpc":


        stream["grpcSettings"]={


            "serviceName":

            params.get(

                "serviceName",

                [""]

            )[0]

        }







    outbound={


        "protocol":"vless",


        "settings":{


            "vnext":[


                {


                    "address":

                    url.hostname,


                    "port":

                    url.port,


                    "users":[user]

                }

            ]

        },


        "streamSettings":stream

    }





    return base_config(outbound)









# =========================
# Trojan
# =========================


def trojan_config(node):


    url=urllib.parse.urlparse(node)


    params=urllib.parse.parse_qs(

        url.query

    )



    outbound={


        "protocol":"trojan",


        "settings":{


            "servers":[


                {


                    "address":

                    url.hostname,


                    "port":

                    url.port,


                    "password":

                    url.username


                }

            ]

        },


        "streamSettings":{


            "security":"tls",


            "tlsSettings":{


                "serverName":

                params.get(

                    "sni",

                    [url.hostname]

                )[0]

            }

        }

    }



    return base_config(outbound)









# =========================
# VMess
# =========================


def vmess_config(node):


    try:


        raw=node.replace(

            "vmess://",

            ""

        )



        info=json.loads(

            base64.b64decode(

                raw+"=="

            ).decode()

        )




        outbound={


            "protocol":"vmess",


            "settings":{


                "vnext":[


                    {


                        "address":

                        info["add"],


                        "port":

                        int(info["port"]),


                        "users":[


                            {


                                "id":

                                info["id"]


                            }

                        ]

                    }

                ]

            }

        }



        return base_config(outbound)



    except Exception:


        return None
