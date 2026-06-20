from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Handles personal and contest-wide notification websocket connections.
    """
    
    async def connect(self):
        self.group_name = None
        self.players_group_name = None

        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.group_name = f'user_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        self.players_group_name = "contest_players_notifications"
        
        await self.channel_layer.group_add(
            self.players_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
        await self.channel_layer.group_discard(
            self.players_group_name,
            self.channel_name
        )
        
    async def notification(self, event):
        await self.send_json(event["data"])
        
class LeaderboardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "leaderboard_group",
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):  # این نداشتی
        await self.channel_layer.group_discard("leaderboard_group", self.channel_name)

        
    async def update_leaderboard(self, event):
        await self.send_json(event["data"])
        
class ContestConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "contest_users",
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
            await self.channel_layer.group_discard("contest_users", self.channel_name)

        
    async def force_refresh(self, event):
        await self.send_json({
            "type": "FORCE_REFRESH",
        })

class EventConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "inflation_group",
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):  # این نداشتی
        await self.channel_layer.group_discard("inflation_group", self.channel_name)

        
    async def inflation_announcement(self, event):
        await self.send_json({"current_inflation": event["data"]})