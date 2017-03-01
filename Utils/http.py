# -*- coding: UTF-8 -*-
import re
import json

from django.http import HttpResponse
from Utils.json_utils import ComplexEncoder


reg_b = re.compile(
    r"(android|bb\\d+|meego).+mobile"
    r"|avantgo|bada\\/|blackberry|blazer|compal|elaine"
    r"|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge "
    r"|maemo|midp|mmp|mobile.+firefox|netfront"
    r"|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker"
    r"|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)"
    r"|vodafone|wap|windows (ce|phone)|xda|xiino",
    re.I | re.M)
reg_v = re.compile(
    r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)"
    r"|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )"
    r"|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi"
    r"|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)"
    r"|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)"
    r"|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)"
    r"|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit"
    r"|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)"
    r"|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k"
    r"|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt "
    r"|kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw"
    r"|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)"
    r"|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]"
    r"|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im"
    r"|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)"
    r"|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)"
    r"|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)"
    r"|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)"
    r"|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)"
    r"|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9"
    r"|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc"
    r"|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-",
    re.I | re.M)


def get_client_ip(request):
    '''获得访问者的IP地址'''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def putNoneToString(x):
    if isinstance(x,dict):
        for key in x:
            x[key] = putNoneToString(x[key])
    if isinstance(x,list):
        for i in range(len(x)):
            x[i] = putNoneToString(x[i])
    if x is None:
        x = ''
    return x

def json_response(x):
    return HttpResponse(json.dumps(putNoneToString(x), cls=ComplexEncoder,separators=(',', ':'),ensure_ascii=True))
    #return HttpResponse(json.dumps(x), content_type="application/json")  

def is_mobile_browser(request):
    if 'HTTP_USER_AGENT' in request.META:
        user_agent = request.META['HTTP_USER_AGENT']
        b = reg_b.search(user_agent)
        v = reg_v.search(user_agent[0:4])
        if b or v:
            return True
    else:
        return False