# 背景介绍：
排行榜业务使用的频率实在太高了，各种活动都会使用排行榜。经过多次开发后我觉得实现一个简单的排行榜库，它能够完成当前我遇到的所有业务逻辑问题，也希望能够帮助到想要快速开发排行榜业务的同行。
# 目前只是第一版Python结合Redis实现热排行功能（简约版）
# 第一个问题解决排序问题，假设数据格式是json格式
```
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
```
一般这些数据是通过数据库获取到的。下面声明一个排行榜实例，
排行榜有一个需求是显示用户的榜单是上升还是下降，这个需要数据库缓存上一次的结果，目前使用的缓存是redis数据库实现。
安装redis移步 https://blog.csdn.net/qq_27695659/article/details/88551219
# 创建rank.py,安装ujson，pip3 isntall ujson
```
import ujson
import functools


class RanklistBase(dict):

    def __init__(self, name, redis_handler, ex=30):
        self.name = name
        self.redis_handler = redis_handler
        self.ex = ex
        self.ranklist = []
        self.plugin_functions = []

    def plugin(self, f=None):
        """
        扩展函数例如：
        def profit(d):
            price = d.get("price")-d.get("cost")
            d.update({"profit":price})
        :param f:
        :return:
        """
        if len(self) > 0:
            raise RuntimeError(
                "在执行命令之前，先安装插件"
            )
        if f:
            self.plugin_functions.append(f)
            
            
    #将数据一个个push_in 到排行榜中
    def push_in(self, item, primary='uid'):
        """
        结构如下：
        {
            "uid":"12345",
            "score":98,
            "something":"something"
        }
        :param item:
        :param primary:
        :return:
        """
        uid = str(item.get(primary))
        item.update({primary: uid})
        [f(item) for f in self.plugin_functions]
        self[uid] = item
        
        
    #python3支持functools.cmp_to_key函数，不再支持cmp了。并且注意两个key是不能变的
    def sort_by(self, key_item):
        """
        将数据从大到小排序
        :param key_item:
        :return:
        """
        sort_list =self.values()
        key = sorted(sort_list, key=functools.cmp_to_key(lambda x, y: int(x[key_item]) - int(y[key_item])),reverse=True)

        self.ranklist =key
        # print(self.ranklist)
        return self

    def sort_by_many(self, *args):
        pass
    #添加新排行榜
    def add_rank(self, care='profit', conflict=True):
        j = 1
        new_rank_list = []
        last_record = {}
        for i in self.ranklist:
            rank_index = {}
            if conflict:
                last_v = last_record.get(care)
                rank_index = last_record.get("rank") if int(
                    i.get(care)) == last_v else j
            i.update({
                "rank":str(rank_index)
            })

            j+=1
            new_rank_list.append(i)
            last_record.update({
                care:i.get(care),
                "rank":str(rank_index)
            })
        self.ranklist = new_rank_list
        return self

    #用户热排行，奖励
    def add_gift(self,gift_config):
        j = 1
        gift_config = self._extend_dict(gift_config)
        new_rank_list = []
        for i in self.ranklist:
            rank_num = i.get("rank")
            i.update({
                "gift":gift_config.get(str(rank_num))
            })
            j+=1
            new_rank_list.append(i)
        self.ranklist = new_rank_list
        return self

    def add_value_from(self,callback,input_fiel, output_field):
        j =1
        new_rank_list = []
        for i in self.ranklist:
            input_value = i.get(input_fiel)
            i.update({
                output_field:callable(input_value)
            })
            j+=1
            new_rank_list.append(i)
        self.ranklist = new_rank_list

        return self
    #添加对象是否上升下降，如果上升向上箭头，下降向下箭头
    def add_trend(self, ref_field="rank"):
        the_cache = self.redis_handler.get(self.name) or '{}'
        the_cache = ujson.loads(the_cache)
        for uid, v in self.items():
            if uid in the_cache:
                p = int(v.get(ref_field))
                c = int(the_cache.get(uid).get(ref_field))
                if p < c:
                    v.update({"trend": "1"})
                elif p == c:
                    v.update({"trend": "0"})
                else:
                    v.update({"trend": "-1"})
            else:
                v.update({"trend": "1"})
        new_ranlist = []
        for i in self.ranklist:
            uid = i.get("uid")
            trend = self.get(uid).get("trend")
            i.update({"trend": trend})
            new_ranlist.append((i))
        self.ranklist = new_ranlist
        d = ujson.dumps(self)
        self.redis_handler.set(self.name, d, self.ex)
        return self


    def _extend_dict(self,d):
        """
        Input:
            a = {
                "1":"hello world",
                "2~5":"range between 2~5",
                "6~7":"range between 6~7"
            }
        Output:
            {
                '1': 'helloworld',
                '3': 'rangebetween2~5',
                '2': 'rangebetween2~5',
                '5': 'rangebetween2~5',
                '4': 'rangebetween2~5',
                '7': 'rangebetween6~7',
                '6': 'rangebetween6~7'
            }
        :param d:
        :return:
        """
        new_d ={}
        for k,v in d.items():
            if '~' in k:
                start, end = k.split('~')
                keys = range(int(start),int(end)+1)
                for i in keys:
                    new_d.update({
                        str(i):v
                    })
            else:
                new_d.update({
                    k:v
                })
        return new_d



    def about_me(self,uid):
        return self.get(uid,{})


    def top(self,care = 10):
        lst =self.ranklist if self.ranklist else self.values()
        return lst[:care]


class RankList(list):
    def __init__(self, name, cache):
        pass

    def __setitem__(self, index, value):
        self.app

    def __lt__(self, *filter):
        pass



if __name__ == '__main__':
    pass
```
# 效果展示
![Image](https://github.com/HQCfly/HotRank/blob/master/imgfolder/1.png)

# 后续迭代更多功能版本
# 添加页面展示，实战真实数据，实时更新