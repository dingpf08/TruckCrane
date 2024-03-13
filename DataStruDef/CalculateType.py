from enum import Enum
#添加施工软件的计算类型，所有计算类型用同一个枚举值
class ConstructionCalculationType(Enum):
    SOIL_EMBANKMENT_CALCULATION = 1  # 土方边坡计算
    # 可以继续添加其他施工软件计算类型

def main():
    for calc_type in ConstructionCalculationType:
        print(calc_type)

if __name__ == '__main__':
    main()