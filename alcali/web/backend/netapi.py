import os
import json
from contextlib import contextmanager
from urllib.error import URLError

import pendulum
from pepper import Pepper, PepperException

# TODO: Clear the dependency between this module and the middleware:
#       There is 3 functions in this module, that can be consider part
#       of the business logic, that directly depend on that
#       django middleware, to to test the business logic
#       we'll need the django context. It would be nice
#       to isolate the two, by dependency injection for example.
from django_currentuser.middleware import get_current_user

from ..utils.input import RawCommand
from ..models.alcali import Minions, Functions, MinionsCustomFields, Keys, Schedule

url = os.environ.get("SALT_URL")


@contextmanager
def api_connect():
    user = get_current_user()
    # NOTE: The ignore_ssl_errors value should be the choice of the user,
    #       especially if the flag is switch from the original one.
    api = Pepper(url, ignore_ssl_errors=True)
    try:
        login_ret = api.login(
            # XXX: Why do we have to force the type of user.username ?
            # NOTE: I think it is better to user keyword when theire is
            #       some sort of computation on the right, even if it is a simple
            #       one, it make the api calls more readable.
            str(user.username), user.user_settings.token, os.environ.get("SALT_AUTH")
        )
        user.user_settings.salt_permissions = json.dumps(login_ret["perms"])
        user.save()
        yield api

    # XXX: Where does ConnectionRefusedError comes from ?
    except (PepperException, ConnectionRefusedError, URLError) as e:
        # TODO: Switch to a logger instance which the user can control on it.
        print("Can't connect to {url}: {e}".format(url=url, e=e))
        yield


def get_keys(refresh=False):
    if refresh:
        # Salt return to minion status.
        minion_status = {
            "minions_rejected": "rejected",
            "minions_denied": "denied",
            "minions_pre": "unaccepted",
            "minions": "accepted",
        }
        # NOTE: In this function(and all other in this module),
        #       you directly depend on api_connect which is performing both
        #         - a external HTTP call
        #         - a DB operation(user.save)
        #       So to unit test get_keys you'll need to set up a
        #       DB and salt server, by injecting either the api_connect
        #       callable or better an api object, we can isolate the behavior
        #       of each function and test them.
        with api_connect() as api:
            # NOTE: I think overloading the same variable is unnessessary,
            #       and can create confusion why not just
            #       api.wheel("key.list_all")["return"][0]["data"]["return"]
            api_ret = api.wheel("key.list_all")
            api_ret = api_ret["return"][0]["data"]["return"]

            Keys.objects.all().delete()
            for key, value in minion_status.items():
                for minion in api_ret[key]:
                    finger_ret = api.wheel(
                        "key.finger", match=minion, hash_type="sha256"
                    )
                    # NOTE: Same remark here about overloading variables.
                    finger_ret = finger_ret["return"][0]["data"]["return"][key]
                    obj, created = Keys.objects.update_or_create(
                        minion_id=minion,
                        defaults={"status": value, "pub": finger_ret[minion]},
                    )
                    if created:
                        pass
                        # LOG CREATED

    return Keys.objects.all()


def refresh_minion(minion_id):
    with api_connect() as api:
        grain = api.local(minion_id, "grains.items")
        grain = grain["return"][0]
        # TODO: return smt useful, better error mgmt.
        if grain.get(minion_id):
            pillar = api.local(minion_id, "pillar.items")
            pillar = pillar["return"][0]
            Minions.objects.update_or_create(
                minion_id=minion_id,
                defaults={
                    "grain": json.dumps(grain[minion_id]),
                    "pillar": json.dumps(pillar[minion_id]),
                },
            )
            minion_fields = MinionsCustomFields.objects.values(
                "name", "function"
            ).distinct()
            for field in minion_fields:
                # NOTE: The S/N ratio here is bigger than necessary,
                #       1. name is only used once, so no need to alias it
                #       2. func is used twice but the difference in performance
                #          between a local access and a dict key access seems
                #          negligeable compared to the semantic value of field.
                #       3. parsed is also unnessessary, what we really want is
                #          custom_field_return so why not just
                #          run_raw(comm_inst.parse())
                #       It will remove 3 variables that add noise
                #       to our main goal:
                #       run a salt function on a minion,
                #       create a custom field with the result.
                #       Which stated like this can justify its own function
                #       by the way.
                name = field["name"]
                func = field["function"]
                comm_inst = RawCommand("salt {} {}".format(minion_id, func))
                parsed = comm_inst.parse()
                custom_field_return = run_raw(parsed)
                MinionsCustomFields.objects.update_or_create(
                    name=name,
                    function=func,
                    minion=Minions.objects.get(minion_id=minion_id),
                    defaults={"value": json.dumps(custom_field_return[minion_id])},
                )


def run_job(tgt, fun, args, kwargs=None):
    with api_connect() as api:
        api_ret = api.local(tgt, fun, arg=args, kwarg=kwargs)
    # XXX: Why not just returning api_ret["return"][0]?
    api_ret = api_ret["return"][0]
    return api_ret


def run_raw(load):
    with api_connect() as api:
        api_ret = api.low(load)
    api_ret = api_ret["return"][0]
    return api_ret


