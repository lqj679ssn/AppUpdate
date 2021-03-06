import os
import re
# import codecs

import datetime

from AppUpdate.settings import APP_URL
from Apps.models import Apps, Level, Version
from Base.error import Error
from Developer.models import Developer


def get_readable_time_string(t, only_date=False):
    ret_str = str(t.year) + "年"
    if t.month < 10:
        ret_str += "0"
    ret_str += str(t.month) + "月"
    if t.day < 10:
        ret_str += "0"
    ret_str += str(t.day) + "日 "
    if only_date:
        return ret_str
    if t.hour < 10:
        ret_str += "0"
    ret_str += str(t.hour) + "时"
    if t.minute < 10:
        ret_str += "0"
    ret_str += str(t.minute) + "分"

    return ret_str


def get_relevant_time(that_time):
    timestamp_now = int(datetime.datetime.now().timestamp())
    timestamp_crt = int(that_time.timestamp())
    dist = timestamp_now - timestamp_crt
    if dist < 60:
        dist_str = str(int(dist)) + "秒前"
    elif dist < 60 * 60:
        dist_str = str(int(dist / 60)) + "分钟前"
    elif dist < 60 * 60 * 24:
        dist_str = str(int(dist / 60 / 60)) + "小时前"
    elif dist < 60 * 60 * 24 * 30:
        dist_str = str(int(dist / 60 / 60 / 24)) + "天前"
    elif dist < 60 * 60 * 24 * 365:
        dist_str = str(int(dist / 60 / 60 / 24 / 30)) + "个月前"
    else:
        dist_str = str(int(dist / 60 / 60 / 24 / 365)) + "年前"
    return dist_str


def login_to_session(request, user):
    """
    更新登录数据并添加到session
    """
    user.lastLogin = user.thisLogin
    user.lastIpv4 = user.thisIpv4
    user.thisLogin = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user.thisIpv4 = request.META['HTTP_X_FORWARDED_FOR'] \
        if 'HTTP_X_FORWARDED_FOR' in request.META else request.META['REMOTE_ADDR']
    user.save()

    try:
        request.session.cycle_key()
    except:
        pass
    request.session["uid"] = user.pk
    request.session["isLogin"] = True
    return None


def get_user_from_session(request):
    try:
        developer = Developer.objects.get(pk=request.session["uid"])
    except:
        return None
    return developer


def save_file_to_local(save_file, file_path):
    with open(file_path, "wb+") as f:
        for chunk in save_file.chunks():
            f.write(chunk)
        f.close()


def is_legal_string(string, illegal_chars='<>;/\t\n\r\\'):
    for c in illegal_chars:
        if c in string:
            return False
    return True


def is_legal_length(string, string_min=0, string_max=10):
    if len(string) < string_min or len(string) > string_max:
        return False
    return True


def is_legal_level(level, level_min=0, level_max=10):
    try:
        if int(level) < level_min or int(level) > level_max:
            return False
    except:
        return False
    return True


def get_apps_by_english_name_func(app_english_name):
    try:
        apps = Apps.objects.get(appEnglishName=app_english_name)
    except:
        return None, Error.NOT_FOUND_APPS
    if not apps.isAlive:
        return None, Error.APPS_NOT_ALIVE
    return apps, Error.OK


def get_level_func(apps, level):
    try:
        o_level = Level.objects.get(relatedApp=apps, level=level)
    except:
        return None, Error.NOT_FOUND_LEVEL
    return o_level, Error.OK


def get_latest_version_func(apps, level, force_level=False):
    try:
        versions = Version.objects.filter(
            relatedApp=apps,
            isLevelLatest=True,
            isAlive=True,
        ).order_by('-updateDatetime')
        if force_level:
            versions = versions.filter(relatedLevel__level=level)
        else:
            versions = versions.filter(relatedLevel__level__lte=level)
    except:
        return None, Error.NOT_FOUND_VERSION
    if versions.count() == 0:
        return None, Error.NOT_FOUND_VERSION
    return versions[0], Error.OK


