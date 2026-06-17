import redis

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=3,
    decode_responses=True
)

LEADERBOARD_KEY = "groups_leaderboard"