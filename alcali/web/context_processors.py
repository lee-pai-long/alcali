from alcali.web.models.alcali import Notifications


def notifications(request):
    if request.user.is_authenticated:
        # XXX: This a bit of a nitpick but I'll avoid lego naming
        #      variables with their types, since notifs is a plurar
        #      we know it is a collection, and looking at the right side
        #      we know it is a list.
        notifs_list = []
        notifs = Notifications.objects.all()
        for notif in notifs:
            # XXX: We don't really need notif_data, we can
            #      just append the our dict and redure the S/N
            #      ratio.
            notif_data = {
                "notif_attr": notif.notif_attr(),
                "id": notif.id,
                "datetime": notif.datetime(),
            }
            notifs_list.append(notif_data)
        return {"notifs_list": notifs_list}
    # XXX: Souldn't it return a 403 error ?
    return {}
