# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import django.forms
import django.forms.models
import django.core.exceptions
from django.utils.translation import ugettext_lazy as _
import cms.forms.fields
import cms.models
from django.forms.widgets import Media

from . import models, constants


class RowPluginBaseForm(django.forms.models.ModelForm):
    create = django.forms.IntegerField(
        label=_('Create Columns'),
        help_text=_('Create this number of columns inside'),
        required=False,
        min_value=0,
    )

    class Meta:
        model = models.Bootstrap3RowPlugin
        # fields = ('classes',)
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')


extra_fields = {}
for size, name in constants.DEVICE_CHOICES:
    extra_fields["create_{}_size".format(size)] = django.forms.IntegerField(
        label=_('Column {}'.format(name)),
        help_text=('Width of created columns. You can still change the width of the column afterwards.'),
        required=False,
        min_value=0,
        max_value=constants.GRID_SIZE,
    )
    extra_fields["create_{}_offset".format(size)] = django.forms.IntegerField(
        label=_('Offset {}'.format(name)),
        help_text=('Offset of created columns. You can still change the width of the column afterwards.'),
        required=False,
        min_value=0,
        max_value=constants.GRID_SIZE,
    )


RowPluginForm = type(str('RowPluginBaseForm'), (RowPluginBaseForm,), extra_fields)


class LinkForm(django.forms.models.ModelForm):
    page_link = cms.forms.fields.PageSelectFormField(
        queryset=cms.models.Page.objects.drafts(),
        label=_("Page"),
        required=False,
    )

    def for_site(self, site):
        # override the page_link fields queryset to containt just pages for
        # current site
        self.fields['page_link'].queryset = cms.models.Page.objects.drafts().on_site(site)

    class Meta:
        model = models.Boostrap3ButtonPlugin
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')

    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = Media()
        for field in self.fields.values():
            media = media + field.widget.media
        media._js = ['cms/js/libs/jquery.min.js'] + media._js
        return media
    media = property(_get_media)

    def clean(self):
        cleaned_data = super(LinkForm, self).clean()
        link_fields = {
            'url': cleaned_data.get("url"),
            'page_link': cleaned_data.get("page_link"),
            'mailto': cleaned_data.get("mailto"),
            'phone': cleaned_data.get("phone"),
        }
        error_msg = _("Only one of Page, Link, Email address or Phone is allowed.")
        if len([i for i in link_fields.values() if i]) > 1:
            for field, value in link_fields.items():
                if value:
                    self._errors[field] = self.error_class([error_msg])
            raise django.core.exceptions.ValidationError(error_msg)
        return cleaned_data
