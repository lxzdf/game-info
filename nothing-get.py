import csv
import random
from collections import namedtuple

Config = namedtuple('Config', ['id', 'cpu', 'gpu', 'ram', 'storage', 'year', 'device_type'])

# CPU层级定义
TIER_BUDGET = 'budget'
TIER_MAINSTREAM = 'mainstream'
TIER_HIGH_END = 'high_end'
TIER_ENTHUSIAST = 'enthusiast'

# CPU数据库 - 按发布年份精确组织

# CPU数据库 - 按发布年份和层级组织（扩展版）
CPU_DATABASE = {
    2018: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-8100', 10),
                ('Intel Core i3-8350K', 8),
                # 新增：同代常见型号
                ('Intel Core i3-8300', 9),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-8400', 15),
                ('Intel Core i5-8600K', 12),
                ('Intel Core i7-8700', 10),
                # 新增：同为 8 代主流游戏 U
                ('Intel Core i5-8500', 12),
                ('Intel Core i5-8600', 10),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-8700K', 14),   # 调高一点，毕竟 2018 真·热销高端
                ('Intel Core i9-9900K', 10),   # 2018 Q4 发布的旗舰
                # 新增：限量纪念版
                ('Intel Core i7-8086K', 8),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 3 2200G', 10),
                ('AMD Ryzen 3 2300X', 8),
                # 新增：同年 APU
                ('AMD Ryzen 5 2400G', 6),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 2600', 15),
                ('AMD Ryzen 5 2600X', 12),
                ('AMD Ryzen 7 2700', 10),
            ],
            TIER_HIGH_END: [
                # 2800X 从未真实发布，这里只放真实型号
                ('AMD Ryzen 7 2700X', 14),
                ('AMD Ryzen 7 2700', 10),
            ],
        },
    },

    2019: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-9100', 10),
                ('Intel Core i3-9350K', 8),
                # 新增：最常见的带 F 型号
                ('Intel Core i3-9100F', 12),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-9400', 14),
                ('Intel Core i5-9600K', 12),
                ('Intel Core i7-9700', 10),
                # 新增：销量更高的 9400F
                ('Intel Core i5-9400F', 18),
                ('Intel Core i5-9500', 12),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-9700K', 12),
                ('Intel Core i9-9900K', 14),
                ('Intel Core i9-9900KS', 8),
                # 新增：同代 KF 版本
                ('Intel Core i9-9900KF', 8),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 3 3200G', 10),
                ('AMD Ryzen 5 3400G', 8),
                # 旧款 APU 依然在 2019 年大量出货
                ('AMD Ryzen 3 2200G', 6),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 3600', 18),   # 2019 年全球范围非常畅销
                ('AMD Ryzen 5 3600X', 14),
                ('AMD Ryzen 7 3700X', 12),
                # 新增：非 X 版
                ('AMD Ryzen 7 3700', 10),
                ('AMD Ryzen 7 3800X', 10),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 7 3800X', 10),
                ('AMD Ryzen 9 3900X', 14),
                ('AMD Ryzen 9 3950X', 8),
                # 新增：OEM 版 3900
                ('AMD Ryzen 9 3900', 6),
            ],
        },
    },

    2020: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-10100', 12),
                ('Intel Core i3-10300', 10),
                # 新增：极高性价比的 F 型号
                ('Intel Core i3-10100F', 14),
                ('Intel Core i3-10105F', 10),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-10400', 16),
                ('Intel Core i5-10600K', 14),
                ('Intel Core i7-10700', 12),
                # 新增：10400F 在电商上非常常见
                ('Intel Core i5-10400F', 18),
                ('Intel Core i5-10600KF', 12),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-10700K', 14),
                ('Intel Core i9-10900K', 16),
                ('Intel Core i9-10850K', 8),
                # 新增：KF 版本
                ('Intel Core i9-10900KF', 10),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 3 3100', 10),
                ('AMD Ryzen 5 3500X', 12),
                # 新增：一度非常抢手的 3300X
                ('AMD Ryzen 3 3300X', 8),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 5600X', 18),
                ('AMD Ryzen 7 5800X', 16),
                ('AMD Ryzen 7 3700X', 12),
                # 新增：Zen2 热销型号延续到 2020
                ('AMD Ryzen 5 3600', 16),
                ('AMD Ryzen 5 3600X', 14),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 9 5900X', 15),
                ('AMD Ryzen 9 5950X', 10),
                # 新增：上一代 3900X 仍有不少装机量
                ('AMD Ryzen 9 3900X', 12),
            ],
        },
    },

    2021: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-10105', 10),
                ('Intel Core i5-11400', 14),
                # 新增：11400F / 10100F 是 2021 年很常见的入门选择
                ('Intel Core i5-11400F', 16),
                ('Intel Core i3-10100F', 12),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-11400', 16),
                ('Intel Core i5-11600K', 14),
                ('Intel Core i7-11700', 12),
                # 新增：11500 / 11600KF
                ('Intel Core i5-11500', 14),
                ('Intel Core i5-11600KF', 14),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-11700K', 14),
                ('Intel Core i9-11900K', 10),
                # 新增：11900KF
                ('Intel Core i9-11900KF', 10),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 5 5600G', 12),
                ('AMD Ryzen 5 5500', 10),
                # 新增：8 核 APU
                ('AMD Ryzen 7 5700G', 10),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 5600X', 18),
                ('AMD Ryzen 7 5700X', 14),
                ('AMD Ryzen 7 5800X', 16),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 9 5900X', 15),
                ('AMD Ryzen 9 5950X', 12),
            ],
        },
    },

    2022: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-12100', 14),
                ('Intel Core i5-12400', 16),
                # 新增：12100F、12400F 都是公认超高性价比
                ('Intel Core i3-12100F', 16),
                ('Intel Core i5-12400F', 20),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-12400', 18),
                ('Intel Core i5-12600K', 16),
                ('Intel Core i7-12700', 14),
                ('Intel Core i5-12400F', 20),
                ('Intel Core i5-12500', 16),
                ('Intel Core i5-12600KF', 16),
                ('Intel Core i7-12700F', 14),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-12700K', 16),
                ('Intel Core i9-12900K', 12),
                ('Intel Core i9-12900KS', 8),
                # 新增：12900KF
                ('Intel Core i9-12900KF', 10),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 5 5600', 14),
                ('AMD Ryzen 5 5600X', 12),
                # 新增：廉价 U：5500 / 4600G / 4100
                ('AMD Ryzen 5 5500', 12),
                ('AMD Ryzen 5 4600G', 8),
                ('AMD Ryzen 3 4100', 8),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 5700X', 14),
                ('AMD Ryzen 7 5800X', 16),
                ('AMD Ryzen 7 5800X3D', 18),
                # 新增：5700G 也常被当作主流装机选择
                ('AMD Ryzen 7 5700G', 12),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 9 5900X', 14),
                ('AMD Ryzen 9 5950X', 12),
            ],
        },
    },

    2023: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-13100', 12),
                ('Intel Core i5-13400', 16),
                # 新增 F 系列
                ('Intel Core i3-13100F', 14),
                ('Intel Core i5-13400F', 18),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-13400', 18),
                ('Intel Core i5-13600K', 16),
                ('Intel Core i7-13700', 14),
                ('Intel Core i5-13500', 16),
                ('Intel Core i5-13600KF', 16),
                ('Intel Core i7-13700F', 14),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-13700K', 16),
                ('Intel Core i9-13900K', 14),
                ('Intel Core i9-13900KS', 10),
                ('Intel Core i9-13900KF', 12),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 5 7500F', 12),
                ('AMD Ryzen 5 5600', 14),
                # 新增：老 AM4 平台性价比 U
                ('AMD Ryzen 5 5500', 10),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 7600', 18),
                ('AMD Ryzen 5 7600X', 16),
                ('AMD Ryzen 7 7700', 16),
                ('AMD Ryzen 7 7700X', 14),
                # 新增：非 X 的 Ryzen 9 主流玩家也在用
                ('AMD Ryzen 9 7900', 12),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 7 7800X3D', 20),
                ('AMD Ryzen 9 7900X', 14),
                ('AMD Ryzen 9 7950X', 12),
                # 新增：2023 发布的 X3D 高端型号
                ('AMD Ryzen 9 7900X3D', 18),
                ('AMD Ryzen 9 7950X3D', 16),
            ],
        },
    },

    2024: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-14100', 12),
                ('Intel Core i5-14400', 16),
                # 新增：F 系列
                ('Intel Core i3-14100F', 14),
                ('Intel Core i5-14400F', 18),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-14400', 18),
                ('Intel Core i5-14600K', 16),
                ('Intel Core i7-14700', 16),
                ('Intel Core i5-14500', 16),
                ('Intel Core i5-14600KF', 16),
                ('Intel Core i7-14700F', 16),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-14700K', 18),
                ('Intel Core i9-14900K', 16),
                ('Intel Core i9-14900KS', 12),
                ('Intel Core i9-14900KF', 14),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 5 7500F', 12),
                ('AMD Ryzen 5 7600', 14),
                # 新增：2024 年电商排行榜上依然很常见的 AM4 U
                ('AMD Ryzen 5 5600X', 12),
                ('AMD Ryzen 5 5500', 10),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 7600', 16),
                ('AMD Ryzen 5 7600X', 14),
                ('AMD Ryzen 7 7700', 18),
                ('AMD Ryzen 7 7700X', 16),
                # 新增：2024 年发布的 AM4 X3D
                ('AMD Ryzen 7 5700X3D', 14),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 7 7800X3D', 22),
                ('AMD Ryzen 9 7900X', 16),
                ('AMD Ryzen 9 7950X', 14),
                ('AMD Ryzen 7 9800X3D', 18),
                # 新增：Zen5 Ryzen 9
                ('AMD Ryzen 9 9900X', 12),
                ('AMD Ryzen 9 9950X', 10),
            ],
        },
    },

    2025: {
        'Intel': {
            TIER_BUDGET: [
                ('Intel Core i3-14100', 12),
                ('Intel Core i5-14400', 18),
                ('Intel Core i3-14100F', 14),
                ('Intel Core i5-14400F', 20),
            ],
            TIER_MAINSTREAM: [
                ('Intel Core i5-14400', 20),
                ('Intel Core i5-14600K', 18),
                ('Intel Core i7-14700', 18),
                ('Intel Core i5-14600KF', 18),
                ('Intel Core i7-14700F', 18),
            ],
            TIER_HIGH_END: [
                ('Intel Core i7-14700K', 20),
                ('Intel Core i9-14900K', 18),
                ('Intel Core i9-14900KS', 14),
                ('Intel Core i9-14900KF', 16),
                # 新增：与 9800X3D、9950X3D 对位的 Arrow Lake 旗舰
                ('Intel Core Ultra 9 285K', 16),
            ],
        },
        'AMD': {
            TIER_BUDGET: [
                ('AMD Ryzen 5 7600', 14),
                ('AMD Ryzen 5 8500G', 12),
                # 新增：2025 新出的 AM4 X3D 预算 U
                ('AMD Ryzen 5 5500X3D', 12),
                ('AMD Ryzen 5 7500F', 12),
            ],
            TIER_MAINSTREAM: [
                ('AMD Ryzen 5 7600', 18),
                ('AMD Ryzen 5 7600X', 16),
                ('AMD Ryzen 7 7700', 20),
                ('AMD Ryzen 7 7700X', 18),
            ],
            TIER_HIGH_END: [
                ('AMD Ryzen 7 7800X3D', 24),
                ('AMD Ryzen 9 7900X', 18),
                ('AMD Ryzen 9 7950X', 16),
                ('AMD Ryzen 7 9800X3D', 22),
                # 新增：2025 年发布的 X3D 旗舰
                ('AMD Ryzen 9 9900X3D', 20),
                ('AMD Ryzen 9 9950X3D', 18),
            ],
        },
    },
}


