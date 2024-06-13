from django.urls import path
from core.views import WcOrderView

urlpatterns = [
    # woocommerce order_create webhook
    path("wcorders/", WcOrderView.as_view()),
]
