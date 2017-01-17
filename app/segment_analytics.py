from flask import request

def get_anon_id():
    """Grabs the anonymous id from the request context var for segment"""
    anon_id = request.cookies['ajs_anonymous_id']
    # strip out the '%22' part
    return anon_id.strip('%22')
