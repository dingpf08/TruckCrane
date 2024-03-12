class VerificationProject:
    """
    验算项目选择类，用于存储用户选择的验算项目类型。
    """
    def __init__(self, project_type: str):
        # 验算项目类型，例如："土方直立壁开挖深度计算" 或 "基坑安全边坡计算"
        self.project_type = project_type


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
        self.cohesion = cohesion
        # 边坡的坡度角θ(°)
        self.slope_angle = slope_angle
#土方边坡计算的数据类型
class SlopeCalculationData:
    """
    土方边坡计算数据类型，整合验算项目选择、坡顶作用荷载、基本土体物理参数。
    """
    def __init__(self, verification_project: VerificationProject, slope_top_load: SlopeTopLoad, basic_parameters: BasicParameters):
        # 验算项目
        self.verification_project = verification_project
        # 坡顶作用荷载
        self.slope_top_load = slope_top_load
        # 基本土体物理参数
        self.basic_parameters = basic_parameters

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
