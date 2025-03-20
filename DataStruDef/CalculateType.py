from enum import Enum
#添加施工软件的计算类型，所有计算类型用同一个枚举值
class ConstructionCalculationType(Enum):
    #region 1 地基基础计算
    SOIL_EMBANKMENT_CALCULATION = 1  # 土方边坡计算
    # endregion 1
    #region 6吊装计算
    Hoisting_Lifting_CALCULATION_TruckCrane=6 #汽车吊装计算
    Hoisting_Lifting_CALCULATION_CrawlerCrane = 7  # 履带吊装计算
    None_CalculationType=100#默认为空
    # endregion吊装计算
    # 可以继续添加其他施工软件计算类型
class VerificationProject:
    """
    验算项目选择类，用于存储用户选择的验算项目类型。
    """
    def __init__(self, project_type: str):
        # 验算项目类型，例如："土方直立壁开挖深度计算" 或 "基坑安全边坡计算"
        self.project_type = project_type
def main():
    for calc_type in ConstructionCalculationType:
        print(calc_type)

if __name__ == '__main__':
    main()