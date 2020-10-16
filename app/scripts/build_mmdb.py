#!coding=utf-8
import mmdbencoder

# first install lib
# pip install py-mmdb-encoder

enc = mmdbencoder.Encoder(
    6,  # IP version
    32,  # Size of the pointers
    'GeoLite2-City',  # Name of the table
    ['en'],  # Languages
    {'en': 'GeoLite2-City'},  # Description
    compat=True)  # Map IPv4 in IPv6 (::abcd instead of ::ffff:abcd) to be read by official libraries


def build_geoip_data(prov, city, lat, lon):
    return {
        "city":
            {
                "names":
                    {
                        "en": city
                    }
            }, "continent":
            {
                "code": "AS",
                "names":
                    {
                        "en":
                            "AS"
                    }
            }, "country":
            {
                "iso_code": "CN",
                "names":
                    {
                        "en": "China"
                    }
            }, "location":
            {
                "accuracy_radius": 2,
                "latitude": lat,
                "longitude": lon,
                "metro_code": 623,
                "time_zone": "Asia/Shanghai"
            }, "registered_country":
            {
                "iso_code": "CN",
                "names":
                    {
                        "en": "China"
                    }
            }, "subdivisions":
            [
                {
                    "iso_code": prov,
                    "names":
                        {
                            "en": prov
                        }
                }
            ]
    }


