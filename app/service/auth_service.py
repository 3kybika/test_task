import logging
from fastapi import Depends
from pymongo import MongoClient
from tinode_grpc import pb
import random
import pkg_resources
from app.service import tinode_service
from app.service.utils import get_id


# ToDo - to conf
SECRET_KEY = "your_jwt_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RANDOM_SEED = 42

APP_NAME = "tn_test_task"
APP_VERSION = "2.0.0b2"  # ?!
LIB_VERSION = pkg_resources.get_distribution("tinode_grpc").version
GRPC_VERSION = pkg_resources.get_distribution("grpcio").version
TINODE_HOST = "localhost:16060"

logger = logging.getLogger("AuthService")
random.seed(RANDOM_SEED)

# Настройка MongoDB


def get_session():
    client = MongoClient("mongodb://localhost:27017/")
    return client


class UserExistsException(Exception):
    pass


class AuthService:
    def __init__(
        self,
        mongo_client: MongoClient = Depends(get_session),
        #grpc_service: GrpcService = Depends(GrpcService),
    ):
        self.session = mongo_client
        self.mongo_db = mongo_client.db
        #self.grpc_service = grpc_service

    @staticmethod
    def make_secret(email, pasword):
        return (str(email) + ":" + str(pasword)).encode("utf-8")

    @staticmethod
    def parse_cred(cred):
        result = None
        if cred is not None:
            result = []
            for c in cred.split(","):
                parts = c.split(":")
                result.append(
                    pb.ClientCred(
                        method=parts[0] if len(parts) > 0 else None,
                        value=parts[1] if len(parts) > 1 else None,
                        response=parts[2] if len(parts) > 2 else None,
                    )
                )

        return result

    async def register_new_user(self, email, password):
        msg = [
            tinode_service.register_msg(
                id="asd",
                email=email,
                secret = self.make_secret(email, password),
                scheme = "basic",
                login=False
            )
        ]

        failed, responses = tinode_service.message_loop(msg)
        logger.debug(responses)
        if failed:
            raise UserExistsException() # ToDo
        logger.debug(responses)
        if len(responses) == 0:
            raise UserExistsException() # ToDo
        
        if  responses[0].code != 201:
            #code: 422 "policy violation"
            raise UserExistsException(responses[0])

        return responses


    async def login(self, email, password):
        msg = [
            tinode_service.login_msg(
                id="123",
                email=email,
                secret = self.make_secret(email, password),
                scheme = "basic"
            )
        ]
        failed, responses = tinode_service.message_loop(msg)
        if failed:
            raise UserExistsException() # ToDo
        logger.debug(responses)
        if len(responses) == 0:
            raise UserExistsException() # ToDo
        
        if  responses[0].code != 201:
            raise UserExistsException(responses[0])

        return responses


    """
    ToDo:  didn't have time to use it
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def authentification_exception() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    @staticmethod
    def create_token(user: UserModel) -> TokenSchema:
        user_data = UserJwtSchema(
            id=user.id,
            login=user.login
        )

        now_dttm = datetime.now(timezone.utc)
        payload = {
            "iat": now_dttm,
            "nbf": now_dttm,
            "exp": now_dttm + timedelta(seconds=settings.auth_service_expire_time),
            "sub": str(user_data.id),
            "user": user_data.model_dump()
        }
        token = jwt.encode(
            payload,
            key=settings.auth_service_jwt_secret,
            algorithm=settings.auth_service_jwt_algo
        )

        return TokenSchema(access_token=token)


    @staticmethod
    def validate_token(jwt_token: str) -> UserJwtSchema:
        try:
            payload = jwt.decode(
                jwt=jwt_token,
                key=settings.auth_service_jwt_secret,
                algorithms=[settings.auth_service_jwt_algo]
            )
        except jwt.exceptions.PyJWTError:
            logger.warn("AuthService.authentification_exception() ")
            raise AuthService.authentification_exception() from None

        user_data = payload.get("user")

        try:
            user = UserJwtSchema.model_validate(user_data)
        except ValidationError:
            logger.warn("AuthService.ValidationError() ")
            raise AuthService.authentification_exception() from None

        return user
    """
