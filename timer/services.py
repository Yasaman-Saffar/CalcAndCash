from bank.models import Event
from bank.services.economy_engine import EconomyEngine

def execute_event(event: Event):
    ee = EconomyEngine()
    
    if event.type == 'inflation':
        ee.apply_inflation(event)
    else:
        ee.apply_interest(event)