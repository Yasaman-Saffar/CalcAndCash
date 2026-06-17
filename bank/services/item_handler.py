from ..models import Item
from django.db.models import Q, Max, Min

class ItemHandler:
    """ 
    Provides item filtering, searching 
    and price aggregation utilities.
    """
    
    def get_max_min_price(self):
        return Item.objects.aggregate(
            min_price=Min('current_price'),
            max_price=Max('current_price'),
        )
        
    def search_or_filter(self, queryset, q, price, status):
        if q:
            queryset = self.search_items(q, queryset)
        if price:
            queryset = self.filter_price(price, queryset)
        if status:
            queryset = self.filter_in_bank(status, queryset)  
        return queryset
    
    def search_items(self, q, queryset):
        return queryset.filter(name__icontains=q)
    
    def filter_price(self, price, queryset):
        return queryset.filter(current_price__lte=price)
    
    def filter_in_bank(self, status, queryset):
        if status == 'Yes':
            return queryset.filter(has_owner=False)
        elif status == 'No':
            return queryset.filter(has_owner=True)
        return queryset