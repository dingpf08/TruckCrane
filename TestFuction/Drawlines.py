import matplotlib.pyplot as plt

# 软件的年销售数量范围
sales_quantity = range(0, 10001)

# 每年的销售收入和开发成本
revenue_per_year = [3.5 * x for x in sales_quantity]
development_cost = 5

# 计算每年的盈利或亏损
profit_or_loss = [revenue - development_cost for revenue in revenue_per_year]

# 绘制盈亏平衡图
plt.figure(figsize=(10, 6))
plt.plot(sales_quantity, profit_or_loss, color='blue', linewidth=2)
plt.xlabel('年销售数量')
plt.ylabel('盈利或亏损金额（万元）')
plt.title('软件盈亏平衡图')
plt.grid(True)
plt.axhline(0, color='black', linestyle='--')  # 添加横轴参考线，表示盈亏平衡点
plt.show()
