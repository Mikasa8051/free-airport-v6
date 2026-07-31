import os
import platform
import requests
import zipfile


XRAY_URL = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"



def install_xray():

    if os.path.exists("./xray"):
        return


    print("下载Xray核心...")


    r=requests.get(
        XRAY_URL,
        timeout=60
    )


    open(
        "xray.zip",
        "wb"
    ).write(r.content)



    with zipfile.ZipFile(
        "xray.zip"
    ) as z:

        z.extractall(
            "."
        )


    os.chmod(
        "xray",
        0o755
    )


    print(
        "Xray安装完成"
    )



if __name__=="__main__":

    install_xray()