# GPU 数据库 - 参考 Steam 调查、电商销量、矿潮 & AI 影响（2018–2025）
GPU_DATABASE = {
    2018: {
        TIER_BUDGET: [
            ('NVIDIA GeForce GTX 1050', 14),
            ('NVIDIA GeForce GTX 1050 Ti', 20),
            ('NVIDIA GeForce GT 1030', 8),
            ('AMD Radeon RX 560', 7),
            ('AMD Radeon RX 570 4GB', 10),
            ('AMD Radeon RX 550', 6),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce GTX 1060 3GB', 22),
            ('NVIDIA GeForce GTX 1060 6GB', 28),   # Steam 最热门卡之一
            ('NVIDIA GeForce GTX 970', 10),
            ('AMD Radeon RX 580 4GB', 12),
            ('AMD Radeon RX 580 8GB', 16),
            ('AMD Radeon RX 570 8GB', 12),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce GTX 1070', 18),
            ('NVIDIA GeForce GTX 1070 Ti', 14),
            ('NVIDIA GeForce GTX 1080', 18),
            ('AMD Radeon RX Vega 56', 10),
            ('AMD Radeon RX Vega 64', 12),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce GTX 1080 Ti', 18),
            ('NVIDIA GeForce RTX 2080', 10),       # 2018 年底刚上市, 占比较低
            ('NVIDIA GeForce RTX 2080 Ti', 8),
            ('NVIDIA Titan Xp', 4),
            ('NVIDIA Titan V', 3),
        ],
    },

    2019: {
        TIER_BUDGET: [
            ('NVIDIA GeForce GTX 1650', 22),
            ('NVIDIA GeForce GTX 1050 Ti', 16),
            ('AMD Radeon RX 570', 13),
            ('AMD Radeon RX 580', 12),
            ('NVIDIA GeForce GT 1030', 6),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce GTX 1660', 18),
            ('NVIDIA GeForce GTX 1660 Ti', 18),
            ('NVIDIA GeForce GTX 1660 SUPER', 22),
            ('NVIDIA GeForce GTX 1060 6GB', 14),
            ('AMD Radeon RX 590', 12),
            ('AMD Radeon RX 5500 XT', 8),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce RTX 2060', 22),
            ('NVIDIA GeForce RTX 2060 SUPER', 18),
            ('NVIDIA GeForce RTX 2070', 18),
            ('AMD Radeon RX 5700', 12),
            ('AMD Radeon RX 5700 XT', 14),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 2080', 16),
            ('NVIDIA GeForce RTX 2080 SUPER', 14),
            ('NVIDIA GeForce RTX 2080 Ti', 18),
            ('AMD Radeon VII', 8),
        ],
    },

    2020: {
        TIER_BUDGET: [
            ('NVIDIA GeForce GTX 1650', 24),
            ('NVIDIA GeForce GTX 1650 SUPER', 20),
            ('NVIDIA GeForce GTX 1050 Ti', 10),
            ('AMD Radeon RX 5500 XT 4GB', 12),
            ('AMD Radeon RX 5500 XT 8GB', 10),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce GTX 1660 SUPER', 26),
            ('NVIDIA GeForce GTX 1660 Ti', 18),
            ('NVIDIA GeForce RTX 2060', 22),
            ('NVIDIA GeForce GTX 1660', 14),
            ('AMD Radeon RX 5600 XT', 16),
            ('AMD Radeon RX 5700', 14),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce RTX 2070 SUPER', 20),
            ('NVIDIA GeForce RTX 2060 SUPER', 16),
            ('NVIDIA GeForce RTX 3060 Ti', 22),  # 2020 年底首发
            ('NVIDIA GeForce RTX 3070', 24),
            ('AMD Radeon RX 5700 XT', 16),
            ('NVIDIA GeForce RTX 2080 SUPER', 10),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 3080', 26),
            ('NVIDIA GeForce RTX 3090', 18),
            ('NVIDIA GeForce RTX 2080 Ti', 12),
            ('AMD Radeon RX 6800', 8),
            ('AMD Radeon RX 6800 XT', 10),
            ('AMD Radeon RX 6900 XT', 8),
        ],
    },

    2021: {  # 矿潮高峰期，高端卡大量去挖矿
        TIER_BUDGET: [
            ('NVIDIA GeForce GTX 1650', 28),
            ('NVIDIA GeForce GTX 1050 Ti', 20),
            ('AMD Radeon RX 570', 16),
            ('AMD Radeon RX 580', 14),
            ('NVIDIA GeForce GTX 1060 3GB', 12),
            ('AMD Radeon RX 560', 8),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce GTX 1660 SUPER', 26),
            ('NVIDIA GeForce GTX 1660 Ti', 20),
            ('NVIDIA GeForce GTX 1660', 18),
            ('NVIDIA GeForce GTX 1650 SUPER', 16),
            ('AMD Radeon RX 5600 XT', 14),
            ('NVIDIA GeForce RTX 2060', 18),
        ],
        TIER_HIGH_END: [  # 能买到 30 系列的人相对少
            ('NVIDIA GeForce RTX 3060', 20),
            ('NVIDIA GeForce RTX 3060 Ti', 14),
            ('AMD Radeon RX 6600', 16),
            ('AMD Radeon RX 6600 XT', 14),
            ('NVIDIA GeForce RTX 2070 SUPER', 12),
            ('NVIDIA GeForce RTX 2070', 10),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 3070', 8),
            ('NVIDIA GeForce RTX 3070 Ti', 6),
            ('NVIDIA GeForce RTX 3080', 5),
            ('NVIDIA GeForce RTX 3080 Ti', 4),
            ('NVIDIA GeForce RTX 3090', 4),
            ('AMD Radeon RX 6700 XT', 6),
            ('AMD Radeon RX 6800', 4),
        ],
    },

    2022: {  # 矿潮尾声，30 系列和新一代高端逐步恢复
        TIER_BUDGET: [
            ('NVIDIA GeForce GTX 1650', 24),
            ('NVIDIA GeForce RTX 3050', 26),   # 2022 年初首发
            ('AMD Radeon RX 6500 XT', 16),
            ('NVIDIA GeForce GTX 1660 SUPER', 18),
            ('NVIDIA GeForce GTX 1630', 10),   # 2022 年 6 月的超入门卡
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce RTX 3060', 32),
            ('NVIDIA GeForce RTX 2060', 18),
            ('AMD Radeon RX 6600', 22),
            ('AMD Radeon RX 6600 XT', 18),
            ('AMD Radeon RX 6650 XT', 16),
            ('NVIDIA GeForce GTX 1660 Ti', 14),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce RTX 3060 Ti', 24),
            ('NVIDIA GeForce RTX 3070', 26),
            ('NVIDIA GeForce RTX 3070 Ti', 22),
            ('AMD Radeon RX 6700 XT', 18),
            ('AMD Radeon RX 6750 XT', 16),
            ('NVIDIA GeForce RTX 3080', 16),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 3080 Ti', 14),
            ('NVIDIA GeForce RTX 3090', 12),
            ('NVIDIA GeForce RTX 3090 Ti', 8),
            ('NVIDIA GeForce RTX 4090', 6),    # 2022 年 10 月首发
            ('NVIDIA GeForce RTX 4080', 6),
            ('AMD Radeon RX 6800 XT', 12),
            ('AMD Radeon RX 6900 XT', 10),
        ],
    },

    2023: {
        TIER_BUDGET: [
            ('NVIDIA GeForce RTX 3050', 24),
            ('NVIDIA GeForce GTX 1650', 18),
            ('AMD Radeon RX 6500 XT', 14),
            ('NVIDIA GeForce GTX 1660 SUPER', 12),
            ('AMD Radeon RX 6600', 16),
            ('Intel Arc A580', 10),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce RTX 3060', 32),   # Steam 上占比长期第一梯队
            ('NVIDIA GeForce RTX 4060', 28),
            ('AMD Radeon RX 6600', 18),
            ('AMD Radeon RX 7600', 24),
            ('AMD Radeon RX 6650 XT', 14),
            ('Intel Arc A750', 8),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce RTX 3070', 22),
            ('NVIDIA GeForce RTX 4060 Ti', 24),
            ('NVIDIA GeForce RTX 4070', 28),
            ('AMD Radeon RX 6700 XT', 16),
            ('AMD Radeon RX 7700 XT', 20),
            ('AMD Radeon RX 7800 XT', 18),
            ('NVIDIA GeForce RTX 3060 Ti', 16),
            ('AMD Radeon RX 7900 GRE', 12),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 4070 Ti', 22),
            ('NVIDIA GeForce RTX 4080', 20),
            ('NVIDIA GeForce RTX 4090', 24),   # 同时也是民用 AI 训练主力
            ('AMD Radeon RX 7900 XT', 18),
            ('AMD Radeon RX 7900 XTX', 20),
            ('NVIDIA GeForce RTX 3080', 12),
        ],
    },

    2024: {  # Ada Super 系列 & Intel Arc B 系列登场
        TIER_BUDGET: [
            ('NVIDIA GeForce RTX 3050', 22),
            ('NVIDIA GeForce GTX 1650', 16),
            ('AMD Radeon RX 6600', 18),
            ('Intel Arc A580', 12),
            ('AMD Radeon RX 6500 XT', 10),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce RTX 3060', 28),
            ('NVIDIA GeForce RTX 4060', 32),
            ('AMD Radeon RX 7600', 24),
            ('AMD Radeon RX 7600 XT', 20),
            ('Intel Arc A750', 10),
            ('AMD Radeon RX 7700 XT', 14),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce RTX 4060 Ti', 26),
            ('NVIDIA GeForce RTX 4070', 30),
            ('NVIDIA GeForce RTX 4070 SUPER', 28),
            ('AMD Radeon RX 7800 XT', 24),
            ('AMD Radeon RX 7900 GRE', 18),
            ('NVIDIA GeForce RTX 3070', 14),
            ('Intel Arc B580', 8),             # 2024 年底发布的 Battlemage
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 4070 Ti', 18),
            ('NVIDIA GeForce RTX 4070 Ti SUPER', 20),
            ('NVIDIA GeForce RTX 4080', 18),
            ('NVIDIA GeForce RTX 4080 SUPER', 22),
            ('NVIDIA GeForce RTX 4090', 26),
            ('AMD Radeon RX 7900 XT', 16),
            ('AMD Radeon RX 7900 XTX', 20),
        ],
    },

    2025: {  # RTX 50 系列 + RX 9000 系列 + Arc B570/B580 + 5090D
        TIER_BUDGET: [
            ('NVIDIA GeForce RTX 3050', 22),
            ('NVIDIA GeForce GTX 1650', 14),
            ('AMD Radeon RX 6600', 18),
            ('NVIDIA GeForce RTX 5050', 18),       # RTX 50 入门卡
            ('AMD Radeon RX 7600', 20),
            ('Intel Arc B570', 12),
        ],
        TIER_MAINSTREAM: [
            ('NVIDIA GeForce RTX 3060', 26),
            ('NVIDIA GeForce RTX 4060', 30),
            ('NVIDIA GeForce RTX 5060', 28),
            ('NVIDIA GeForce RTX 5060 Ti 16GB', 20),
            ('AMD Radeon RX 7600 XT', 18),
            ('AMD Radeon RX 9060 XT', 18),         # RDNA4 中端甜点卡
            ('Intel Arc B580', 14),
        ],
        TIER_HIGH_END: [
            ('NVIDIA GeForce RTX 4070', 22),
            ('NVIDIA GeForce RTX 4070 SUPER', 24),
            ('NVIDIA GeForce RTX 5070', 28),
            ('NVIDIA GeForce RTX 5070 Ti', 24),
            ('AMD Radeon RX 7800 XT', 20),
            ('AMD Radeon RX 7900 GRE', 10),        # 已停产, 但二手/库存仍有
            ('AMD Radeon RX 9070', 16),
            ('AMD Radeon RX 9070 XT', 14),
        ],
        TIER_ENTHUSIAST: [
            ('NVIDIA GeForce RTX 4080 SUPER', 18),
            ('NVIDIA GeForce RTX 5080', 24),
            ('NVIDIA GeForce RTX 5090', 28),       # 黑威龙旗舰, AI+游戏顶级
            ('NVIDIA GeForce RTX 5090D', 16),      # 中国阉割 AI 版
            ('AMD Radeon RX 7900 XT', 14),
            ('AMD Radeon RX 7900 XTX', 18),
            ('NVIDIA GeForce RTX 4090', 20),
        ],
    },
}



