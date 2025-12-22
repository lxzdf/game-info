clc
clear

player = readtable('玩家配置评分数据出图版.xlsx');
game   = readtable('游戏配置数据出图版.xlsx','VariableNamingRule','preserve');

pv = player.Properties.VariableNames;



player.Year     = player.Year;
player.CPUScore  = player.CPU_Score;               % '最低' / '推荐'
player.GPUScore  = player.GPU_Score;    
player.TotalScore  = player.Total_Score;  


game.Year = game.Year;
game.Config = game.('配置');
game.CPUReq = game.('CPU评分');
game.GPUReq = game.('显卡评分');

player.CoreScore = 0.4*player.CPUScore + 0.6*player.GPUScore;

%% ================= 3. 构造分位档位（横轴：玩家 CPU+GPU 档位） =================
% 为了图更清爽，用 5 档：低配 / 偏低 / 中配 / 偏高 / 高配
K = 5;

allCore = player.CoreScore;

% 0, 0.2, 0.4, ..., 1 的分位点
edges = quantile(allCore, linspace(0,1,K+1));


% 为横轴准备档位标签，例如：P00–P20, P20–P40, ...
binLabels = strings(1,K);
for b = 1:K
    lowP  = (b-1)*100/K;
    highP = b*100/K;
    binLabels(b) = sprintf('P%02.0f–P%02.0f', lowP, highP);
end


%% ================= 4. 年份轴（纵轴：大作发行年份） =================
years = (min(game.Year):max(game.Year))';   % 例如 2020:2025
nY    = numel(years);

% 结果矩阵：行 = 年份，列 = 档位；值 = 满足CPU+GPU推荐配置的比例（0~1）
PlayMat = nan(nY, K);

%% ================= 5. 逐年 & 逐档位计算“CPU+GPU 满足推荐配置”的比例 =================
for iy = 1:nY
    Y = years(iy);

    % 当年的所有推荐配置大作
    G = game(game.Year == Y & strcmp(game.Config,'推荐'), :);
    if isempty(G)
        continue;   % 没有游戏就跳过
    end

    % 截止到该年为止已经购机的玩家
    P = player(player.Year <= Y, :);
    if isempty(P)
        continue;
    end

    for b = 1:K
        % 当前档位的核心算力分区间
        lo = edges(b);
        hi = edges(b+1);

        % 最后一档包括右端点
        if b < K
            idxP = (P.CoreScore >= lo) & (P.CoreScore < hi);
        else
            idxP = (P.CoreScore >= lo) & (P.CoreScore <= hi);
        end

        Pb = P(idxP, :);     % 这一档位的玩家
        if isempty(Pb)
            continue;
        end

        nP = height(Pb);
        nG = height(G);

        % ok(p,g)：该档位第 p 个玩家，对第 g 个游戏，CPU&GPU 是否同时 ≥ 推荐
        ok = false(nP, nG);
        for j = 1:nG
            ok(:,j) = (Pb.CPUScore >= G.CPUReq(j)) & ...
                      (Pb.GPUScore >= G.GPUReq(j));
        end

        % 这一年、这一档位的“匹配推荐配置”比例（只看 CPU+GPU）
        PlayMat(iy, b) = mean(ok(:));   % 0~1
    end
end

%% 图1：CPU+GPU 热力图
figure('Position',[200 200 820 480],'Color','w');

h = heatmap(binLabels, years, PlayMat * 100);  % 转成百分比显示

% 文本内容
h.XLabel = '玩家核心算力分位档位（按 0.4·CPU + 0.6·GPU 划分）';
h.YLabel = '年份（大作发行年份）';
h.Title  = '不同档位玩家在当年大作中满足 CPU+GPU 推荐配置的比例';

% 统一字体和字号（标题、坐标轴、格子里的百分比都会跟着变）
h.FontName = 'Microsoft YaHei';
h.FontSize = 18;

% 颜色与数值显示设置
h.ColorLimits      = [0 100];         % 颜色映射 0–100%
h.CellLabelFormat  = '%.0f%%';        % 每格显示百分比
h.MissingDataLabel = '';
h.MissingDataColor = [0.9 0.9 0.9];   % 没数据的格子用浅灰

colormap(parula);


%% ================= 7. 图2：CPU / GPU 分布对比（玩家 vs 推荐配置） =================
% 取所有玩家的 CPU/GPU 得分
cpu_player = player.CPUScore;
gpu_player = player.GPUScore;

% 取所有大作“推荐配置”的 CPU/GPU 要求
cpu_game = game.CPUReq(strcmp(game.Config,'推荐'));
gpu_game = game.GPUReq(strcmp(game.Config,'推荐'));

% 去掉 NaN
cpu_player = cpu_player(isfinite(cpu_player));
gpu_player = gpu_player(isfinite(gpu_player));
cpu_game   = cpu_game(isfinite(cpu_game));
gpu_game   = gpu_game(isfinite(gpu_game));

figure('Position',[200 200 900 400],'Color','w');
tiledlayout(1,2,'TileSpacing','compact','Padding','compact');

% ---- 左图：CPU 分布对比 ----
ax1 = nexttile;
hold(ax1,'on'); grid(ax1,'on'); box(ax1,'on');

% 玩家 CPU 分布
h1 = histogram(ax1, cpu_player, 'Normalization','probability', ...
               'FaceAlpha',0.5, 'EdgeColor','none');
% 游戏推荐 CPU 分布
h2 = histogram(ax1, cpu_game,   'Normalization','probability', ...
               'FaceAlpha',0.6, 'EdgeColor','none');

h1.FaceColor = [0.30 0.45 0.85];
h2.FaceColor = [0.90 0.45 0.20];

xlabel(ax1,'CPU 得分');
ylabel(ax1,'概率');
title(ax1,'玩家 vs 大作推荐配置：CPU 分布对比');

lg1 = legend(ax1,{'玩家 CPU 得分','大作推荐 CPU 要求'}, ...
             'Location','northeast');

set(ax1,'FontName','Microsoft YaHei','FontSize',11);

% ---- 右图：GPU 分布对比 ----
ax2 = nexttile;
hold(ax2,'on'); grid(ax2,'on'); box(ax2,'on');

% 玩家 GPU 分布
h3 = histogram(ax2, gpu_player, 'Normalization','probability', ...
               'FaceAlpha',0.5, 'EdgeColor','none');
% 游戏推荐 GPU 分布
h4 = histogram(ax2, gpu_game,   'Normalization','probability', ...
               'FaceAlpha',0.6, 'EdgeColor','none');

h3.FaceColor = [0.30 0.45 0.85];
h4.FaceColor = [0.90 0.45 0.20];

xlabel(ax2,'GPU 得分');
ylabel(ax2,'概率');
title(ax2,'玩家 vs 大作推荐配置：GPU 分布对比');

lg2 = legend(ax2,{'玩家 GPU 得分','大作推荐 GPU 要求'}, ...
             'Location','northeast');

set(ax2,'FontName','Microsoft YaHei','FontSize',11);

% 统一调整字体（坐标轴 + 图例）
set(findall(gcf,'Type','axes'),   ...
    'FontName','Microsoft YaHei','FontSize',11);
set(findall(gcf,'Type','legend'), ...
    'FontName','Microsoft YaHei','FontSize',10);