def get_version_detail_func(o_version, with_url=False):
    detail = dict(
        # level=o_version.relatedLevel.level,
        # note=o_version.relatedLevel.note,
        description=o_version.description,
        version=o_version.version,
        updateDatetime=get_readable_time_string(o_version.updateDatetime),
        relevantTime=get_relevant_time(o_version.updateDatetime),
        isAlive=o_version.isAlive,
        timeStamp=int(o_version.updateDatetime.timestamp()),
    )

    if with_url and o_version.isAlive and o_version.relatedApp.isAlive:
        detail['url'] = o_version.url
        detail['md5'] = o_version.md5
        detail['sha1'] = o_version.sha1
    return detail


def get_version_func(apps, version):
    try:
        o_version = Version.objects.get(
            relatedApp=apps,
            version=version,
        )
        return o_version, Error.OK
    except:
        return None, Error.NOT_FOUND_VERSION


def get_app_detail(app):
    versions = Version.objects.filter(relatedApp=app, isAlive=True)
    return dict(
        appName=app.appName,
        appEnglishName=app.appEnglishName,
        createDatetime=get_readable_time_string(app.createDatetime),
        relevantTime=get_relevant_time(app.createDatetime),
        isAlive=app.isAlive,
        logo='/app/logo/'+app.appEnglishName+'_'+app.logo if app.logo else '/app/logo/default.png',
        versions=versions.count(),
        description=app.description,
    )


def get_app_list_func():
    apps = Apps.objects.filter(isAlive=True)

    detail_dict = []
    for app in apps:
        detail_dict.append(get_app_detail(app))
    return detail_dict


def get_level_list_func(apps):
    try:
        levels = Level.objects.filter(relatedApp=apps).order_by('level')
    except:
        levels = []

    detail_dict = []
    for o_level in levels:
        versions = Version.objects.filter(relatedApp=apps, relatedLevel=o_level, isAlive=True)
        detail_dict.append(dict(
            level=o_level.level,
            note=o_level.note,
            versions=versions.count(),
        ))
    return detail_dict


def get_version_list_func(apps, level):
    try:
        versions = Version.objects.filter(relatedApp=apps, relatedLevel__level=level, isAlive=True)
    except:
        versions = []

    detail_dict = []
    for o_version in versions:
        detail_dict.append(get_version_detail_func(o_version, with_url=True))
    return detail_dict


def create_app_func(app_name, app_english_name, description):
    matched = re.search('^([a-zA-Z0-9_-]+)$', app_english_name)
    if matched is None:
        return None, Error.ILLEGAL_APP_ENGLISH_NAME
    if not is_legal_string(app_name):
        return None, Error.ILLEGAL_APP_NAME
    if not is_legal_length(app_english_name, string_max=Apps.C['appEnglishNameLength']):
        return None, Error.ILLEGAL_APP_ENGLISH_NAME_LENGTH
    if not is_legal_length(app_name, string_max=Apps.C['appNameLength']):
        return None, Error.ILLEGAL_APP_NAME_LENGTH

    try:
        apps = Apps.create(app_name, app_english_name, description)
    except:
        return None, Error.ADD_APPS_FAILED

    os.mkdir(os.path.join(APP_URL, app_english_name))

    return apps, Error.OK


def create_level_func(apps, level, note):
    if not is_legal_string(note):
        return None, Error.ILLEGAL_NOTE
    if not is_legal_length(note, string_max=Level.C['noteLength']):
        return None, Error.ILLEGAL_NOTE_LENGTH
    if not is_legal_level(level):
        return None, Error.ILLEGAL_LEVEL

    try:
        o_level = Level.create(apps, level, note)
    except:
        return None, Error.ADD_LEVEL_FAILED
    return o_level, Error.OK


def create_version_func(apps, level, version, url, md5, sha1, description):
    o_level, ret_code = get_level_func(apps, level)
    if ret_code != Error.OK:
        return None, ret_code

    try:
        o_version = Version.create(apps, o_level, version, url, md5, sha1, description)
    except:
        return None, Error.ADD_VERSION_FAILED
    return o_version, Error.OK


def get_file_hash(file_path):
    import hashlib

    try:
        file = open(file_path, "rb")
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        while True:
            read = file.read(8096)
            if not read:
                break
            else:
                md5.update(read)
                sha1.update(read)
        str_md5 = md5.hexdigest()
        str_sha1 = sha1.hexdigest()
        if file:
            file.close()
    except:
        return None, None

    return str_md5, str_sha1
