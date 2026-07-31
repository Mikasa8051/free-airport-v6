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


        return None


    except Exception:

        return None






# =========================
# 基础配置
# =========================

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


        "outbounds":[outbound]

    }







# =========================
# VLESS
# =========================

def vless_config(node):


    url=urllib.parse.urlparse(node)


    params=urllib.parse.parse_qs(

        url.query,

        keep_blank_values=True

    )



    security=params.get(

        "security",

        ["none"]

    )[0]



    network=params.get(

        "type",

        ["tcp"]

    )[0]





    user={


        "id":url.username,


        "encryption":"none"

    }



    # flow

    if "flow" in params:

        user["flow"]=params["flow"][0]





    outbound={


        "protocol":"vless",


        "settings":{


            "vnext":[

                {

                    "address":url.hostname,


                    "port":url.port,


                    "users":[user]

                }

            ]

        }

    }





    stream={}


    stream["network"]=network



    # =====================
    # TLS
    # =====================

    if security=="tls":


        stream["security"]="tls"


        tls={}



        if "sni" in params:

            tls["serverName"]=params["sni"][0]



        if "fp" in params:

            tls["fingerprint"]=params["fp"][0]



        if "alpn" in params:

            tls["alpn"]=params["alpn"][0].split(",")



        if params.get(

            "allowInsecure",

            ["0"]

        )[0]=="1":

            tls["allowInsecure"]=True



        stream["tlsSettings"]=tls





    # =====================
    # Reality
    # =====================

    if security=="reality":


        stream["security"]="reality"



        reality={}



        if "sni" in params:

            reality["serverName"]=params["sni"][0]



        if "fp" in params:

            reality["fingerprint"]=params["fp"][0]



        if "pbk" in params:

            reality["publicKey"]=params["pbk"][0]


        else:

            return None



        if "sid" in params:

            reality["shortId"]=params["sid"][0]



        stream["realitySettings"]=reality







    # =====================
    # WebSocket
    # =====================

    if network=="ws":


        ws={}



        if "path" in params:


            ws["path"]=urllib.parse.unquote(

                params["path"][0]

            )



        headers={}



        if "host" in params:


            headers["Host"]=params["host"][0]



        if headers:


            ws["headers"]=headers



        stream["wsSettings"]=ws







    # =====================
    # gRPC
    # =====================

    if network=="grpc":


        grpc={}



        if "serviceName" in params:


            grpc["serviceName"]=params["serviceName"][0]



        if "mode" in params:


            grpc["multiMode"] = (

                params["mode"][0]=="multi"

            )



        stream["grpcSettings"]=grpc






    outbound["streamSettings"]=stream



    return base_config(outbound)









# =========================
# Trojan
# =========================

def trojan_config(node):


    url=urllib.parse.urlparse(node)


    params=urllib.parse.parse_qs(

        url.query,

        keep_blank_values=True

    )



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




    stream={

        "security":"tls"

    }




    tls={}



    if "sni" in params:

        tls["serverName"]=params["sni"][0]



    if "fp" in params:

        tls["fingerprint"]=params["fp"][0]



    if tls:

        stream["tlsSettings"]=tls



    outbound["streamSettings"]=stream



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

                                "id":info["id"],


                                "alterId":int(

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



        stream={}



        network=info.get(

            "net",

            "tcp"

        )



        stream["network"]=network




        if info.get("tls")=="tls":


            stream["security"]="tls"


            stream["tlsSettings"]={


                "serverName":

                info.get(

                    "sni",

                    ""

                )

            }





        if network=="ws":


            stream["wsSettings"]={


                "path":

                info.get(

                    "path",

                    ""

                ),


                "headers":{


                    "Host":

                    info.get(

                        "host",

                        ""

                    )

                }

            }



        outbound["streamSettings"]=stream



        return base_config(outbound)



    except Exception:


        return None
