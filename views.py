from django.shortcuts import render, redirect
from .forms import SamTaxFormYear, SampleInputForm, BaseDataInputFormSet, SampleInputMultiplier, BaseDataInputForm, \
    TaxonInputForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.forms import modelformset_factory, BaseModelFormSet, inlineformset_factory, Select, NumberInput
from alga.models import SamTax, Sample, Taxon
from .functions import taxonifier
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
import datetime
from django import forms
from django.contrib.auth.views import login
from django.core.mail import mail_admins


def index_page(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return login(request, template_name='index.html')


@login_required
@permission_required(['alga.add_taxon', 'alga.add_sample', 'alga.add_samtax'], raise_exception=True)
def datainput_form(request):
    DatainputFormSet = inlineformset_factory(Sample, SamTax, extra=10, formset=BaseDataInputFormSet,
                                             can_delete=False, form=BaseDataInputForm)
    if request.method == "POST" and request.is_ajax():
        if request.POST.get('genus' and 'species'):
            taxon_form = TaxonInputForm(request.POST)
            if taxon_form.is_valid():
                taxon_form = taxon_form.save(commit=True)
                if taxon_form.varietas and taxon_form.forma:
                    taxon_name = '{} {} var. {} f. {} {}'.format(taxon_form.genus, taxon_form.species, taxon_form.varietas, taxon_form.forma, taxon_form.note)
                elif taxon_form.varietas:
                    taxon_name = '{} {} var. {} {}'.format(taxon_form.genus, taxon_form.species, taxon_form.varietas, taxon_form.note)
                elif taxon_form.forma:
                    taxon_name = '{} {} f. {} {}'.format(taxon_form.genus, taxon_form.species, taxon_form.forma, taxon_form.note)
                else:
                    taxon_name = '{} {} {}'.format(taxon_form.genus, taxon_form.species, taxon_form.note)
                mail_admins('Új taxon', '{} hozzáadva a fajlistához.'.format(taxon_name))
                return JsonResponse({'taxon_id': taxon_form.pk, 'taxon_name': taxon_name})
            else:
                return HttpResponse("not valid taxon")
        multiplier = request.POST.get('multiplier')
        sample_form = SampleInputForm(request.POST)
        if sample_form.is_valid():
            sample_inst = sample_form.save(commit=False)
            sample_inst.type = 'fitoplankton'
            sample_inst.multiplier = multiplier
            sample_inst.save()
        else:
            return HttpResponse("not valid date!")

        formset = DatainputFormSet(request.POST, instance=sample_inst)
        if formset.is_valid():
            instances = formset.save(commit=True)
            # genus = instances[0].taxon.genus
            # return JsonResponse({'genus': genus, 'multiplier-form': multiplier})
        else:
            return HttpResponse("not valid formset!")
        return HttpResponse("OK")

    else:
        sample_form = SampleInputForm()
        taxon_form = TaxonInputForm
        sample_form_multiplier = SampleInputMultiplier()
        formset = DatainputFormSet()
        return render(request, 'alga/datainput.html', {'dateform': sample_form, 'taxon_form': taxon_form,
                                                       'multiplier_form': sample_form_multiplier, 'formset': formset})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def samtax_form_year(request):
    if request.method == "POST":
        form = SamTaxFormYear(request.POST)
        if form.is_valid():
            return redirect('samtax_form', year=form.cleaned_data['year'])
    else:
        form = SamTaxFormYear()
    return render(request, 'alga/samtax_form_year.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def samtax_form(request, year):
    select_year, ind_table, raw_name = taxonifier(year)

    class BaseTaxonFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.queryset = SamTax.objects.filter(taxon=None)
            for i in range(0, len(self)):
                self[i].fields['taxon'].label = raw_name[i]

        def add_fields(self, form, index):
            super(BaseTaxonFormSet, self).add_fields(form, index)
            form.fields["genus"] = forms.CharField(required=False)
            form.fields["species"] = forms.CharField(required=False)
            form.fields["group"] = forms.CharField(required=False)

    SamTaxFormSet = modelformset_factory(SamTax, fields=('taxon',), formset=BaseTaxonFormSet, extra=len(select_year))
    if request.method == "POST":
        formset = SamTaxFormSet(request.POST, prefix='samtax')
        if formset.is_valid():
            new_taxons = []
            for inst in formset:
                try:
                    if inst.cleaned_data['genus']:
                        genus = inst.cleaned_data['genus']
                        species = inst.cleaned_data['species']
                        group = inst.cleaned_data['group']
                        new_taxon = Taxon(genus=genus, species=species, group=group)
                        new_taxon.save()
                        new_taxons += [new_taxon.id]
                except KeyError:
                    pass
            instances = formset.save(commit=False)
            for idx, instance in enumerate(instances):
                if instance.taxon.pk == 812:
                    instance.taxon = Taxon.objects.get(id=new_taxons[0])
                    del new_taxons[0]
                # in the model `class Meta: select_on_save = True` (required)
                for date, ind in ind_table.items():
                    instance.sample = Sample.objects.get(date=datetime.datetime.strptime(date, '%Y-%m-%d').date())
                    if ind[idx] != "":
                        instance.count_ind = float(ind[idx].replace(',', '.').strip(' '))
                        instance.pk = None
                        instance.save()
    else:
        formset = SamTaxFormSet(initial=select_year, prefix='samtax')
    return render(request, 'alga/samtax_form.html', {'formset': formset, 'raw_name': raw_name})
