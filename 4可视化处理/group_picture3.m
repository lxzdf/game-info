clc
clear

player = readtable('玩家配置评分数据出图版.xlsx');
game   = readtable('游戏配置数据出图版.xlsx','VariableNamingRule','preserve');

player.Properties.VariableNames
game.Properties.VariableNames

player.Year       = player.Year;      % 比如 F 列
player.TotalScore = player.Total_Score;          % 最后一列

game.Year     = game.Year;
game.Config   = game.('配置');               % '最低' / '推荐'
game.TotalReq = game.('综合性能分');

years = (2020:2025)';  % 你也可以根据实际年份自动算 unique

nY = numel(years);
Tmin      = NaN(nY,1);   % 当年大作最低配置综合分均值
Trec      = NaN(nY,1);   % 当年大作推荐配置综合分均值
PlayerAvg = NaN(nY,1);   % 当年玩家总分均值

for k = 1:nY
    y = years(k);
    
    % 当年大作
    Gy = game(game.Year == y, :);
    if ~isempty(Gy)
        idxMin = strcmp(Gy.Config, '最低');
        idxRec = strcmp(Gy.Config, '推荐');
        
        if any(idxMin)
            Tmin(k) = mean(Gy.TotalReq(idxMin));
        end
        if any(idxRec)
            Trec(k) = mean(Gy.TotalReq(idxRec));
        end
    end
    
    % 当年玩家
    Py = player(player.Year == y, :);
    if ~isempty(Py)
        PlayerAvg(k) = mean(Py.TotalScore);
        % 中位数：
        % PlayerAvg(k) = median(Py.TotalScore);
    end
end

underPct = NaN(nY,1);   % 性能不足（低于 Tmin）
midPct   = NaN(nY,1);   % 基本匹配
overPct  = NaN(nY,1);   % 性能过剩（≥ 1.5 * Trec）

for k = 1:nY
    y = years(k);
    
    % 如果这一年没有游戏门槛数据，跳过
    if isnan(Tmin(k)) || isnan(Trec(k))
        continue;
    end
    
    % 当年玩家
    Py = player(player.Year == y, :);
    if isempty(Py)
        continue;
    end
    
    score = Py.TotalScore;
    
    % 判定三类
    isUnder = score < Tmin(k);
    isOver  = score >= 1.5 * Trec(k);  % ≥ 推荐均值 1.5 倍
    isMid   = ~(isUnder | isOver);
    
    n = numel(score);
    underPct(k) = sum(isUnder) / n;
    overPct(k)  = sum(isOver)  / n;
    midPct(k)   = sum(isMid)   / n;
end


figure('Position',[100 100 900 650], 'Color','w');

% 用 tiledlayout 让上下两张图之间空隙更小
tiledlayout(2,1,'TileSpacing','compact','Padding','compact');

%% ================= 上半图：玩家性能结构 =================
ax1 = nexttile;                      % 上半图的坐标轴
hold(ax1,'on'); grid(ax1,'on'); box(ax1,'on');

% 把三类玩家占比拼成一个矩阵（行：年份，列：三类）
Ystack = [underPct, midPct, overPct] * 100;   % 转换为百分比
valid  = all(isfinite(Ystack), 2);            % 只保留有数据的年份

% 堆叠面积图：行对应年份，列对应三类玩家
h = area(ax1, years(valid), Ystack(valid,:));

% 去掉边框线，看起来更平滑
for i = 1:numel(h)
    h(i).EdgeColor = 'none';
end

% 自定义三种颜色（与下半图的三条线保持同一色系）
h(1).FaceColor = [0.30 0.45 0.85];   % 性能不足：偏冷色（蓝）
h(2).FaceColor = [0.90 0.45 0.20];   % 基本匹配：橙色
h(3).FaceColor = [0.95 0.80 0.25];   % 性能过剩：金色

% 略微透明一点，视觉上不那么压抑
for i = 1:numel(h)
    h(i).FaceAlpha = 0.9;
end

% 轴标签与标题
xlabel(ax1,'年份','FontSize',18);
ylabel(ax1,'玩家占比（%）','FontSize',18);
title(ax1,'各年份玩家性能结构（相对当年大作门槛）','FontSize',20);

% 轴范围和刻度
ylim(ax1,[0 100]);
yticks(ax1,0:20:100);
xlim(ax1,[min(years)-0.5, max(years)+0.5]);

% 图例放在图上方，横向铺开
lg1 = legend(ax1,{'性能不足（低于最低均值）', ...
                  '基本匹配', ...
                  '性能过剩（高于推荐均值 50%）'}, ...
             'Location','northoutside', ...
             'Orientation','horizontal','FontSize',18);
lg1.NumColumns = 3;

% 字体设置（微软雅黑）
set(ax1,'FontName','Microsoft YaHei','FontSize',18);

%% ================= 下半图：大作门槛 & 玩家平均水平 =================
ax2 = nexttile;                      % 下半图的坐标轴
hold(ax2,'on'); grid(ax2,'on'); box(ax2,'on');

% 有任意一条曲线有值的年份才画
valid2 = isfinite(Tmin) | isfinite(Trec) | isfinite(PlayerAvg);

% 三条折线：最低门槛、推荐门槛、玩家平均总分
p1 = plot(ax2, years(valid2), Tmin(valid2), '-o', ...
          'LineWidth',2, 'MarkerSize',8);
p2 = plot(ax2, years(valid2), Trec(valid2), '-s', ...
          'LineWidth',2, 'MarkerSize',8);
p3 = plot(ax2, years(valid2), PlayerAvg(valid2), '-^', ...
          'LineWidth',2, 'MarkerSize',8);

% 三条线颜色：与上半图的三块区域保持色系一致
p1.Color = [0.30 0.45 0.85];   % Tmin
p2.Color = [0.90 0.45 0.20];   % Trec
p3.Color = [0.95 0.80 0.25];   % PlayerAvg

xlabel(ax2,'年份','FontSize',18);
ylabel(ax2,'综合性能分','FontSize',18);
title(ax2,'大作配置门槛与玩家平均配置对比','FontSize',20);

% 图例：只认 p1, p2, p3 三条线，不再自动把 data1 拉进来
lg2 = legend(ax2, [p1 p2 p3], ...
             {'最低配置均值 T_{min}', ...
              '推荐配置均值 T_{rec}', ...
              '玩家平均总分'}, ...
             'Location','northwest','FontSize',16);

xlim(ax2,[min(years)-0.5, max(years)+0.5]);

set(ax2,'FontName','Microsoft YaHei','FontSize',18);
% 和上半图联动缩放 X 轴
linkaxes([ax1, ax2],'x');

