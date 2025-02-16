import base64
import json
import logging
import os
import platform
from typing import Any, Dict, List, Optional
import grpc
import grpclib.client
import pkg_resources
from tinode_grpc import pb
from tinode_grpc import pbx


import grpclib

logger = logging.getLogger("TinodeService")

# ToDo: to conf
APP_NAME = "tn_test_task"
APP_VERSION = "2.0.0b2"  # ?!
LIB_VERSION = pkg_resources.get_distribution("tinode_grpc").version
GRPC_VERSION = pkg_resources.get_distribution("grpcio").version

LANG = "en-US"
PLATFORM = "web"
USER_AGENT = user_agent="{}/{} ({}/{}) gRPC-python/{}+{}".format(
                    APP_NAME,
                    APP_VERSION,
                    platform.system(),
                    platform.release(),
                    LIB_VERSION,
                    GRPC_VERSION,
                )
DEVICE_ID = '1'


TINODE_HOST = "tinode:16060"

SECURE = False
SSL_HOST = None


os.environ["GRPC_SSL_CIPHER_SUITES"] = "HIGH+ECDSA"


def hi_msg():
    return pb.ClientMsg(
        hi=pb.ClientHi(
            id='hello',
            user_agent=USER_AGENT,
            ver=APP_VERSION,
            device_id=DEVICE_ID,
            lang=LANG,
            platform=PLATFORM
        )
    )

def register_msg(
    email: str,
    secret: Optional[str] = None,
    scheme: str = 'basic',
    login: bool = True,
    tags: Optional[List[str]] = None,
    public: Optional[bytes] = None,
    private: Optional[bytes] = None,
    id="register"
) -> str:

    """
    Create a new account with the specified `secret` and, if `login`
    is `True`, automatically log in using the new account.

    `scheme`: One of `"basic"` or `"anonymous"`. `"basic"` requires
    a `secret` in the form `"<username>:<password>"`. `secret` should
    be `None` for `"anonymous"`.

    `tags`: Arbitrary case-insensitive strings used for discovering
    users with `find_users()`. Tags may have a prefix which serves as
    a namespace, like `tel:14155551212`. Tags may not contain the
    double quote `"` but may contain spaces.

    `public`: Application-defined content to describe the user,
    visible to all users.

    `private`: Private application-defined content to describe the
    user, visible only to the user.

    Returns a `str` token that can be used for subsequent login
    attempts from different sessions using `scheme="token"`.

    response contains
    """

    if scheme not in ['anonymous', 'basic']:
        raise Exception(f'Authentication scheme must be one of [anonymous, basic]')
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    elif not isinstance(secret, bytes) and scheme != 'anonymous':
        raise Exception(f'Authentication secret must be str or bytes')

    return pb.ClientMsg(
        acc=pb.ClientAcc(
            id=id,
            user_id='new',
            scheme=scheme,
            secret=secret,
            login=login,
            tags=tags,
            cred=parse_cred("email:{}".format(email))
        )
    )

def register_handler(ctrl):
    user_id = json.loads(ctrl.params['user'].decode('utf-8'))
    token = ctrl.params['token']
    token = json.loads(token.decode('utf-8')) if token is not None else None,
    return user_id, token

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


def login_msg(email: str, secret: str, scheme: str = 'basic', id: str = "0") -> str:
    """
    Log in using the specified `secret`. `scheme` must be one of
    `basic` or `token`. This means that anonymous users, created
    using `register()` with `scheme="anynomous"`, are ephemeral
    and cannot log in again from a different session. `"basic"`
    requires a `secret` in the form `"<username>:<password>"`.

    Returns a `str` token that can be used for subsequent login
    attempts from different sessions using `scheme="token"`.
    """

    if scheme not in ['basic', 'token']:
        raise Exception(f'Authentication scheme must be one of [basic, token]')

    # ToDo in db?
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
        if scheme == 'token':
            secret = base64.b64decode(secret)

    elif not isinstance(secret, bytes):
        raise Exception(f'Authentication secret must be str or bytes')

    return pb.ClientMsg(
        login=pb.ClientLogin(
            id=id,
            scheme=scheme,
            secret=secret,
            cred=#[pb.ClientCred(method="email")]
            parse_cred("email:'{}".format(email))
        )
    )

def login_handler(ctrl):
    user_id = json.loads(ctrl.params['user'].decode('utf-8'))
    token = ctrl.params['token']

    return (user_id, token)

