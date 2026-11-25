"""Local HTTP Supabase boundary; credentials still pass the real JWT verifier."""
import json
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from uuid import UUID

import jwt
from cryptography.hazmat.primitives.asymmetric import ec


class AuthSource:
    def __init__(self):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.users = {}
        source = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == "/auth/v1/.well-known/jwks.json":
                    key = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(source.key.public_key()))
                    key.update(kid="fixture-key", alg="ES256", use="sig")
                    body = {"keys": [key]}
                elif self.path == "/auth/v1/user":
                    token = self.headers.get("Authorization", "").removeprefix("Bearer ")
                    try:
                        claims = jwt.decode(token, source.key.public_key(), algorithms=["ES256"], audience="authenticated", issuer=source.url + "/auth/v1")
                        body = source.users[claims["sub"]]
                    except Exception:
                        self.send_response(401)
                        self.end_headers()
                        return
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                encoded = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def token(self, actor: UUID, *, verified=True, providers=None, overrides=None, key=None):
        self.users[str(actor)] = {
            "id": str(actor), "email": f"{actor.int}@example.test",
            "email_confirmed_at": "2026-11-17T00:00:00Z" if verified else None,
            "app_metadata": {"providers": providers or ["email"]},
            "user_metadata": {"display_name": "Seed Name", "email_verified": True},
        }
        now = datetime.now(timezone.utc)
        claims = {"sub": str(actor), "exp": now + timedelta(minutes=10),
                  "iat": now, "iss": self.url + "/auth/v1", "aud": "authenticated"}
        claims.update(overrides or {})
        return jwt.encode(claims, key or self.key, algorithm="ES256", headers={"kid": "fixture-key"})

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
