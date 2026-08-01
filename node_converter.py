import json
import base64
import urllib.parse



# =========================
# 主入口
# =========================

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






# =========================
# 基础配置
# =========================

def base_config(outbound):


    return {


        "log":{

            "loglevel":"info"

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



    user={


        "id":url.username,


        "encryption":"none"

    }




    # Reality Vision

    if "flow" in params:


        user["flow"]=params["flow"][0]





    network=params.get(

        "type",

        ["tcp"]

    )[0]



    security=params.get(

        "security",

        [""]

    )[0]





    stream={


        "network":network

    }





    # =================
    # TLS
    # =================

    if security=="tls":


        stream["security"]="tls"



        stream["tlsSettings"]={


            "serverName":

            params.get(

                "sni",

                [url.hostname]

            )[0],


            "fingerprint":

            params.get(

                "fp",

                ["chrome"]

            )[0]

        }






    # =================
    # Reality
    # =================

    elif security=="reality":


        stream["security"]="reality"



        stream["realitySettings"]={


            "show":False,


            "serverName":

            params.get(

                "sni",

                [url.hostname]

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






    # =================
    # websocket
    # =================

    if network=="ws":


        stream["wsSettings"]={


            "path":

            urllib.parse.unquote(

                params.get(

                    "path",

                    ["/"]

                )[0]

            ),



            "headers":{


                "Host":

                params.get(

                    "host",

                    [url.hostname]

                )[0]

            }

        }






    # =================
    # grpc
    # =================

    if network=="grpc":


        stream["grpcSettings"]={


            "serviceName":

            params.get(

                "serviceName",

                [""]

            )[0],



            "multiMode":False

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



                    "users":[

                        user

                    ]

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

        }



    }





    stream={


        "security":"tls",



        "tlsSettings":{


            "serverName":

            params.get(

                "sni",

                [url.hostname]

            )[0]

        }

    }




    outbound["streamSettings"]=stream




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



        raw += "=" * (

            -len(raw) % 4

        )




        info=json.loads(

            base64.b64decode(

                raw

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

                                info["id"],



                                "alterId":

                                int(

                                    info.get(

                                        "aid",

                                        0

                                    )

                                )

                            }

                        ]

                    }

                ]

            }

        }




        stream={



            "network":

            info.get(

                "net",

                "tcp"

            )

        }




        if info.get("tls")=="tls":


            stream["security"]="tls"



            stream["tlsSettings"]={


                "serverName":

                info.get(

                    "sni",

                    info.get(

                        "host",

                        ""

                    )

                )

            }





        if stream["network"]=="ws":


            stream["wsSettings"]={


                "path":

                info.get(

                    "path",

                    "/"

                ),



                "headers":{


                    "Host":

                    info.get(

                        "host",

                        info["add"]

                    )

                }

            }






        outbound["streamSettings"]=stream




        return base_config(outbound)




    except Exception:


        return None
