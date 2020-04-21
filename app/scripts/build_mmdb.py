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


def build_geoip_data(d=None):
    if d is None:
        return
    city_name = d
    return {
        "city":
        {
            "names":
            {
                "en": city_name.split('_')[1]
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
            "latitude": 27.829939,
            "longitude": 113.135933,
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
                "iso_code": city_name.split('_')[0],
                "names":
                {
                    "en": city_name.split('_')[0]
                }
            }
        ]
    }


subnet_info = {
    "LiaoLin_ShenYang": [u"10.18.9.0/24"],
    "JiLIn_ChangChun": [u"10.18.10.0/24"],
    "HeiLongJiang_HaErBin": [u"10.18.11.0/24"],
    "NeiMengGu_HuHeHaoTe": [u"10.18.16.0/24"],
    "GuangXi_NanNing": [u"10.18.19.0/24"],
    "GuiZhou_GuiYang": [u"10.18.23.0/24"],
    "HuBei_WuHan": [u"10.18.27.0/24"],
    "AnHui_HeFei": [u"10.18.28.0/24"],
    "HuNan_LouDi": [u"10.18.32.0/24", u"10.18.42.0/24", u"10.18.43.0/24"],
    "GuangDong_ZhongShan": [u"10.18.33.0/24", u"10.18.34.0/24"],
    "ZheJiang_WenZhou": [u"10.18.36.0/24", u"10.18.37.0/24"],
    "GuangXi_GuiLin": [u"10.18.39.0/24", u"10.18.40.0/24"],
    "HuNan_ChangDe": [u"10.18.44.0/24", u"10.18.45.0/24"],
    "HuNan_XiangTan": [u"10.18.47.0/24", u"10.18.48.0/24"],
    "HuNan_ShaoYang": [u"10.18.50.0/24", u"10.18.51.0/24", u"10.18.59.0/24"],
    "HuNan_ChenZhou": [u"10.18.53.0/24", u"10.18.54.0/24"],
    "HuNan_HuaiHua": [u"10.18.56.0/24", u"10.18.57.0/24"],
    "HuNan_HenYang": [u"10.18.60.0/24", u"10.18.61.0/24"],
    "HuNan_YiYang": [u"10.18.63.0/24", u"10.18.64.0/24"],
    "HuNan_YueYang": [u"10.18.66.0/24", u"10.18.67.0/24"],
    "HuNan_ZhuZhou": [u"10.18.69.0/24", u"10.18.70.0/24", u"10.18.88.0/24"],
    "HuNan_YongZhou": [u"10.18.72.0/24", u"10.18.73.0/24"],
    "HuNan_ZhangJiaJie": [u"10.18.75.0/24", u"10.18.76.0/24"],
    "HuNan_JiShou": [u"10.18.78.0/24", u"10.18.79.0/24"],
    "FuJIan_FuZhou": [u"10.18.81.0/24", u"10.18.82.0/24"],
    "JiangXi_NangChang": [u"10.18.84.0/24", u"10.18.85.0/24", u"10.18.86.0/24"],
    "JiangXi_NangChang": [u"10.18.90.0/24", u"10.18.91.0/24", u"10.18.92.0/24"],
    "JiangXi_ShangRao": [u"10.18.93.0/24", u"10.18.94.0/24", u"10.18.95.0/24"],
    "GuangXi_QinZhou": [u"10.18.97.0/24", u"10.18.98.0/24", u"10.18.99.0/24", u"10.18.100.0/24"],
    "JiangXi_JiuJiang": [u"10.18.102.0/24", u"10.18.103.0/24", u"10.18.104.0/24", u"10.18.105.0/24"],
    "GuiZhou_ZunYi": [u"10.18.106.0/24", u"10.18.107.0/24", u"10.18.108.0/24", u"10.18.109.0/24"],
    "GuangXi_NanNing": [u"10.18.111.0/24", u"10.18.112.0/24", u"10.18.113.0/24", u"10.18.114.0/24", u"10.18.115.0/24", u"10.18.116.0/24", u"10.18.117.0/24"],
    "GuangXi_BaiSe": [u"10.18.118.0/24", u"10.18.119.0/24", u"10.18.120.0/24"],

    "ChangSha_RiYe": [u"10.7.0.0/16"],
    "ChangSha_XinYuan": [u"10.12.0.0/16"],
    "ChangSha_GongYuanDao": [u"10.3.0.0/16"],
    "ChangSha_GaoXinQu": [u"10.8.0.0/16"],
    "ChangSha_XinHua": [u"10.13.0.0/16"],
}

for i in subnet_info:
    data = enc.insert_data(build_geoip_data(i))
    for x in subnet_info[i]:
        enc.insert_network(x, data)
    enc.write_file('GeoLite2-City.mmdb')