#def sub_msg():
#    if isinstance(if_modified_since, dt.datetime):
#        # Convert dt.datetime to milliseconds since 1970 epoch
#        if_modified_since = (if_modified_since - dt.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0
#    resp = await self.__send_message(pb.ClientMsg(
#        get=pb.ClientGet(
#            topic=topic,
#            query=pb.GetQuery(
#                what='sub',  # query for subscribers
#                sub=pb.GetOpts(
#                    if_modified_since=if_modified_since,
#                    limit=limit)))))
#    

def subscribe_msg(topic: str):
    """
    Subscribe to the named `topic`.
    """

    return pb.ClientMsg(
        sub=pb.ClientSub(
            topic=topic,  # topic to be subscribed or attached to
            # get_query=pb.GetQuery(
            #     what='sub',  # query for subscribers
            #        sub=pb.GetOpts(
            #           if_modified_since=if_modified_since,
            #           limit=limit
            #        )
            #     )
        )
    )

def new_topic_msg(
    tags: Optional[List[str]] = None,
    public: Optional[bytes] = None,
    private: Optional[bytes] = None) -> str:

    """
    Create a new group topic and subscribe to it.

    `tags`: Arbitrary case-insensitive strings used for discovering
    topics with `find_topics()`. Tags may have a prefix which serves
    as a namespace, like `region:us`. Tags may not contain the double
    quote `"` but may contain spaces.

    `public`: Application-defined content to describe the topic,
    visible to all users using `get_topic_description()`.

    `private`: Per-user application-defined content to describe
    the topic, visible only to the current user.

    Ctrl.topic - in responce
    """
    return pb.ClientMsg(
        sub=pb.ClientSub(
            topic="new",
            set_query=pb.SetQuery(
                tags=tags,
                desc=pb.SetDesc(
                    public=public,
                    private=private
                )
            )
        )
    )

def publish_msg(topic: str, content: bytes,
    no_echo: bool = False,
    forwarded: Optional[str] = None,
    hashtags: Optional[List[str]] = None,
    mentions: Optional[List[str]] = None,
    mime: Optional[str] = None,
    priority: Optional[Any] = None,
    replace: Optional[str] = None,
    reply: Optional[str] = None,
    thread: Optional[str] = None,
    additional_headers: Optional[Dict[str, str]] = None):
    """
    Distribute content to subscribers to the named `topic`.
    Topic subscribers receive the supplied `content` and, unless
    `no_echo` is `True`, this originating session gets a copy
    of this message like any other currently attached session.

    Returns the `int` sequence ID of the delivered message.

    `forwarded`: Set to `"topic:seq_id"` to indicate that the
    message is a forwarded message.

    `hashtags`: A list of hashtags in this message, without
    the # symbol, e.g. `["onehash", "twohash"]`.

    `mentions`: A list of user IDs mentioned in this message
    (think @alice), e.g. `["usr1XUtEhjv6HND", "usr2il9suCbuko"]`.

    `mime`: MIME-type of this message content, e.g. `"text/x-drafty"`.
    The default value `None` is interpreted as `"text/plain"`.

    `priority`: Message display priority, or a hint for clients that
    this message should be displayed more prominently for a set period
    of time, e.g. `{"level": "high", "expires": "2019-10-06T18:07:30.038Z"}`.
    Think "starred" or "stickied" messages. Can only be set by the
    topic owner or an administrator (with 'A' permission). The `"expires"`
    field is optional.
    
    `replace`: Set to the `":seq_id"` of another message in this
    topic to indicate that this message is a correction or
    replacement for that message.

    `reply`: Set to the `":seq_id"` of another message in this topic
    to indicate that this message is a reply to that message.

    `thread`: To indicate that this message is part of a conversation
    thread in this topic, set to the `":seq_id"` of the first message
    in the thread. Intended for tagging a flat list of messages, not
    creating a tree.

    `additional_headers`: Additional application-specific headers
    which should begin with `"x-<application-name>-"`, although
    not yet enforced.
    """

    head = {
        key: value
        for key, value in {
            'forwarded': forwarded,
            'hashtags': hashtags,
            'mentions': mentions,
            'mime': mime,
            'priority': priority,
            'replace': replace,
            'reply': reply,
            'thread': thread
        }.items()
        if value is not None
    }

    if additional_headers is not None:
        for h in additional_headers:
            head[h] = additional_headers[h]

    return pb.ClientMsg(
        pub=pb.ClientPub(
            topic=topic,
            no_echo=no_echo,
            head=head,
            content=content
        )
    )

