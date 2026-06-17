from django.views.generic import TemplateView

class Home(TemplateView):
    template_name = "Core/home_page/home.html"