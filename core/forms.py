from django.forms import FileField
from django.forms import Form


class OrderUploadForm(Form):
    file = FileField(
        label="Upload CSV file",
        required=True,)
