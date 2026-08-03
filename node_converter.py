import json
import base64
import urllib.parse


# =====================================================
# 主入口
# =====================================================

def build_config(node):

    try:

        if node.startswith("trojan://"):

            return trojan_config(node)


        elif node.startswith("vless://"):

            return vless_config(node)


        elif node.startswith("vmess://"):

            return vmess_config(node)


    except Exception as e:

        print(
            "节点解析失败:",
            e
        )

        return None


    return None



# =====================================================
# 基础 Xray 配置
# =====================================================

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





# =====================================================
# SNI清洗
# =====================================================

def clean_sni(value):


    if not value:

        return ""


    # URL解码

    value = urllib.parse.unquote(
        value
    )


    # 去掉路径

    if "/" in value:

        value = value.split("/")[0]


    return value





# =====================================================
# Trojan
# =====================================================

def trojan_config(node):


    url = urllib.parse.urlparse(node)


    params = urllib.parse.parse_qs(
        url.query
    )


    server = {


        "address":

        url.hostname,


        "port":

        int(url.port),


        "password":

        url.username

    }



    outbound = {


        "protocol":

        "trojan",


        "settings": {


            "servers": [

                server

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



    # =====================
    # SNI处理
    # =====================

    if params.get("sni"):


        tls["serverName"] = clean_sni(

            params["sni"][0]

        )


    elif params.get("peer"):


        tls["serverName"] = clean_sni(

            params["peer"][0]

        )


    else:


        tls["serverName"] = url.hostname




    # =====================
    # fingerprint
    # =====================

    if params.get("fp"):


        tls["fingerprint"] = params["fp"][0]



    # 注意：
    # Xray 26.x 已删除 allowInsecure
    # 不再写入该参数



    stream["tlsSettings"] = tls





    # =====================
    # websocket
    # =====================

    if stream["network"] == "ws":


        stream["wsSettings"] = {


            "path":

            urllib.parse.unquote(

                params.get(

                    "path",

                    ["/"]

                )[0]

            ),


            "headers": {


                "Host":

                params.get(

                    "host",

                    [url.hostname]

                )[0]

            }

        }



    outbound["streamSettings"] = stream



    return base_config(outbound)





# =====================================================
# VLESS
# =====================================================

def vless_config(node):


    url = urllib.parse.urlparse(node)


    params = urllib.parse.parse_qs(

        url.query

    )


    user = {


        "id":

        url.username,


        "encryption":

        "none"

    }



    if params.get("flow"):


        user["flow"] = params["flow"][0]



    stream = {


        "network":

        params.get(

            "type",

            ["tcp"]

        )[0]

    }



    security = params.get(

        "security",

        [""]

    )[0]



    if security == "tls":


        stream["security"] = "tls"


        stream["tlsSettings"] = {


            "serverName":

            clean_sni(

                params.get(

                    "sni",

                    [url.hostname]

                )[0]

            )

        }



    elif security == "reality":


        stream["security"]="reality"


        stream["realitySettings"]={


            "show":False,


            "serverName":

            clean_sni(

                params.get(

                    "sni",

                    [url.hostname]

                )[0]

            ),


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




    outbound={


        "protocol":

        "vless",


        "settings": {


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


        "streamSettings":

        stream

    }



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


        data += "=" * (

            (-len(data)) % 4

        )


        raw=base64.b64decode(data)


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


            "protocol":

            "vmess",


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



        outbound["streamSettings"]={


            "network":

            info.get(

                "net",

                "tcp"

            )

        }



        return base_config(outbound)



    except Exception as e:


        print(

            "VMess解析失败:",

            e

        )


        return None
