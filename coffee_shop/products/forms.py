from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'name': forms.TextInput(attrs={'placeholder': 'Например: Эфиопия Иргачифф'}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }
        help_texts = {
            'image': 'Рекомендуемый размер: 800x800px',
        }
    
    # Добавляем иконки для полей
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].icon = 'tag'
        self.fields['description'].icon = 'align-left'
        self.fields['price'].icon = 'ruble-sign'
        self.fields['category'].icon = 'list'
        self.fields['image'].icon = 'image'