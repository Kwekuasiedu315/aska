# from django_select2.forms import ModelSelect2Widget
# from django import forms

# from api.models import School, District


# class SchoolAdminForm(forms.ModelForm):
#     class Meta:
#         fields = "__all__"
#         model = School
#         widgets = {
#             "district": ModelSelect2Widget(
#                 model=District, search_fields=["name__icontains"]
#             )
#         }
