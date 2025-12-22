clc
clear

filename = '玩家配置评分数据出图版.xlsx';

% 用 readtable 读入整个表
T = readtable(filename, 'Sheet', 1);   

totalScore = T.("Total_Score");

% 把非数值（NaN）去掉，防止影响统计
totalScore = totalScore(~isnan(totalScore));


%%
% 2. 画直方图（Y 轴 = 玩家数量）
figure;
numBins = 30;   % 分成多少个柱子，你可以改成 20、40 试

histogram(totalScore, numBins);   % 不设 Normalization，默认就是“数量”

% 3. 标注和美化
xlabel('配置评分', 'FontSize', 20);
ylabel('玩家数量', 'FontSize', 20);
title('玩家配置评分分布（直方图）', 'FontSize', 24);

grid on;
set(gca, 'FontSize', 20);

%% 
%
% 只保留需要的列
year  = T.Year;
score = T.Total_Score;
type  = categorical(T.Type);  % 'Desktop' / 'Laptop'

%% 按 年份 + 设备类型 统计平均值
G = groupsummary(T, {'Year','Type'}, 'mean', 'Total_Score');
% G 里会有列：Year, Type, mean_Total_Score

% 把 Desktop / Laptop 摊成两列，方便画图
Gw = unstack(G, "mean_Total_Score", "Type");
% Gw.Year, Gw.Desktop, Gw.Laptop  三列

% Desktop 这一条线：去掉 Desktop 为 NaN 的年份
idxD = ~isnan(Gw.Desktop);
xD   = Gw.Year(idxD);
yD   = Gw.Desktop(idxD);

% Laptop 这一条线：去掉 Laptop 为 NaN 的年份
idxL = ~isnan(Gw.Laptop);
xL   = Gw.Year(idxL);
yL   = Gw.Laptop(idxL);


%% 画折线图
figure; hold on;
plot(xD, yD, '-o', 'LineWidth', 2, 'MarkerSize', 10);
plot(xL, yL,  '-s', 'LineWidth', 2, 'MarkerSize', 10);
hold off;

xlabel('配置年份','FontSize', 20);
ylabel('平均总配置评分','FontSize', 20);
title('玩家平均总配置评分随年份变化（Desktop vs Laptop）','FontSize', 20);
legend('Desktop','Laptop','Location','northwest', 'FontSize', 24);
grid on;
set(gca, 'FontSize', 20);


