from django import forms
from alga.models import Taxon, Sample, SamTax
from django.forms import BaseModelFormSet, BaseInlineFormSet, ModelForm, Textarea, TextInput, NumberInput, Select


class SamTaxFormYear(forms.Form):
    years = [(str(i), str(i)) for i in range(2013, 2017)]
    year = forms.ChoiceField(label='Válassz évet, de gyorsan!', choices=years)


class BaseDataInputFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Taxon.objects.filter(genus=None)

    def add_fields(self, form, index):
        super(BaseDataInputFormSet, self).add_fields(form, index)


class BaseDataInputForm(ModelForm):
    class Meta:
        model = SamTax
        fields = ['taxon', 'count_ind', 'count_cell', 'size_d_width', 'size_height']
        widgets = {'taxon': Select(attrs={'class': 'form-control'}),
                   'count_ind': NumberInput(attrs={'class': 'form-control small-input count'}),
                   'count_cell': NumberInput(attrs={'class': 'form-control small-input count'}),
                   'size_d_width': NumberInput(attrs={'class': 'form-control small-input'}),
                   'size_height': NumberInput(attrs={'class': 'form-control small-input'})}
        labels = {'count_ind': 'Egyedszám', 'count_cell': 'Sejtszám', 'size_d_width': 'Átmérő/szélesség',
                  'size_height': 'Magasság/hosszúság'}


class TaxonForm(forms.Form):
    taxon = forms.CharField(required=False)


class SampleInputForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['date', 'location', 'water', 'note']
        widgets = {
            'location': TextInput(attrs={'class': 'form-control'}),
            'water': TextInput(attrs={'class': 'form-control'}),
            'note': Textarea(attrs={'class': 'form-control', 'rows': '2'}),
        }
        labels = {
            'date': 'Dátum',
            'location': 'Hely',
            'water': 'Víztest',
            'note': 'Jegyzet',
        }


class TaxonInputForm(ModelForm):
    class Meta:
        model = Taxon
        fields = ['genus', 'species', 'varietas', 'forma', 'note']
        widgets = {
            'genus': TextInput(attrs={'class': 'form-control'}),
            'species': TextInput(attrs={'class': 'form-control'}),
            'varietas': TextInput(attrs={'class': 'form-control'}),
            'forma': TextInput(attrs={'class': 'form-control'}),
            'note': TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'note': 'Megjegyzés'
        }


class SampleInputMultiplier(forms.Form):
    n = forms.IntegerField(label='Átszámolt átmérők száma', widget=forms.NumberInput(attrs={'class': 'form-control input-sm'}))
    d = forms.IntegerField(label='A kamra zárólapjának átmérője (mm)', widget=forms.NumberInput(attrs={'class': 'form-control input-sm'}))
    a = forms.IntegerField(label='Az átszámolt sáv szélessége (µm)', widget=forms.NumberInput(attrs={'class': 'form-control input-sm'}))
    V = forms.DecimalField(label='A számlálókamra térfogata (ml)', decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control input-sm'}))
