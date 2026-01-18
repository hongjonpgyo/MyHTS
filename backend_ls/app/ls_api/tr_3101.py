from backend_ls.app.ls_api.ls_client_api import LSClient

def call_3101() -> list[dict]:

    res = LSClient.call(
        tr_cd="o3101",
        body={}
    )

    out = res.get("o3101OutBlock", [])
    if not isinstance(out, list):
        raise RuntimeError("3101 OutBlock is not list")

    return out