def get_message_history_msg(
    topic: str, 
    since: Optional[int] = None, 
    before: Optional[int] = None, 
    limit: Optional[int] = 50
):
    """
    Get message history for the named `topic`. No return value;
    message history will come in through `messages()`, as usual.
    This method returns AFTER the message history comes in.

    `since`: Only return messages with sequence IDs greater than or
    equal to this integer (i.e., inclusive).

    `before`: Only return messages with sequence IDs less than this
    integer (i.e., exclusive).

    `limit`: Only return this many messages.
    """

    return pb.ClientMsg(
        get=pb.ClientGet(
            topic=topic,
            query=pb.GetQuery(
                what='data',
                data=pb.GetOpts(
                    since_id=since,
                    before_id=before,
                    limit=limit
                )
            )
        )
    )

def handle_ctrl(msg):
    pass


def message_loop(messages):
    failed = False
    responses = []
    try:

        # Create secure channel with default credentials.
        channel = None
        if SECURE:
            opts = (('grpc.ssl_target_name_override', SSL_HOST),) if SSL_HOST else None
            channel = grpc.secure_channel(TINODE_HOST, grpc.ssl_channel_credentials(), opts)
        else:
            channel = grpc.insecure_channel(TINODE_HOST)
        
        def gen_message():
            yield hi_msg()
            for message in messages:
                yield message

        # Call the server
        stream = pbx.NodeStub(channel).MessageLoop(gen_message())

        # Read server responses
        for msg in stream:

            if msg.HasField("ctrl"):
                #handle_ctrl(msg.ctrl)
                if msg.ctrl.id == "hello":
                    logger.debug("hello msg sent successfully: {}".format(msg))
                else:
                    responses.append(msg.ctrl)

            elif msg.HasField("meta"):
                what = []
                if len(msg.meta.sub) > 0:
                    what.append("sub")
                if msg.meta.HasField("desc"):
                    what.append("desc")
                if msg.meta.HasField("del"):
                    what.append("del")
                if len(msg.meta.tags) > 0:
                    what.append("tags")
                logger.debug("\r<= meta " + ",".join(what) + " " + msg.meta.topic)

                responses.append(msg)
                #if tn_globals.WaitingFor and tn_globals.WaitingFor.await_id == msg.meta.id:
                #    if 'varname' in tn_globals.WaitingFor:
                #        tn_globals.Variables[tn_globals.WaitingFor.varname] = msg.meta
                #    tn_globals.WaitingFor = None

            elif msg.HasField("data"):
                logger.debug("\n\rFrom: " + msg.data.from_user_id)
                logger.debug("Topic: " + msg.data.topic)
                logger.debug("Seq: " + str(msg.data.seq_id))
                if msg.data.head:
                    logger.debug("Headers:")
                    for key in msg.data.head:
                        logger.debug("\t" + key + ": "+str(msg.data.head[key]))
                logger.debug(json.loads(msg.data.content))

            elif msg.HasField("pres"):
                # 'ON', 'OFF', 'UA', 'UPD', 'GONE', 'ACS', 'TERM', 'MSG', 'READ', 'RECV', 'DEL', 'TAGS'
                what = pb.ServerPres.What.Name(msg.pres.what)
                logger.debug("\r<= pres " + what + " " + msg.pres.topic)

            elif msg.HasField("info"):
                switcher = {
                    pb.READ: 'READ',
                    pb.RECV: 'RECV',
                    pb.KP: 'KP'
                }
                logger.debug("\rMessage #" + str(msg.info.seq_id) + " " + switcher.get(msg.info.what, "unknown") +
                    " by " + msg.info.from_user_id + "; topic=" + msg.info.topic + " (" + msg.topic + ")")

            else:
                logger.debug("\rMessage type not handled" + str(msg))

    #except grpc.RpcError as err:
    #    logger.error("gRPC failed with {0}: {1}".format(err.code(), err.details()))
    #    failed = True
    #except Exception as ex:
    #    logger.error("Request failed: {0}".format(ex))
    #    failed = True
    finally:
        logger.debug('Shutting down...')
        channel.close()

    return failed, responses
