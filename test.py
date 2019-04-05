from functools import cmp_to_key
import redis
from rank import RanklistBase as Ranklist
import functools

r = redis.Redis("127.0.0.1", 6379, 0)

data = [
    {
        'uid': "1234",
        'score': 123,
        'bookname': '局外人',
        'authname': '加缪'

    },
    {
        'uid': "1235",
        'bookname': '我喜欢你，像风走了八千里',
        'authname': '末那大叔',
        'score': 44
    },
    {
        'uid': "1236",
        'bookname': '债务危机',
        'score': 188,
        'authname': '达里欧',
    },
    {
        'uid': "1237",
        'bookname': '全球科技通史',
        'authname': '吴军',
        'score': 99,
    },
    {
        'uid': "1224",
        'score': 12,
        'authname': '霍金',
        'bookname': '霍金沉思录'
    },
    {
        'uid': "1224",
        'bookname': '小丑',
        'authname': 'DG',
        'score': 44
    },
    {
        'uid': "1224",
        'bookname': '脱胎换骨',
        'authname': '克里斯',
        'score': 223
    },
    {
        'uid': "1224",
        'bookname': '间花荨影',
        'authname': '古戈力',
        'score': 11
    }
]
gift_config = {
    "1":{
        "name":"从0到1",
        "something":"something"
    },
    "2~3":{
        "name":"大国崛起",
        "something":"gift img url"
    },
    "4":{
        "name":"python精通",
        "something":"desc ."
    }
}

if __name__ == '__main__':
    # print(data)
    rk = Ranklist('redis_cache',r)
    for item in data:
        rk.push_in(item)
    rk.sort_by("score").add_rank(care='score').add_trend().add_gift(gift_config)
    new_data =rk.top(10)
    print("new_data================",new_data)