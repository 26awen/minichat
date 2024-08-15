import os


from sqlalchemy import create_engine

from flask import Flask
from flask import Blueprint
from flask import Response
from flask import stream_with_context
from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse

from minichat.db_moldes import Base

from minichat.client_openai import ClientOpenai
from minichat.client_coze import ClientCoze
from minichat.client_claude import ClientClaude


from minichat.logbot import logger

from minichat.config_schema import Config
from minichat.config_schema import ClientType

"""
Base set
"""
where_ami = os.path.dirname(__file__)
"""
End of base set
"""


"""
To start a sqlalchemy engine:
"""
engine = create_engine("sqlite:///chatline.db", echo=False)
Base.metadata.create_all(engine)
"""
End of init of the sqlalchemy engine
"""

"""Init the ai_client, Then if there is a 
   client type in the client request, ai_client will be reset.
"""
cfig = Config.load(os.path.join(where_ami, "minichat.json"))
match cfig.client_type:
    case ClientType.OPENAI.value:
        ai_client = ClientOpenai(cfig, engine)
    case ClientType.COZE.value:
        ai_client = ClientCoze(cfig, engine)
    case ClientType.CLAUDE.value:
        ai_client = ClientClaude(cfig, engine)
    case _:
        ai_client = ClientOpenai(cfig, engine)
"""
End of init ai_client
"""


# print(ai_client)


def flask_app():
    # When fetch from client，should use ‘flush’ to print
    # the iter message immediutly

    app = Flask(__name__)
    app.config["SECRET_KEY"] = cfig.server.secret

    chat_api_bp = Blueprint("chat", __name__)
    api = Api(chat_api_bp)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("t_id", type=int, help="the chat thread id")
    post_parser.add_argument("user_id", type=int, help="the user identify num")
    post_parser.add_argument("role", type=str, help="role of message")
    post_parser.add_argument("content", type=str, help="msg to chat with ai")
    # response_format is used to change the response format,
    # which is used to return the response in different formats.
    # default is text, and the other is json
    post_parser.add_argument(
        "response_format", type=str, help="response format: json or text"
    )

    """
    Post arguments below are used to change to server config, 
    which is configed in the minichat.json file. 
    """
    post_parser.add_argument(
        "client_type", type=str, help="set the client type from client side"
    )

    # get method arguments, not used by now
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("user_id", type=int, help="the user identify num")

    class Chat(Resource):
        def post(self):
            logger.opt(colors=True).info("<yellow>New request=></yellow>")
            args = post_parser.parse_args()
            t_id, role, content, user_id, client_type, response_format = (
                args.get("t_id"),
                args.get("role"),
                args.get("content"),
                args.get("user_id"),
                args.get("client_type"),
                args.get("response_format"),
            )

            # Reset the ai_client if got client_type from client request
            if client_type is not None:
                cfig.client_type = client_type
            match cfig.client_type:
                case ClientType.OPENAI.value:
                    ai_client = ClientOpenai(cfig, engine)
                case ClientType.COZE.value:
                    ai_client = ClientCoze(cfig, engine)
                case ClientType.CLAUDE.value:
                    ai_client = ClientClaude(cfig, engine)
                case _:
                    ai_client = ClientOpenai(cfig, engine)

            if user_id is None:
                return {"error": "must request with a user id"}
            if t_id is None:
                t_id = ai_client.new_tid(user_id)
            if role is None:
                role = "user"
            if content is None or content == "":
                content = "Who are you and what can you do?"

            msg = ai_client.fetch_messages(user_id=user_id, t_id=t_id)
            if response_format == "json":
                return Response(
                    stream_with_context(
                        ai_client.make_chat_json(
                            msg, user_id, t_id, role, content
                        )
                    ),
                    content_type="text/plain",
                )
            else:
                return Response(
                    stream_with_context(
                        ai_client.make_chat(msg, user_id, t_id, role, content)
                    ),
                    content_type="text/plain",
                )

    # class MaxTid(Resource):
    #     def get(self):
    #         args = get_parser.parse_args()
    #         user_id = args.get("user_id")
    #         if user_id is None:
    #             return {"error": "user_id is needed to get the max t_id"}
    #         return ai_client.get_max_tid(engine, user_id)

    api.add_resource(Chat, "/chat")
    # api.add_resource(MaxTid, "/maxtid")
    app.register_blueprint(chat_api_bp)

    return app


"""
End of init app
"""
