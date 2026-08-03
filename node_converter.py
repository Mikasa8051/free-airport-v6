import json
import urllib.parse


# =====================================================
# 主入口
# =====================================================

def build_config(node):

    try:

        if node.startswith("trojan://"):

            return trojan_config(node)

    except Exception as e:

        print("配置生成失败:", e)

        return None


    return None



# =====================================================
# 基础Xray配置
# =====================================================

def base_config(outbound):


    return {


        "log": {

            "loglevel": "info"

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
# 清理SNI
# =====================================================

def clean_sni(sni):


    if not sni:

        return ""


    sni = urllib.parse.unquote(sni)


    # 去除路径

    if "/" in sni:

        sni = sni.split("/")[0]


    return sni





# =====================================================
# Trojan解析
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




    # -----------------------
    # TLS
    # -----------------------

    tls = {}



    # SNI

    if params.get("sni"):


        tls["serverName"] = clean_sni(

            params["sni"][0]

        )


    else:


        tls["serverName"] = url.hostname





    # fingerprint

    if params.get("fp"):


        tls["fingerprint"] = params["fp"][0]

    else:


        # 免费节点常用

        tls["fingerprint"] = "chrome"






    # allowInsecure

    if params.get("allowInsecure"):


        value = params["allowInsecure"][0]


        if value in [

            "1",

            "true",

            "True"

        ]:


            tls["allowInsecure"] = True






    stream = {


        "network":

        params.get(

            "type",

            ["tcp"]

        )[0],



        "security":

        "tls",



        "tlsSettings":

        tls

    }





    outbound = {


        "protocol":

        "trojan",



        "settings": {


            "servers": [

                server

            ]

        },



        "streamSettings":

        stream

    }





    return base_config(outbound)
