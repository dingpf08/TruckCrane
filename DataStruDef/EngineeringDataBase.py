#所有的工程数据类型的基类
from DataStruDef.CalculateType import ConstructionCalculationType as ConCalType

class EngineeringDataBase:
    def __init__(self):
        # Initialize conCalType with a default enum value
        self.conCalType = ConCalType.None_CalculationType

    def set_calculation_type(self, cal_type):
        """设置计算类型"""
        if isinstance(cal_type, ConCalType):
            self.conCalType = cal_type
        else:
            raise ValueError("Invalid calculation type. Must be a ConstructionCalculationType.")

    def get_calculation_type(self):
        """获取计算类型"""
        return self.conCalType

    def validate_data(self):
        """验证数据的有效性"""
        return self.conCalType != ConCalType.None_CalculationType

    def describe(self):
        """返回数据的描述"""
        return f"Engineering Data with Calculation Type: {self.conCalType.name}"



# 示例用法
if __name__ == "__main__":
    data = EngineeringDataBase()
    data.set_calculation_type(ConCalType.SOIL_EMBANKMENT_CALCULATION)
    print(data.describe())
    print("Is data valid?", data.validate_data())