def get_cpu_brand_ratio(year):
    """
    根据年份返回 (Intel, AMD) 近似占比（面向 Steam 玩家群体的经验值）。
    数据大致拟合自 Steam Hardware Survey 2018–2025 的 CPU Vendor 走势。
    """
    ratios = {
        2018: (90, 10),  # 实测大约 91/9，取整简化
        2019: (86, 14),  # Ryzen 发力但整体仍偏低
        2020: (76, 24),  # 2020 年 7 月 AMD ≈ 23.7%
        2021: (70, 30),  # 2021 年 5 月首次破 30%
        2022: (68, 32),  # 小幅上涨
        2023: (64, 36),  # AM4/AM5 平台口碑发酵
        2024: (61, 39),  # 接近 40% 区间
        2025: (56, 44),  # 11 月约 43.56%，取整到 44
    }
    # 默认值给个中性值
    return ratios.get(year, (60, 40))



def get_ram_options(year, device_type):
    """
    根据年份和设备类型返回内存选项。
    - 数据大致参照 Steam Hardware Survey 2018–2025 的 RAM 分布趋势，
      再结合 DDR5 市场渗透率报告做了平滑近似。
    - weight 代表相对占比（百分比近似），每一年的权重和为 100。
    """

    if device_type == 'Desktop':
        # 桌面：以 Steam PC 玩家为主
        if year <= 2019:
            # 2018-2019：8GB 仍是主流，16GB 快速增长，32GB/64GB 很少
            return [
                ('8GB DDR4', 52),
                ('16GB DDR4', 38),
                ('32GB DDR4', 8),
                ('64GB DDR4', 2),
            ]
        elif year == 2020:
            # 2020：16GB 开始略微超过 8GB
            return [
                ('8GB DDR4', 35),
                ('16GB DDR4', 48),
                ('32GB DDR4', 14),
                ('64GB DDR4', 3),
            ]
        elif year == 2021:
            # 2021：16GB 已经是明显主流，32GB 增长；DDR5 刚发布，占比可以忽略
            return [
                ('8GB DDR4', 28),
                ('16GB DDR4', 50),
                ('32GB DDR4', 18),
                ('64GB DDR4', 4),
            ]
        elif year == 2022:
            # 2022：开始出现少量 DDR5，高端玩家小规模采用
            return [
                ('8GB DDR4', 25),

                ('16GB DDR4', 36),
                ('16GB DDR5', 9),

                ('32GB DDR4', 20),
                ('32GB DDR5', 5),

                ('64GB DDR4', 4),
                ('64GB DDR5', 1),
            ]
        elif year == 2023:
            # 2023：16GB 继续是主流，32GB 明显增长，DDR5 渗透到约 30% 左右
            return [
                ('8GB DDR4', 22),

                ('16GB DDR4', 38),
                ('16GB DDR5', 12),

                ('32GB DDR4', 9),
                ('32GB DDR5', 14),

                ('64GB DDR4', 1),
                ('64GB DDR5', 4),
            ]
        elif year == 2024:
            # 2024：16GB ~ 32GB 两极，32GB 增长很快，DDR5 ~ 50%
            return [
                ('8GB DDR4', 13),
                ('8GB DDR5', 3),

                ('16GB DDR4', 28),
                ('16GB DDR5', 17),

                ('32GB DDR4', 7),
                ('32GB DDR5', 25),

                ('64GB DDR4', 2),
                ('64GB DDR5', 5),
            ]
        else:  # 2025 及以后
            # 2025：16GB 仍略多于 32GB，但 32GB 已经非常接近；
            # DDR5 在新装机和高端玩家中基本成为主流
            return [
                ('8GB DDR4', 10),
                ('8GB DDR5', 2),

                ('16GB DDR4', 22),
                ('16GB DDR5', 20),

                ('32GB DDR4', 1),
                ('32GB DDR5', 35),

                ('64GB DDR4', 2),
                ('64GB DDR5', 8),
            ]

    else:
        # Laptop：笔记本整体会比台式机更保守一些，8GB 持续时间更长
        if year <= 2019:
            # 2018-2019：大量 4GB/8GB 入门本，16GB 偏少
            return [
                ('4GB DDR4', 25),
                ('8GB DDR4', 60),
                ('16GB DDR4', 15),
            ]
        elif year == 2020:
            # 2020：4GB 逐步减少，16GB 慢慢变多，32GB 极少
            return [
                ('4GB DDR4', 15),
                ('8GB DDR4', 60),
                ('16GB DDR4', 23),
                ('32GB DDR4', 2),
            ]
        elif year == 2021:
            # 2021：8GB 仍主力，但 16GB 已经很常见
            return [
                ('4GB DDR4', 8),
                ('8GB DDR4', 55),
                ('16GB DDR4', 32),
                ('32GB DDR4', 5),
            ]
        elif year == 2022:
            # 2022：开始出现 DDR5/LPDDR5 笔记本，但整体仍以 DDR4 为主
            return [
                ('4GB DDR4', 5),

                ('8GB DDR4', 43),
                ('8GB DDR5', 2),

                ('16GB DDR4', 29),
                ('16GB DDR5', 11),

                ('32GB DDR4', 8),
                ('32GB DDR5', 2),
            ]
        elif year == 2023:
            # 2023：8GB 逐渐不够用，16GB 成为主流，32GB/64GB 在高端本上出现
            return [
                ('4GB DDR4', 3),

                ('8GB DDR4', 35),
                ('8GB DDR5', 3),

                ('16GB DDR4', 29),
                ('16GB DDR5', 15),

                ('32GB DDR4', 6),
                ('32GB DDR5', 6),

                ('64GB DDR4', 2),
                ('64GB DDR5', 1),
            ]
        elif year == 2024:
            # 2024：新款本普遍 16GB 起步（Apple 全系 16GB 起），32GB 在高端/创作本上变多
            return [
                ('8GB DDR4', 25),
                ('8GB DDR5', 5),

                ('16GB DDR4', 27),
                ('16GB DDR5', 18),

                ('32GB DDR4', 3),
                ('32GB DDR5', 17),

                # 64GB 几乎都是 DDR5 工作站 / 高端移动工作站
                ('64GB DDR5', 5),
            ]
        else:  # 2025 及以后
            # 2025：买 8GB 本已经被大量媒体认为是“错误选择”，16GB 成默认，
            # 32GB 在游戏/AI/专业本里越来越常见
            return [
                ('8GB DDR4', 15),
                ('8GB DDR5', 5),

                ('16GB DDR4', 23),
                ('16GB DDR5', 22),

                ('32GB DDR4', 1),
                ('32GB DDR5', 26),

                ('64GB DDR4', 1),
                ('64GB DDR5', 7),
            ]



