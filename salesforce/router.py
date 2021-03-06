# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

"""
Database router for SalesforceModel objects.
"""

import logging

from django.apps import apps
from django.conf import settings

log = logging.getLogger(__name__)

def is_sf_database(db, model=None):
    """The alias is a Salesforce database."""
    from django.db import connections
    from salesforce.backend.base import DatabaseWrapper
    if db is None:
        return getattr(model, '_salesforce_object', False)
    else:
        engine = connections[db].settings_dict['ENGINE']
        return (engine == 'salesforce.backend' or
                isinstance(connections[db], DatabaseWrapper))


class ModelRouter(object):
    """
    Database router for Salesforce models.
    """
    @property
    def sf_alias(self):
        return getattr(settings, 'SALESFORCE_DB_ALIAS', 'salesforce')

    def db_for_read(self, model, **hints):
        """
        If given some hints['instance'] that is saved in a db, use related
        fields from the same db. Otherwise if passed a class or instance to
        model, return the salesforce alias if it's a subclass of SalesforceModel.
        """
        if 'instance' in hints:
            db = hints['instance']._state.db
            if db:
                return db
        if getattr(model, '_salesforce_object', False):
            return self.sf_alias

    def db_for_write(self, model, **hints):
        """
        If given some hints['instance'] that is saved in a db, use related
        fields from the same db. Otherwise if passed a class or instance to
        model, return the salesforce alias if it's a subclass of SalesforceModel.
        """
        if 'instance' in hints:
            db = hints['instance']._state.db
            if db:
                return db
        if getattr(model, '_salesforce_object', False):
            return self.sf_alias

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Don't attempt to sync SF models to non SF databases and vice versa.
        """
        if 'model' in hints:
            model = hints['model']
        elif model_name:
            model = apps.get_model(app_label, model_name)
        else:
            # in data migrations
            model = None

        if hasattr(model, '_salesforce_object'):
            # SF models can be migrated if SALESFORCE_DB_ALIAS is e.g.
            # a sqlite3 database or any non-SF database.
            if not (is_sf_database(db) or db == self.sf_alias):
                return False
        else:
            if is_sf_database(db):
                return False
        # TODO: It is usual that "migrate" is currently disallowed for SF.
        # In the future it can be implemented to do a deep check by
        # introspection of compatibily between Django models and SF database.
        if hasattr(model, '_salesforce_object'):
            # return False
            pass
        # Nothing is said about non SF models with non SF databases, because
        # it can be solved by other routers. By default it is enabled if all
        # routers say "None".
