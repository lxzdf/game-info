
clc
clear
T = readtable('游戏配置数据出图版.xlsx','VariableNamingRule','preserve');  

T.Properties.VariableNames

T.Game       = T.("game");
T.Year       = T.("Year");
T.Config     = T.("配置");
T.TotalScore = T.("综合性能分");

% 假设列名：Game, Year, Config, TotalScore
games = unique(T.game, 'stable');
n = numel(games);

minScore = nan(n,1);
recScore = nan(n,1);
year     = nan(n,1);

for i = 1:n
    idx = strcmp(T.game, games{i});
    Ti  = T(idx, :);

    % 年份（如果一款游戏多行，就取众数或第一行）
    year(i) = mode(Ti.Year);

    % 最低配置
    im = strcmp(Ti.Config, "最低");
    if any(im)
        minScore(i) = Ti.TotalScore(im);
    end

    % 推荐配置
    ir = strcmp(Ti.Config, "推荐");
    if any(ir)
        recScore(i) = Ti.TotalScore(ir);
    end
end

% 删掉缺少数据的游戏
valid = ~isnan(minScore) & ~isnan(recScore);
games    = games(valid);
minScore = minScore(valid);
recScore = recScore(valid);
year     = year(valid);
n        = numel(games);


% 按推荐配置分数排序（从低到高）
[recScore, order] = sort(recScore);
minScore = minScore(order);
games    = games(order);
year     = year(order);


y = 1:n;   % y 轴位置

%% 作图：水平哑铃图
figure('Position',[100 100 900 600]);
hold on; box on; grid on;

% 连线：每款游戏一条水平线，HandleVisibility 设为 off，这样不会进图例
for i = 1:n
    plot([minScore(i), recScore(i)], [y(i), y(i)], '-', ...
        'LineWidth', 2, ...
        'Color', [0.8 0.8 0.8], ...        % 淡灰色
        'HandleVisibility','off');         % 不参与图例
end

% 最低配置点
hMin = scatter(minScore, y, 50, 'filled', ...
    'MarkerFaceAlpha', 0.9);

% 推荐配置点
hRec = scatter(recScore, y, 50, 'filled', ...
    'MarkerFaceAlpha', 0.9);

hLine = plot([0 1],[0 0], '-', ...
    'LineWidth', 2, ...
    'Color', [0.8 0.8 0.8]);    % 这条线只给图例看


set(gca,'YTick', y, 'YTickLabel', games, 'YDir','reverse', ...
        'FontSize', 20);        % 坐标轴整体字号
xlabel('综合性能分','FontSize',20);
ylabel('游戏名','FontSize',20);
title('2020–2025 年典型大作的最低 / 推荐配置对比','FontSize',24);

legend([hLine, hMin, hRec], ...
       {'最低–推荐连线', '最低配置', '推荐配置'}, ...
       'Location','best', ...
       'FontSize',20);

% 如果游戏太多，可只画某一年或 Top 20
xlim([min(minScore)*0.9, max(recScore)*1.05]);