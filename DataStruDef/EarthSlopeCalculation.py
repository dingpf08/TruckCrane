#土方边坡计算数据结构--
from DataStruDef.CalculateType import ConstructionCalculationType as ConCalType, VerificationProject  # 计算类型
#from CalculateType import ConstructionCalculationType as ConCalType#计算类型  这样子不对 不太理解


class SlopeTopLoad:
    """
    坡顶作用荷载类，用于存储坡顶荷载相关参数。
    """
    def __init__(self, uniform_load: float):
        # 坑顶护道上均布荷载 q(kN/m²)
        self.uniform_load = uniform_load
class BasicParameters:
    """
    基本参数类，用于存储边坡计算所需的基本土体物理参数。
    """
    def __init__(self, soil_type: str, unit_weight: float, internal_friction_angle: float, cohesion: float, slope_angle: float):
        # 坑壁土类型，例如："粘性土", "红粘土","粉土","粉砂","细砂","中砂","粗砂","砂砾" 等
        self.soil_type = soil_type#str
        # 土的重度γ(kN/m³)
        self.unit_weight = unit_weight#double
        # 土的内摩擦角ϕ(°)
        self.internal_friction_angle = internal_friction_angle#double
        # 土粘聚力c(kN/㎡)
        self.cohesion = cohesion#double
        # 边坡的坡度角θ(°)
        self.slope_angle = slope_angle#double
#土方边坡计算的数据类型：新建一个数据类型，要把数据类型默认的名称和类型加到类的初始化函数中
#Note：对于其它数据类型 都要有下面两个变量：self.caltypename（对话框的名字str），self.conCalType（对话框的类型ConCalType）
class SlopeCalculationData:
    """
    土方边坡计算数据类型，整合验算项目选择、坡顶作用荷载、基本土体物理参数。
    """
    def __init__(self, verification_project: VerificationProject, slope_top_load: SlopeTopLoad, basic_parameters: BasicParameters, caltypename="土方边坡计算"):
        # Import EngineeringDataBase locally to avoid circular import
        from DataStruDef.EngineeringDataBase import EngineeringDataBase
        super().__init__()  # Initialize the base class
        self.caltypename = caltypename  # 计算类型文字版
        self.conCalType = ConCalType.SOIL_EMBANKMENT_CALCULATION  # Set the calculation type
        # 验算项目
        self.verification_project = verification_project
        # 坡顶作用荷载
        self.slope_top_load = slope_top_load
        # 基本土体物理参数
        self.basic_parameters = basic_parameters

    # 更新参数
    def update(self, verification_project: VerificationProject, slope_top_load: SlopeTopLoad, basic_parameters: BasicParameters):
        """根据提供的新实例更新计算数据的状态。"""
        self.verification_project = verification_project
        self.slope_top_load = slope_top_load
        self.basic_parameters = basic_parameters
        return self  # 返回实例自身
def main():
    # 使用示例
    # 创建验算项目实例
    verification_project = VerificationProject("基坑安全边坡计算")
    # 创建坡顶作用荷载实例
    slope_top_load = SlopeTopLoad(20.0) # 假设均布荷载为20kN/m²
    # 创建基本参数实例
    basic_parameters = BasicParameters("粘性土", 18.5, 30, 10, 45)

    # 创建土方边坡计算数据实例
    slope_calculation_data = SlopeCalculationData(verification_project, slope_top_load, basic_parameters)

    # 你现在可以通过slope_calculation_data访问所有相关参数和数据
