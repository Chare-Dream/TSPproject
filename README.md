# TSPproject
项目目标：提出一个解决方案，为圣诞老人提供一条最佳路线，将10万份礼物送到世界各地。在处理这个问题时，我们开发了两种算法--随机搜索和模拟退火，其中模拟退火分别使用一个(within-route)或两个邻居方法(within-route & between-route)进行测试。

本项目将讨论每种算法的结果以及达到最优解的步骤。

评价方法：
<img width="598" alt="image" src="https://user-images.githubusercontent.com/79248301/159371483-01862450-452f-40d7-8064-2f5c99bc0ddd.png">

算法优化内容：
1. 最佳路径评价算法优化：设置两个numpy array，包含各地点的坐标数据，在第一个numpy array中在每趟旅程的初始处插入北极点坐标数据，在第二个numpy array中在每趟旅程的末尾处插入北极点坐标数据，两个array相减后得到相邻两点的经纬度差，从而通过距离计算函数一次性得到每两个相邻点之间的haversine distance，避免每次计算相邻两点距离时都需要循环一次，提升运行速度；

2. 模拟退火模型优化：使用两种邻居算法(within-route & between-route)，将退火速度设置为0.98。
<img width="864" alt="image" src="https://user-images.githubusercontent.com/79248301/159372940-ef13660c-4d76-4ee3-b1da-f3ad6ff4b8f1.png">
<img width="1075" alt="image" src="https://user-images.githubusercontent.com/79248301/159372869-eb35f562-874c-4d70-a199-0c97414b83b0.png">

项目结果：
1. 最佳路径评价算法优化后速度提升25倍， 优化的模拟退火模型较随机算法模型平均值下降92%。 （样本数：1,000， 运行次数： 100,000， 随机种子数：30）
2. 使用优化后的模拟退火模型，计算10万个样本的最佳路径，运行次数56000次，WRW值为28,027,030,000。