def get_storage_options(year, device_type):
    """
    根据年份和设备类型返回存储选项（近似真实分布）
    - 参考：Steam Hardware Survey 的硬盘容量分布 + 各年 SSD/HDD 市场趋势。
    - weight 约等于该配置在该年份玩家中的占比（总和为 100）。
    """

    if device_type == 'Desktop':
        # 桌面机：以 PC 玩家/装机市场为主
        if year <= 2019:
            # 2018-2019：SSD 已经普及，但很多人仍有/只用 HDD
            return [
                ('256GB SATA SSD', 25),          # 入门整机/早期升级
                ('512GB SATA SSD', 30),          # 主流
                ('1TB HDD', 25),                 # 纯机械老机器
                ('256GB SSD + 1TB HDD', 20),     # 系统 SSD + 存储 HDD
            ]
        elif year == 2020:
            # 2020：NVMe 开始大规模普及，但 HDD 仍然常见
            return [
                ('512GB NVMe SSD', 32),
                ('1TB NVMe SSD', 28),
                ('512GB SSD + 1TB HDD', 20),
                ('2TB HDD', 20),
            ]
        elif year == 2021:
            # 2021：1TB NVMe 成为主流，2TB NVMe 开始出现
            return [
                ('512GB NVMe SSD', 30),
                ('1TB NVMe SSD', 40),
                ('2TB NVMe SSD', 15),
                ('1TB NVMe SSD + 2TB HDD', 15),
            ]
        elif year == 2022:
            # 2022：总容量持续上升，2TB NVMe 比例增加，机械盘偏存量
            return [
                ('512GB NVMe SSD', 22),
                ('1TB NVMe SSD', 45),
                ('2TB NVMe SSD', 25),
                ('1TB NVMe SSD + 2TB HDD', 8),
            ]
        elif year == 2023:
            # 2023：1TB+ 已经是绝对主流，2TB 在玩家中非常常见
            return [
                ('512GB NVMe SSD', 16),
                ('1TB NVMe SSD', 46),
                ('2TB NVMe SSD', 30),
                ('4TB NVMe SSD', 8),
            ]
        else:  # 2024-2025
            # 2024-2025：参考 Steam：总空间 >1TB 超过一半，
            # 新装机/高端玩家倾向 2TB 起步，4TB 也开始变多:contentReference[oaicite:4]{index=4}
            return [
                ('512GB NVMe SSD', 10),   # 主要是老机器或极低价整机
                ('1TB NVMe SSD', 40),
                ('2TB NVMe SSD', 35),
                ('4TB NVMe SSD', 15),
            ]

    else:
        # Laptop：笔记本整体更“保守”，低容量拖后腿时间更长
        if year <= 2019:
            # 2018-2019：办公本/轻薄本以 256/512 SATA 为主，1TB HDD 边缘
            return [
                ('256GB SATA SSD', 40),
                ('512GB SATA SSD', 45),
                ('1TB HDD', 15),
            ]
        elif year == 2020:
            # 2020：主流新本切换到 NVMe，256/512 仍占多
            return [
                ('256GB NVMe SSD', 30),
                ('512GB NVMe SSD', 55),
                ('1TB NVMe SSD', 15),
            ]
        elif year == 2021:
            # 2021：512GB 仍主力，1TB 在中高端本上增多
            return [
                ('512GB NVMe SSD', 48),
                ('1TB NVMe SSD', 42),
                ('2TB NVMe SSD', 10),
            ]
        elif year == 2022:
            # 2022：高性能本/游戏本普遍 512-1TB，2TB 仍然少数:contentReference[oaicite:5]{index=5}
            return [
                ('512GB NVMe SSD', 40),
                ('1TB NVMe SSD', 48),
                ('2TB NVMe SSD', 12),
            ]
        elif year == 2023:
            # 2023：不少游戏本开始标配 1TB，512 仍大量存在
            return [
                ('512GB NVMe SSD', 35),
                ('1TB NVMe SSD', 52),
                ('2TB NVMe SSD', 13),
            ]
        else:  # 2024-2025
            # 2024-2025：媒体普遍建议游戏本“至少 1TB”，
            # 但实际市场仍有不少 512GB，2TB 是高端/工作站段:contentReference[oaicite:6]{index=6}
            return [
                ('512GB NVMe SSD', 30),
                ('1TB NVMe SSD', 55),
                ('2TB NVMe SSD', 15),
            ]



