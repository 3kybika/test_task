import pkg_resources
from tinode_grpc import pb
import platform
#tinode_grpc as pb
from tinode_grpc import pbx

import grpc

#    random.seed()
#    id = random.randint(10000,60000)
MSG_ID=42534
APP_NAME="tn_test_task"
APP_VERSION="2.0.0b2" #?!
LIB_VERSION = pkg_resources.get_distribution("tinode_grpc").version
GRPC_VERSION = pkg_resources.get_distribution("grpcio").version
TINODE_HOST = "localhost:16060"

def parse_cred(cred):
    result = None
    if cred is not None:
        result = []
        for c in cred.split(","):
            parts = c.split(":")
            result.append(pb.ClientCred(method=parts[0] if len(parts) > 0 else None,
                value=parts[1] if len(parts) > 1 else None,
                response=parts[2] if len(parts) > 2 else None))

    return result


hi_msg = pb.ClientMsg(
        hi=pb.ClientHi(
            id=str(MSG_ID), #optional
            user_agent=APP_NAME + "/" + APP_VERSION + " (" +
        platform.system() + "/" + platform.release() + "); gRPC-python/" + LIB_VERSION + "+" + GRPC_VERSION,
        ver=LIB_VERSION,
        lang="EN", 
        background=False
        )
    )

acc_msg = pb.ClientMsg(
    acc=pb.ClientAcc(
        id=str(MSG_ID+1), #optional
        user_id="new", # а может user?
        scheme="basic", #cmd.scheme, 
        secret=(str("user_name") + ":" + str("user_password")).encode('utf-8'), 
        login=False,#cmd.do_login, 
        tags=None,
        desc=None,
        cred=parse_cred("email:test@example.com")
    ),
)

login_msg = pb.ClientMsg(
    login=pb.ClientLogin(
        id=str(MSG_ID+2),
        scheme="basic", 
        secret=(str("user_name") + ":" + str("user_password")).encode('utf-8'),
        cred=parse_cred("email:test@example.com")
    )
)
import json
def encode_to_bytes(src):
    if src is None:
        return None
    if isinstance(src, str):
        return ('"' + src + '"').encode()
    return json.dumps(src).encode('utf-8')

sub_msg = pb.ClientMsg(
    sub=pb.ClientSub(
        id=str(MSG_ID+3), 
        topic="new",
        set_query=pb.SetQuery(
            desc=pb.SetDesc(defacs=pb.SetDefacs(
                public="JRWS",
            )),
            sub=pb.SetSub(mode="JRWS"),
            tags=["General"]),
        get_query=None
    ),
)
sub_msg=pb.ClientMsg(
    sub=pb.ClientSub(
        id=str(MSG_ID+4),
        topic="new",
        bkg=False,
        set_query=pb.SetQuery(
            desc=pb.SetDesc(
                public=encode_to_bytes({"fn": 'General Group'}), 
                private=None,
                trusted=None,
                default_acs=pb.DefaultAcsMode(
                    auth="JRWPA",
                    anon="JR"
                )
            ),
            tags=["General", "Test task"]
        ),
        sub=None,
    )
)

pub_msg = pb.ClientMsg(
    pub=pb.ClientPub(
        id=str(MSG_ID+5),
        topic=42534,
        no_echo=True,
        head= {'mime': encode_to_bytes('text/x-drafty')},
        content=encode_to_bytes("message_contenmt")
    ),
)

def gen_msg():
    yield hi_msg
    #yield acc_msg
    yield login_msg
    #yield sub_msg
    #yield pub_msg


channel = grpc.insecure_channel(TINODE_HOST)
channel = grpc.secure_channel(TINODE_HOST, grpc.ssl_channel_credentials(), None)

channel = grpc.insecure_channel(TINODE_HOST)

nodeStub =  pbx.NodeStub(channel)

ml = nodeStub.MessageLoop(gen_msg())

l = list(ml)
print(l)
