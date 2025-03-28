from dataclasses import dataclass, field
from typing import Optional
from DataStruDef.CalculateType import ConstructionCalculationType as Conct
from DataStruDef.EngineeringDataBase import EngineeringDataBase

@dataclass
class HydraulicCraneData(EngineeringDataBase):
    """液压汽车起重机吊装计算数据类"""
    conCalType: int = Conct.HYDRAULIC_CRANE_CALCULATION  # 计算类型
    caltypename: str = "液压汽车起重机吊装计算"  # 计算类型名称
    uuid: str = ""  # 唯一标识符
    
    # 基本参数
    crane_weight: float = 30.0  # 吊重Gw(吨)
    power_factor: float = 1.2  # 起重动力系数k1
    is_smart_recommendation: bool = True  # True为智能推荐，False为自定义
    
    # 吊装要求参数
    max_lifting_height: float = 10.0  # 吊物顶面距地面最大吊装高度h1(m)
    min_boom_distance: float = 3.0  # 吊物顶面距起重臂端部的最小距离h2(m)
    working_radius_method: str = "智能确定"  # 工作幅度确定方法
    min_working_radius: float = 4.0  # 场地要求的最小工作幅度(m)
    
    # 吊物与起重臂安全距离复核参数
    edge_distance: float = 1.0  # 构件边缘距起重臂距离(m)
    safety_distance: float = 1.0  # 安装构件边缘距起重臂中心的最小安全距离ε(m)
    
    # 计算结果和状态
    is_calculated: bool = False  # 是否已经计算
    calculation_results: dict = field(default_factory=dict)  # 计算结果
    
    def __str__(self):
        return (f"液压汽车起重机吊装计算 - UUID: {self.uuid}\n"
                f"吊重: {self.crane_weight}吨\n"
                f"起重动力系数: {self.power_factor}\n"
                f"智能推荐: {self.is_smart_recommendation}\n"
                f"最大吊装高度: {self.max_lifting_height}m\n"
                f"最小臂距: {self.min_boom_distance}m\n"
                f"工作幅度方法: {self.working_radius_method}\n"
                f"最小工作幅度: {self.min_working_radius}m\n"
                f"构件边缘距起重臂距离: {self.edge_distance}m\n"
                f"最小安全距离: {self.safety_distance}m") 