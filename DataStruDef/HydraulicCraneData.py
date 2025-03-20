from DataStruDef.EngineeringDataBase import EngineeringDataBase
from DataStruDef.CalculateType import ConstructionCalculationType as ConCalType
from DataStruDef.CalculateType import VerificationProject

#汽车吊参数
class HydraulicCraneData(EngineeringDataBase):
    """
    液压汽车起重机数据类型，包含吊装能力、吊臂长度和工作半径。
    """
    def __init__(self, load_capacity=30.0, boom_length=50.0, working_radius=20.0):
        super().__init__()
        self.conCalType = ConCalType.Hoisting_Lifting_CALCULATION_TruckCrane#汽车吊
        self.caltypename = "液压汽车起重机吊装计算"  # 计算类型文字版
        # 添加验证项目
        self.verification_project = VerificationProject("液压汽车起重机吊装计算")
        # 基本参数
        self.load_capacity = load_capacity  # 吊装能力 (吨)
        self.boom_length = boom_length  # 吊臂长度 (米)
        self.working_radius = working_radius  # 工作半径 (米)

    def update(self, load_capacity, boom_length, working_radius):
        """更新起重机数据"""
        self.load_capacity = load_capacity
        self.boom_length = boom_length
        self.working_radius = working_radius
        return self

    def describe(self):
        """返回起重机数据的描述"""
        return (f"Hydraulic Crane Data: Load Capacity = {self.load_capacity} tons, "
                f"Boom Length = {self.boom_length} meters, "
                f"Working Radius = {self.working_radius} meters, "
                f"Verification Project = {self.verification_project.project_type}") 