def weighted_choice(choices):
    """根据权重随机选择"""
    items, weights = zip(*choices)
    return random.choices(items, weights=weights, k=1)[0]


def get_gpu_tier_for_cpu_tier(cpu_tier, is_gamer):
    """
    根据 CPU 层级和是否为玩家，返回 GPU 层级。
    设计原则：
    - 玩家：GPU 一般不低于 CPU，大量出现“GPU 高一档”，少量“GPU 高两档甚至三档”。
    - 非玩家：CPU 和 GPU 更脱钩，常见的是 CPU 够用 + 入门/核显，少数是工作站/AI 场景堆高端 GPU。
    """

    if is_gamer:
        # 玩家：优先保证 GPU 不拖后腿
        if cpu_tier == TIER_BUDGET:
            # 预算 CPU：多数配主流/中高端显卡（“卡好一点就行”）
            choices = [TIER_BUDGET, TIER_MAINSTREAM, TIER_HIGH_END, TIER_ENTHUSIAST]
            weights = [10, 50, 30, 10]
            # 约 90% 情况 GPU >= MAINSTREAM，40% 情况 GPU >= HIGH_END

        elif cpu_tier == TIER_MAINSTREAM:
            # 主流 CPU：大部分配主流/高端显卡，少量“节省显卡”或“直接堆顶卡”
            choices = [TIER_BUDGET, TIER_MAINSTREAM, TIER_HIGH_END, TIER_ENTHUSIAST]
            weights = [5, 40, 35, 20]
            # 约 95% 情况 GPU >= MAINSTREAM，55% 情况 GPU >= HIGH_END

        elif cpu_tier == TIER_HIGH_END:
            # 高端 CPU（含 7800X3D, 9800X3D 等）：通常配高端或发烧级显卡
            choices = [TIER_MAINSTREAM, TIER_HIGH_END, TIER_ENTHUSIAST]
            weights = [10, 40, 50]
            # 约 90% 情况 GPU >= HIGH_END，50% 直接发烧级

        else:
            # 不认识的层级，降级为主流
            return TIER_MAINSTREAM

    else:
        # 非玩家：更多“核显 / 入门卡 + 还不错的 CPU”
        if cpu_tier == TIER_BUDGET:
            # 办公/入门主机：基本都是核显/入门独显
            choices = [TIER_BUDGET, TIER_MAINSTREAM]
            weights = [90, 10]

        elif cpu_tier == TIER_MAINSTREAM:
            # 中端 CPU：大量是办公/轻生产力，显卡要求不高；少量设计/渲染类会配中高端 GPU
            choices = [TIER_BUDGET, TIER_MAINSTREAM, TIER_HIGH_END]
            weights = [60, 35, 5]

        elif cpu_tier == TIER_HIGH_END:
            # 高端 CPU 非玩家：一部分是“堆 CPU 的程序员/科研/编译”，
            # 一部分是真·工作站/AI 推理机，配高端/发烧显卡。
            choices = [TIER_MAINSTREAM, TIER_HIGH_END, TIER_ENTHUSIAST]
            weights = [35, 45, 20]

        else:
            return TIER_MAINSTREAM

    return random.choices(choices, weights=weights, k=1)[0]


