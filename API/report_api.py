from flask import Flask, request
import json
import os
import requests
import jwt
from flask_cors import CORS


app = Flask(__name__)
CORS(
    app,
    origins="http://localhost:3000",  # Разрешенный origin
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Разрешенные методы
    allow_headers=["Authorization", "Content-Type"],  # Разрешенные заголовки
    supports_credentials=True  # Разрешить куки/авторизацию
)
valid_roles = {"prothetic_user"}


def get_jwks():
    res = requests.get(f"{os.environ["KEYCLOAK_URL"]}/realms/{os.environ["KEYCLOAK_REALM"]}/protocol/openid-connect/certs")
    if res.status_code != 200:
        raise ValueError(res.status_code)
    public_keys = {}
    for jwk in res.json()['keys']:
        public_keys[jwk['kid']] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    return public_keys


def is_valid(token):
    kid = jwt.get_unverified_header(token)['kid']
    public_keys = get_jwks()
    key = public_keys[kid]
    try:
        payload = jwt.decode(token, key=key, algorithms=['RS256'])
        return len(valid_roles & set(payload['realm_access']['roles'])) > 0
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except jwt.InvalidTokenError:
        print("Token is invalid") 
    return False


def get_token(request):
    jwt_token = request.headers.get("Authorization")
    if jwt_token:
        jwt_token = jwt_token.split()[-1]  # "Bearer ${keycloak.token}""
    assert jwt_token, request.headers
    return jwt_token


@app.route("/reports")
def get_reports():
    token = get_token(request)
    if not is_valid(token):
        return "Unauthorized", 401
    return "OK", 200

app.run(host="0.0.0.0", port=8000, debug=True)