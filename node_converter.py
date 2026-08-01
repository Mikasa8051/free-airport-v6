import json
import base64
import urllib.parse



# =====================================================
# 主入口
# =====================================================

def build_config(node):

    try:

        if node.startswith("vless://"):

            return vless_config(node)


        elif node.startswith("vmess://"):

            return vmess_config(node)


        elif node.startswith("trojan://"):

            return trojan_config(node)



    except Exception:

        return None



    return None







# =====================================================
# 基础 Xray 配置
# =====================================================

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









# =====================================================
# VLESS
# =====================================================

def vless_config(node):


    url=urllib.parse.urlparse(node)


    params=urllib.parse.parse_qs(

        url.query

    )



    user={


        "id":url.username,


        "encryption":"none"

    }




    # flow处理

    if params.get("flow"):


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






    # -----------------
    # TLS
    # -----------------

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









    # -----------------
    # Reality
    # -----------------

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









    # -----------------
    # WebSocket
    # -----------------

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









    # -----------------
    # gRPC
    # -----------------

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

                    int(url.port),



                    "users":[

                        user

                    ]

                }


            ]

        },



        "streamSettings":stream

    }





    return base_config(outbound)


# =====================================================
# Trojan
# =====================================================

def trojan_config(node):


    url=urllib.parse.urlparse(node)


    params=urllib.parse.parse_qs(

        url.query

    )



    server={


        "address":

        url.hostname,



        "port":

        int(url.port),



        "password":

        url.username

    }




    outbound={


        "protocol":"trojan",



        "settings":{


            "servers":[

                server

            ]

        }

    }






    stream={


        "network":

        params.get(

            "type",

            ["tcp"]

        )[0],



        "security":"tls"

    }





    tls={}



    if params.get("sni"):


        tls["serverName"]=params["sni"][0]



    elif params.get("peer"):


        tls["serverName"]=params["peer"][0]



    else:


        tls["serverName"]=url.hostname






    if params.get("fp"):


        tls["fingerprint"]=params["fp"][0]





    stream["tlsSettings"]=tls







    if stream["network"]=="ws":


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






    outbound["streamSettings"]=stream



    return base_config(outbound)









# =====================================================
# VMess
# =====================================================

def vmess_config(node):


    try:


        data=node.replace(

            "vmess://",

            ""

        )



        data=data.strip()



        # 兼容缺少=

        data += "=" * (

            (-len(data)) % 4

        )



        raw=base64.b64decode(

            data

        )



        info=json.loads(

            raw.decode(

                "utf-8",

                errors="ignore"

            )

        )







        user={


            "id":

            info.get(

                "id",

                ""

            ),



            "alterId":

            int(

                info.get(

                    "aid",

                    0

                )

            ),



            "security":

            info.get(

                "scy",

                "auto"

            )

        }







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

                            user

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






        # TLS

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

                ),



                "fingerprint":

                info.get(

                    "fp",

                    "chrome"

                )

            }







        # websocket

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
