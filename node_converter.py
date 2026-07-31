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


    outbound={


        "protocol":"vless",


        "settings":{


            "vnext":[

                {


                    "address":url.hostname,


                    "port":url.port,


                    "users":[

                        {

                            "id":url.username,


                            "encryption":

                            "none"

                        }

                    ]

                }

            ]

        }

    }



    stream={}



    # 传输方式

    network=params.get(

        "type",

        ["tcp"]

    )[0]



    stream["network"]=network





    # TLS

    security=params.get(

        "security",

        [""]

    )[0]



    if security=="tls":


        stream["security"]="tls"



        tls={}



        if "sni" in params:

            tls["serverName"]=params["sni"][0]



        if "fp" in params:

            tls["fingerprint"]=params["fp"][0]



        stream["tlsSettings"]=tls






    # websocket

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






    if stream:


        outbound["streamSettings"]=stream





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


        "security":"tls"

    }



    tls={}



    if "sni" in params:


        tls["serverName"]=params["sni"][0]



    if "peer" in params:


        tls["serverName"]=params["peer"][0]



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


                        "address":

                        info["add"],



                        "port":

                        int(info["port"]),



                        "users":[

                            {

                                "id":

                                info["id"],


                                "alterId":

                                int(info.get(

                                    "aid",

                                    0

                                ))

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


            tls={}


            if info.get("sni"):

                tls["serverName"]=info["sni"]


            stream["tlsSettings"]=tls






        if network=="ws":


            ws={}


            if info.get("path"):

                ws["path"]=info["path"]



            if info.get("host"):


                ws["headers"]={

                    "Host":

                    info["host"]

                }



            stream["wsSettings"]=ws






        outbound["streamSettings"]=stream




        return base_config(outbound)




    except Exception:


        return None
