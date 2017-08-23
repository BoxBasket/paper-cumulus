from django import forms

from .models import (
    Frame,
    Strip,
    Scene
)

class FrameForm(forms.ModelForm):
    class Meta:
        model = Frame
        fields = ['note', 'order', 'frame_image', 'strip']

def getOrderChoices():
    order_choices = (
        ('1',1),('2',2),('3',3)
        )
    return order_choices
    

class StripCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StripCreateForm, self).__init__(*args, **kwargs)
        
        #order Scene by its 'order' attribute
        self.fields['scene'].queryset = Scene.objects.order_by("order")
        # self.fields['scene'] = forms.ModelChoiceField(
        #     queryset=Scene.objects.order_by("order")
        # )
        

    class Meta:
        model = Strip
        fields = ['scene', "order", 'description']
        # https://docs.djangoproject.com/en/1.10/topics/forms/modelforms/#overriding-the-default-fields
        widgets = {
            'order': forms.Select(choices=getOrderChoices()),
        }
        
        #so I would like to add class to these fields. To do it, investigate crispy forms.