def generate_config(config_id, is_gamer):
    """生成单个配置"""
    year_weights = {
        2018: 4, 2019: 6, 2020: 10, 2021: 13,
        2022: 18, 2023: 20, 2024: 32, 2025: 27
    }
    year = weighted_choice(list(year_weights.items()))

    device_type = weighted_choice([('Desktop', 75 if is_gamer else 48),
                                   ('Laptop', 25 if is_gamer else 52)])

    intel_ratio, amd_ratio = get_cpu_brand_ratio(year)
    cpu_brand = weighted_choice([('Intel', intel_ratio), ('AMD', amd_ratio)])

    if is_gamer:
        cpu_tier = weighted_choice([(TIER_BUDGET, 8), (TIER_MAINSTREAM, 72), (TIER_HIGH_END, 20)])
    else:
        cpu_tier = weighted_choice([(TIER_BUDGET, 38), (TIER_MAINSTREAM, 54), (TIER_HIGH_END, 8)])

    cpu_options = CPU_DATABASE[year][cpu_brand][cpu_tier]
    cpu = weighted_choice(cpu_options)

    gpu_tier = get_gpu_tier_for_cpu_tier(cpu_tier, is_gamer)

    # GPU可以用当年或前一年的型号
    gpu_year = year if random.random() < 0.75 else max(2018, year - 1)
    gpu_options = GPU_DATABASE[gpu_year][gpu_tier]
    gpu = weighted_choice(gpu_options)

    ram = weighted_choice(get_ram_options(year, device_type))
    storage = weighted_choice(get_storage_options(year, device_type))

    return Config(config_id, cpu, gpu, ram, storage, year, device_type)


