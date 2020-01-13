#! code=utf-8

from yaml import load, dump


a={
    'data':[{
        'username':None,
        'password':'p',
        'hosts':['a','b']
    },{
        'username':'u',
        'password':'p',
        'hosts':['a','b']
    }
    ]
}

print(dump(a))