def run_runner(fun, args, kwargs=None):
    with api_connect() as api:
        api_ret = api.runner(fun, arg=args, kwarg=kwargs)
    api_ret = api_ret["return"][0]
    return api_ret


def run_wheel(fun, args, kwarg=None, **kwargs):
    with api_connect() as api:
        api_ret = api.wheel(fun, arg=args, kwarg=kwarg, **kwargs)
    api_ret = api_ret["return"][0]
    return api_ret


def get_events():
    with api_connect() as api:
        response = api.req_stream("/events")
    return response


def init_db(target):
    with api_connect() as api:
        # Modules.
        modules_func = api.local(target, "sys.list_functions")
        modules_func = modules_func["return"][0][target]

        modules_doc = api.local(target, "sys.doc")

        for func in modules_func:
            desc = modules_doc["return"][0][target][func]

            Functions.objects.update_or_create(
                name=func, type="local", description=desc or ""
            )
        # Runner.
        # TODO: Factorize.
        runner_func = api.local(target, "sys.list_runner_functions")
        runner_func = runner_func["return"][0][target]

        runner_doc = api.local(target, "sys.runner_doc")

        for func in runner_func:
            desc = runner_doc["return"][0][target][func]

            Functions.objects.update_or_create(
                name=func, type="runner", description=desc or ""
            )
        wheel_docs = api.runner("doc.wheel")
        wheel_docs = wheel_docs["return"][0]
        for fun, doc in wheel_docs.items():
            Functions.objects.update_or_create(
                name=fun, type="wheel", description=doc or ""
            )
    return {"something": "useful"}


def manage_key(action, target, kwargs):
    with api_connect() as api:
        response = api.wheel("key.{}".format(action), match=target, **kwargs)
    return response


def set_perms():
    # XXX: Which of those instruction can throw the URLError ?
    #      the rest can live outside of this try/except block
    try:
        user = get_current_user()
        api = Pepper(url, ignore_ssl_errors=True)
        login_ret = api.login(
            str(user.username), user.user_settings.token, os.environ.get("SALT_AUTH")
        )
        user.user_settings.salt_permissions = json.dumps(login_ret["perms"])
        user.save()
    # NOTE: I'll recommend contextlib.suppress,
    # https://docs.python.org/3/library/contextlib.html#contextlib.suppress
    except URLError:
        pass


def refresh_schedules(minion=None):
    minion = minion or "*"
    with api_connect() as api:
        api_ret = api.local(minion, "schedule.list", kwarg={"return_yaml": False})
    # XXX: If I understand correctly api_ret["return"][0] is a dict with each
    #      key being the minion_id and each value being a dict of jobs.
    #      So can't we use something like:
    #      `for minion_id, minion_jobs in api_ret["return"][0].items():`
    #      Or since we're looping over it, and then return it maybe a alias
    #      can be usefull here: minion = api_ret["return"][0]
    #      But that will require a change of previous `minion` to `minion_name`
    for minion_id in api_ret["return"][0]:
        # TODO: error mgmt
        minion_jobs = api_ret["return"][0][minion_id]
        Schedule.objects.filter(minion=minion_id).delete()
        for job_name in minion_jobs:
            Schedule.objects.create(
                minion=minion_id, name=job_name, job=json.dumps(minion_jobs[job_name])
            )
    return api_ret["return"][0]


def manage_schedules(action, name, minion):
    with api_connect() as api:
        api_ret = api.local(minion, "schedule.{}".format(action), arg=name)
    for target in api_ret["return"][0]:
        # If action was successful.
        if api_ret["return"][0][target]["result"]:
            if "delete" in action:
                Schedule.objects.filter(minion=minion, name=name).delete()
            else:
                # XXX: Why not refresh before get so you have to try it only once ?
                try:
                    sched = Schedule.objects.filter(minion=minion, name=name).get()
                except Schedule.DoesNotExist:
                    refresh_schedules(minion)
                    try:
                        sched = Schedule.objects.filter(minion=minion, name=name).get()
                    except Schedule.DoesNotExist:
                        # XXX: If we return False here, shouldn't we return True here
                        return False
                loaded_job = sched.loaded_job()
                if "enable" in action:
                    loaded_job["enabled"] = True
                elif "disable" in action:
                    loaded_job["enabled"] = False
                sched.job = json.dumps(loaded_job)
                sched.save()


def create_schedules(
    target,
    *args,
    function=None,
    cron=None,
    once=None,
    once_fmt=None,
    name=None,
    **kwargs
):
    name = name or pendulum.now().format("YYYYMMDDHHmmss")
    comm_inst = RawCommand(
        "salt {} schedule.add {} function='{}'".format(target, name, function)
    )
    parsed = comm_inst.parse()
    if args:
        parsed[0]["arg"].append("job_args={}".format(args))
    if kwargs:
        parsed[0]["arg"].append("job_kwargs={}".format(kwargs))
    if cron:
        parsed[0]["arg"].append("cron={}".format(cron))
    if once and once_fmt:
        parsed[0]["arg"].append("once={}".format(once))
        parsed[0]["arg"].append("once_fmt={}".format(once_fmt))
    ret = run_raw(parsed)
    return ret