def generate_configs(total_count=50000, gamer_ratio=0.70):
    """生成配置列表"""
    configs = []
    gamer_count = int(total_count * gamer_ratio)

    print(f"开始生成 {total_count} 条配置数据...")
    print(f"游戏玩家配置: {gamer_count} 条 ({gamer_ratio * 100:.0f}%)")
    print(f"普通用户配置: {total_count - gamer_count} 条 ({(1 - gamer_ratio) * 100:.0f}%)\n")

    for i in range(gamer_count):
        configs.append(generate_config(i + 1, is_gamer=True))
        if (i + 1) % 10000 == 0:
            print(f"已生成游戏玩家配置: {i + 1}/{gamer_count}")

    for i in range(total_count - gamer_count):
        configs.append(generate_config(gamer_count + i + 1, is_gamer=False))
        if (i + 1) % 5000 == 0:
            print(f"已生成普通用户配置: {i + 1}/{total_count - gamer_count}")

    random.shuffle(configs)
    configs = [Config(i + 1, c.cpu, c.gpu, c.ram, c.storage, c.year, c.device_type)
               for i, c in enumerate(configs)]

    return configs


def save_to_csv(configs, filename='player_pc_configs.csv'):
    """保存到CSV文件"""
    print(f"\n正在保存到 {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'CPU', 'GPU', 'RAM', 'Storage', 'Year', 'Type'])
        for config in configs:
            writer.writerow(config)
    print(f"✓ 成功保存 {len(configs)} 条配置到 {filename}")


def print_statistics(configs):
    """打印统计信息"""
    from collections import Counter

    print("\n" + "=" * 75)
    print("配置统计信息")
    print("=" * 75)

    year_counter = Counter(c.year for c in configs)
    print(f"\n年份分布:")
    for year in sorted(year_counter.keys()):
        count = year_counter[year]
        print(f"  {year}: {count:6d} ({count / len(configs) * 100:5.2f}%)")

    device_counter = Counter(c.device_type for c in configs)
    print(f"\n设备类型:")
    for dtype, count in device_counter.items():
        print(f"  {dtype}: {count:6d} ({count / len(configs) * 100:5.2f}%)")

    print(f"\nCPU品牌分布(按年份):")
    for year in sorted(year_counter.keys()):
        year_configs = [c for c in configs if c.year == year]
        intel = sum(1 for c in year_configs if 'Intel' in c.cpu)
        amd = sum(1 for c in year_configs if 'AMD' in c.cpu)
        print(f"  {year}: Intel {intel / len(year_configs) * 100:5.2f}%  AMD {amd / len(year_configs) * 100:5.2f}%")

    nvidia_count = sum(1 for c in configs if 'NVIDIA' in c.gpu)
    amd_gpu_count = sum(1 for c in configs if 'AMD' in c.gpu)
    intel_gpu_count = sum(1 for c in configs if 'Intel' in c.gpu)
    print(f"\nGPU品牌总体分布:")
    print(f"  NVIDIA: {nvidia_count:6d} ({nvidia_count / len(configs) * 100:5.2f}%)")
    print(f"  AMD:    {amd_gpu_count:6d} ({amd_gpu_count / len(configs) * 100:5.2f}%)")
    print(f"  Intel:  {intel_gpu_count:6d} ({intel_gpu_count / len(configs) * 100:5.2f}%)")

    gpu_counter = Counter(c.gpu for c in configs)
    print(f"\nGPU型号TOP 10:")
    for gpu, count in gpu_counter.most_common(10):
        print(f"  {gpu}: {count:6d} ({count / len(configs) * 100:5.2f}%)")

    ram_counter = Counter(c.ram for c in configs)
    print(f"\n内存配置TOP 5:")
    for ram, count in ram_counter.most_common(5):
        print(f"  {ram}: {count:6d} ({count / len(configs) * 100:5.2f}%)")

    print("\n" + "=" * 75)


def main():
    random.seed(42)
    configs = generate_configs(total_count=50000, gamer_ratio=0.70)
    save_to_csv(configs)
    print_statistics(configs)

    print("\n配置示例（前10条）:")
    print("-" * 115)
    print(f"{'ID':<6} {'CPU':<32} {'GPU':<40} {'RAM':<16} {'Storage':<22} {'Year':<6} {'Type':<10}")
    print("-" * 115)
    for config in configs[:10]:
        print(
            f"{config.id:<6} {config.cpu:<32} {config.gpu:<40} {config.ram:<16} {config.storage:<22} {config.year:<6} {config.device_type:<10}")


if __name__ == "__main__":
    main()