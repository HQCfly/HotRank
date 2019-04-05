from datetime import datetime

#future = datetime.strptime('2017-1-17 8:13:01','%Y-%m-%d %H:%M:%S')
def get_me_datetime(dt):

    future = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    delta = future - now
    day_to_hour = delta.days * 24
    hour = delta.seconds/60/60
    minute = (delta.seconds - hour*60*60)/60
    seconds = delta.seconds - hour*60*60 - minute*60
    count_down_dict = {
        "hour": hour + day_to_hour,
        "minute": minute,
        "seconds": seconds
    }
    return count_down_dict

def to_string_time(dt):
    str_format = "{}:{}:{}".format(dt.get("hour"), dt.get("minute"), dt.get("seconds"))
    return str_format

def counter_time(dt):
    dt = get_me_datetime(dt)
    dt = to_string_time(dt)
    return dt

if __name__ == '__main__':
    future = '2019-3-18 8:13:01'
    ret = counter_time(future)
    print(ret)