subnet_info = {
    # locatoin:[lat,lon]
    "LiaoLin_ShenYang": {"location": [22.765297, 108.37512], "subnet": [u"10.18.9.0/24"]},
    "JiLIn_ChangChun": {"location": [43.888988, 125.272324], "subnet": [u"10.18.10.0/24"]},
    "HeiLongJiang_HaErBin": {"location": [45.699308, 126.57951], "subnet": [u"10.18.11.0/24"]},
    "NeiMengGu_HuHeHaoTe": {"location": [40.802448, 111.665459], "subnet": [u"10.18.16.0/24"]},
    "GuangXi_NanNing": {"location": [22.83862, 108.26534], "subnet": [u"10.18.19.0/24"]},
    "GuiZhou_GuiYang": {"location": [26.618567, 106.64389], "subnet": [u"10.18.23.0/24"]},
    "HuBei_WuHan": {"location": [30.574642, 114.234604], "subnet": [u"10.18.27.0/24"]},
    "AnHui_HeFei": {"location": [31.69886, 117.301392], "subnet": [u"10.18.28.0/24"]},
    "HuNan_LouDi": {"location": [27.722832, 112.010887],
                    "subnet": [u"10.18.32.0/24", u"10.18.42.0/24", u"10.18.43.0/24"]},
    "GuangDong_ZhongShan": {"location": [22.550711, 113.486252], "subnet": [u"10.18.33.0/24", u"10.18.34.0/24"]},
    "ZheJiang_WenZhou": {"location": [27.995062, 120.64473], "subnet": [u"10.18.36.0/24", u"10.18.37.0/24"]},
    "GuangXi_GuiLin": {"location": [22.764811, 108.374641], "subnet": [u"10.18.39.0/24", u"10.18.40.0/24"]},
    "HuNan_ChangDe": {"location": [29.070553, 111.679428], "subnet": [u"10.18.44.0/24", u"10.18.45.0/24"]},
    "HuNan_XiangTan": {"location": [27.84845, 112.94212], "subnet": [u"10.18.47.0/24", u"10.18.48.0/24"]},
    "HuNan_ShaoYang": {"location": [27.220922, 111.487312],
                       "subnet": [u"10.18.50.0/24", u"10.18.51.0/24", u"10.18.59.0/24"]},
    "HuNan_ChenZhou": {"location": [25.771509, 113.013237], "subnet": [u"10.18.53.0/24", u"10.18.54.0/24"]},
    "HuNan_HuaiHua": {"location": [27.550316, 109.989731], "subnet": [u"10.18.56.0/24", u"10.18.57.0/24"]},
    "HuNan_HenYang": {"location": [26.884029, 112.586838], "subnet": [u"10.18.60.0/24", u"10.18.61.0/24"]},
    "HuNan_YiYang": {"location": [28.570358, 112.359192], "subnet": [u"10.18.63.0/24", u"10.18.64.0/24"]},
    "HuNan_YueYang": {"location": [29.371059, 113.132072], "subnet": [u"10.18.66.0/24", u"10.18.67.0/24"]},
    "HuNan_ZhuZhou": {"location": [27.82991, 113.136238],
                      "subnet": [u"10.18.69.0/24", u"10.18.70.0/24", u"10.18.88.0/24"]},
    "HuNan_YongZhou": {"location": [26.431479, 111.603447], "subnet": [u"10.18.72.0/24", u"10.18.73.0/24"]},
    "HuNan_ZhangJiaJie": {"location": [29.12562, 110.48288], "subnet": [u"10.18.75.0/24", u"10.18.76.0/24"]},
    "HuNan_JiShou": {"location": [28.31058, 109.74235], "subnet": [u"10.18.78.0/24", u"10.18.79.0/24"]},
    "FuJIan_FuZhou": {"location": [26.040831, 119.216599], "subnet": [u"10.18.81.0/24", u"10.18.82.0/24"]},
    "JiangXi_NangChang": {"location": [28.67353, 116.01792],
                          "subnet": [u"10.18.84.0/24", u"10.18.85.0/24", u"10.18.86.0/24", u"10.18.90.0/24",
                                     u"10.18.91.0/24", u"10.18.92.0/24"]},
    "JiangXi_ShangRao": {"location": [28.4489, 117.941582],
                         "subnet": [u"10.18.93.0/24", u"10.18.94.0/24", u"10.18.95.0/24"]},
    "GuangXi_QinZhou": {"location": [21.974316, 108.652796],
                        "subnet": [u"10.18.97.0/24", u"10.18.98.0/24", u"10.18.99.0/24", u"10.18.100.0/24"]},
    "JiangXi_JiuJiang": {"location": [29.703915, 115.951546],
                         "subnet": [u"10.18.102.0/24", u"10.18.103.0/24", u"10.18.104.0/24", u"10.18.105.0/24"]},
    "GuiZhou_ZunYi": {"location": [27.707447, 106.947838],
                      "subnet": [u"10.18.106.0/24", u"10.18.107.0/24", u"10.18.108.0/24", u"10.18.109.0/24"]},
    "GuangXi_NanNing": {"location": [22.83862, 108.26534],
                        "subnet": [u"10.18.111.0/24", u"10.18.112.0/24", u"10.18.113.0/24", u"10.18.114.0/24",
                                   u"10.18.115.0/24", u"10.18.116.0/24", u"10.18.117.0/24"]},
    "GuangXi_BaiSe": {"location": [23.894192, 106.642067],
                      "subnet": [u"10.18.118.0/24", u"10.18.119.0/24", u"10.18.120.0/24"]},

    "ChangSha_RiYe": {"location": [28.230532271214845, 112.87702284506223], "subnet": [u"10.7.0.0/16"]},
    "ChangSha_XinYuan": {"location": [28.11167940578311, 112.97546528032682], "subnet": [u"10.12.0.0/16"]},
    "ChangSha_GongYuanDao": {"location": [28.20428846938874, 112.92981944731137], "subnet": [u"10.3.0.0/16"]},
    "ChangSha_GaoXinQu": {"location": [28.2306362, 112.87539206], "subnet": [u"10.8.0.0/16"]},
    "ChangSha_XinHua": {"location": [27.717415, 111.318359], "subnet": [u"10.13.0.0/16"]},
}

for i in subnet_info:
    prov = i.split('_')[0]
    city = i.split('_')[1]
    lat = subnet_info[i]['location'][0]
    lon = subnet_info[i]['location'][1]
    data = enc.insert_data(build_geoip_data(prov, city, lat, lon))
    for x in subnet_info[i]['subnet']:
        enc.insert_network(x, data)
    enc.write_file('GeoLite2-City.mmdb')
