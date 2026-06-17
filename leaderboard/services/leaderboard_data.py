from .leaderboard_memory import LEADERBOARD_KEY, redis_client
from bank.models import BankAccount

def save_accounts_in_redis():
    redis_client.delete(LEADERBOARD_KEY)
    
    accounts = BankAccount.all_bankAccounts()
    
    for account in accounts:
        redis_client.zadd(
            LEADERBOARD_KEY,
            {str(account.id): str(account.total_assets)}
        )
    
def get_leaderboard():
    """
    Builds the current leaderboard from group total assets and
    returns ranked account data for websocket updates.
    """
    
    save_accounts_in_redis()
    leaderboard = redis_client.zrevrange(
        LEADERBOARD_KEY,
        0,
        -1,
        withscores=True
    )
    
    if not leaderboard:
        return []
    
    accounts_ids = [int(item[0]) for item in leaderboard]
    accounts = BankAccount.all_bankAccounts().select_related("group").filter(id__in=accounts_ids)
    account_map = {acc.id: acc for acc in accounts}
    
    result = []
    for rank, (bank_account_id, score) in enumerate(leaderboard, start=1):
        account = account_map.get(int(bank_account_id))
        if account:
            result.append({
                "id": account.id,
                "rank": rank,
                "name": account.group.name,
                "score": f"{score:.2f}",
                "bank_balance": str(account.bank_balance),
                "items_amount": str(account.all_items_amounts),
            })
        
    return result