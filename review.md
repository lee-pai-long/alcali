Review general notes
====================

Installing the prod requirements locally fails because of a mysql and postgres dependencies
-------------------------------------------------------------------------------------------

```bash
$ pip install -r requirements/prod.txt 
Collecting ansi2html==1.5.2 (from -r requirements/prod.txt (line 1))
  Using cached https://files.pythonhosted.org/packages/b7/f5/0d658908d70cb902609fbb39b9ce891b99e060fa06e98071d369056e346f/ansi2html-1.5.2.tar.gz
Collecting Django==2.2.2 (from -r requirements/prod.txt (line 2))
  Using cached https://files.pythonhosted.org/packages/eb/4b/743d5008fc7432c714d753e1fc7ee56c6a776dc566cc6cfb4136d46cdcbb/Django-2.2.2-py3-none-any.whl
Collecting django-currentuser==0.4.1 (from -r requirements/prod.txt (line 3))
  Downloading https://files.pythonhosted.org/packages/50/aa/3fd4684180686c1da644586627e4acf2788c7be4602ba494c6cc6c11ad0c/django_currentuser-0.4.1-py2.py3-none-any.whl
Collecting gunicorn==19.9.0 (from -r requirements/prod.txt (line 4))
  Downloading https://files.pythonhosted.org/packages/8c/da/b8dd8deb741bff556db53902d4706774c8e1e67265f69528c14c003644e6/gunicorn-19.9.0-py2.py3-none-any.whl (112kB)
    100% |████████████████████████████████| 122kB 10.0MB/s 
Collecting mysqlclient==1.4.2.post1 (from -r requirements/prod.txt (line 5))
  Downloading https://files.pythonhosted.org/packages/f4/f1/3bb6f64ca7a429729413e6556b7ba5976df06019a5245a43d36032f1061e/mysqlclient-1.4.2.post1.tar.gz (85kB)
    100% |████████████████████████████████| 92kB 35.7MB/s 
    Complete output from command python setup.py egg_info:
    /bin/sh: 1: mysql_config: not found
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/tmp/pip-install-gu9vymm0/mysqlclient/setup.py", line 16, in <module>
        metadata, options = get_config()
      File "/tmp/pip-install-gu9vymm0/mysqlclient/setup_posix.py", line 51, in get_config
        libs = mysql_config("libs")
      File "/tmp/pip-install-gu9vymm0/mysqlclient/setup_posix.py", line 29, in mysql_config
        raise EnvironmentError("%s not found" % (_mysql_config_path,))
    OSError: mysql_config not found
```

Does that mean that any linting or testing must be made in docker ?
If so it is not clear in the Contribute documentation.

It wil lbe better to create dedicated doc(or installer) for mysql and postgres
and let the user choose.

Following the "Try it!" doc fails
---------------------------------

I follow the instruction but after running the services, the web app
wasn't responding.

Looking at the logs of the web service I got:

```bash
$ docker-compose logs web
Attaching to alcali_web_1
web_1     | Performing system checks...
web_1     |
web_1     | Unhandled exception in thread started by <function check_errors.<locals>.wrapper at 0x7fb1712c8268>
web_1     | Traceback (most recent call last):
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/apps/registry.py", line 152, in get_app_config
web_1     |     return self.app_configs[app_label]
web_1     | KeyError: 'admin'
web_1     |
web_1     | During handling of the above exception, another exception occurred:
web_1     |
web_1     | Traceback (most recent call last):
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/utils/autoreload.py", line 225, in wrapper
web_1     |     fn(*args, **kwargs)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/core/management/commands/runserver.py", line 117, in inner_run
web_1     |     self.check(display_num_errors=True)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/core/management/base.py", line 379, in check
web_1     |     include_deployment_checks=include_deployment_checks,
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/core/management/base.py", line 366, in _run_checks
web_1     |     return checks.run_checks(**kwargs)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/core/checks/registry.py", line 71, in run_checks
web_1     |     new_errors = check(app_configs=app_configs)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/core/checks/urls.py", line 40, in check_url_namespaces_unique
web_1     |     all_namespaces = _load_all_namespaces(resolver)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/core/checks/urls.py", line 57, in _load_all_namespaces
web_1     |     url_patterns = getattr(resolver, 'url_patterns', [])
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/utils/functional.py", line 37, in __get__
web_1     |     res = instance.__dict__[self.name] = self.func(instance)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/urls/resolvers.py", line 533, in url_patterns
web_1     |     patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/utils/functional.py", line 37, in __get__
web_1     |     res = instance.__dict__[self.name] = self.func(instance)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/urls/resolvers.py", line 526, in urlconf_module
web_1     |     return import_module(self.urlconf_name)
web_1     |   File "/usr/local/lib/python3.7/importlib/__init__.py", line 127, in import_module
web_1     |     return _bootstrap._gcd_import(name[level:], package, level)
web_1     |   File "<frozen importlib._bootstrap>", line 1006, in _gcd_import
web_1     |   File "<frozen importlib._bootstrap>", line 983, in _find_and_load
web_1     |   File "<frozen importlib._bootstrap>", line 967, in _find_and_load_unlocked
web_1     |   File "<frozen importlib._bootstrap>", line 677, in _load_unlocked
web_1     |   File "<frozen importlib._bootstrap_external>", line 728, in exec_module
web_1     |   File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/alcali/config/urls.py", line 12, in <module>
web_1     |     path('admin/', admin.site.urls),
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/utils/functional.py", line 213, in inner
web_1     |     self._setup()
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/contrib/admin/sites.py", line 526, in _setup
web_1     |     AdminSiteClass = import_string(apps.get_app_config('admin').default_site)
web_1     |   File "/opt/alcali/.local/lib/python3.7/site-packages/django/apps/registry.py", line 159, in get_app_config
web_1     |     raise LookupError(message)
web_1     | LookupError: No installed app with label 'admin'.
```

Even with black there is still a errors detected by pylint
----------------------------------------------------------

*You need both pylint and pylint_django installed to replcate this.*

```bash
$ pylint alcali \
    --output-format=colorized \
    --msg-template='{path}::{obj}:{line} -> [{msg_id}({symbol})] {msg}' \
    --reports=n --load-plugins=pylint_django \
    --errors-only
************* Module alcali.tests.test_views_functions
alcali/tests/test_views_functions.py::test_run_schedule_once:60 -> [E0602(undefined-variable)] Undefined variable 'pendulum'
************* Module alcali.tests.conftest
alcali/tests/conftest.py:::3 -> [E0401(import-error)] Unable to import 'MySQLdb'
************* Module alcali.web.forms
alcali/web/forms.py::AlcaliUserForm.__init__:14 -> [E1003(bad-super-call)] Bad first argument 'UserCreationForm' given to super()
alcali/web/forms.py::AlcaliUserChangeForm.__init__:32 -> [E1003(bad-super-call)] Bad first argument 'UserChangeForm' given to super()
************* Module alcali.web.views.services
alcali/web/views/services.py::schedule:43 -> [E0602(undefined-variable)] Undefined variable 'cron'
************* Module alcali.web.utils.output.highstate_output
alcali/web/utils/output/highstate_output.py::_format_changes:329 -> [E1120(no-value-for-parameter)] No value for argument 'summary' in function call
```

**We can ignore the `MySQLdb` error but other than that all messages are relevant.**
