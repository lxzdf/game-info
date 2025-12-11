import argparse
import concurrent.futures
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ==================== 常量设置 ====================

APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
SEARCH_LIST_URL = "https://store.steampowered.com/search/results/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# 区域：美区；语言：简体中文
# 说明：带简中翻译的游戏会返回中文名；没有简中本地化的游戏会返回英文名
REGION_CC = "us"
LANGUAGE: Optional[str] = "schinese"


@dataclass
class ParsedRequirements:
    cpu: Optional[str]
    gpu: Optional[str]
    ram: Optional[str]
    storage: Optional[str]
    notes: Optional[str]
    raw: Optional[str]   # 仅内部使用，不写入 CSV


# ==================== 获取 app 列表 ====================

def fetch_app_list_via_search(limit: Optional[int]) -> List[Dict]:
    """
    当官方 WebAPI 不可用时，通过商店搜索接口获取一批游戏 appid。
    只会返回类型为游戏（category1=998）的 appid 列表。
    """
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    found: List[int] = []
    start = 0
    page_size = 200
    total_count: Optional[int] = None

    while True:
        params = {
            "query": "",
            "start": start,
            "count": page_size,
            "dynamic_data": "",
            "snr": "1_7_7_230_7",
            "infinite": 1,
            "category1": 998,  # games
            "cc": REGION_CC,
        }
        if LANGUAGE:
            params["l"] = LANGUAGE

        resp = session.get(SEARCH_LIST_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        total_count = total_count or data.get("total_count")
        html = data.get("results_html", "") or ""

        appids = [int(aid) for aid in re.findall(r'data-ds-appid="(\d+)"', html)]
        if not appids:
            break

        found.extend(appids)
        start += page_size

        if limit and len(found) >= limit:
            break
        if total_count and start >= total_count:
            break

    # 去重并转成和 WebAPI 一样的结构
    seen = set()
    deduped = []
    for aid in found:
        if aid in seen:
            continue
        seen.add(aid)
        deduped.append({"appid": aid, "name": None})

    return deduped[:limit] if limit else deduped


def fetch_app_list(limit: Optional[int]) -> List[Dict]:
    """
    优先通过官方 WebAPI 获取 app 列表，失败则回退到搜索接口。
    limit 是“最多扫描多少个 appid”（不是最终行数）。
    """
    try:
        resp = requests.get(
            APP_LIST_URL,
            params={"format": "json"},
            timeout=30,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
        apps = resp.json()["applist"]["apps"]
        print(f"从 WebAPI 获取到 {len(apps)} 个 App。")
        return apps[:limit] if limit else apps
    except Exception as exc:
        print(f"WebAPI 获取 App 列表失败：{exc}")
        print("改用商店搜索接口获取 appid……")
        return fetch_app_list_via_search(limit)


# ==================== 配置解析 ====================

def parse_requirements(html_blob: Optional[str]) -> ParsedRequirements:
    """
    从 pc_requirements 的 HTML 片段中，解析出:
      - cpu / gpu / ram / storage
      - notes: 规整后的附注事项
      - raw: 整段原始配置文本（仅内部使用，不导出）
    """
    if not html_blob:
        return ParsedRequirements(None, None, None, None, None, None)

    soup = BeautifulSoup(html_blob, "html.parser")
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    def match_field(patterns):
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    cpu = match_field([
        r"(?:处理器|processor|cpu)\s*[:：]\s*([^\n]+)",
    ])

    gpu = match_field([
        r"(?:显卡|图形|graphics|video\s*card|gpu)\s*[:：]\s*([^\n]+)",
    ])

    ram = match_field([
        r"(?:内存|memory|ram)\s*[:：]\s*([^\n]+)",
    ])

    storage = match_field([
        r"(?:存储空间|硬盘空间|可用空间"
        r"|storage|hard\s*drive|disk\s*space|hd\s*space|free\s*disk\s*space)"
        r"\s*[:：]?\s*([^\n]+)",
    ])

    notes_content = match_field([
        r"(?:附注事项|附加说明|附加信息)\s*[:：]\s*([^\n]+)",
        r"(?:additional\s+notes?)\s*[:：]\s*([^\n]+)",
    ])

    NOTE_KEYS = [
        "附注事项", "注意", "须知", "说明", "其他要求", "其它要求", "备注",
        "additional", "other requirements", "note",
    ]
    label_variants = [
        "附注事项", "附注事项:", "additional notes", "additional notes:",
    ]

    extra_lines = []
    for line in lines:
        norm = line.replace("：", ":").strip().lower()
        if norm in label_variants:
            continue
        if any(kw.lower() in norm for kw in NOTE_KEYS):
            extra_lines.append(line)

    notes_candidates: List[str] = []
    if notes_content:
        notes_candidates.append(notes_content)
    for line in extra_lines:
        if line not in notes_candidates:
            notes_candidates.append(line)

    if notes_candidates:
        if "附注事项" in text:
            prefix = "附注事项: "
        elif re.search(r"additional\s+notes?", text, re.IGNORECASE):
            prefix = "Additional notes: "
        else:
            prefix = ""
        core = " / ".join(notes_candidates)
        notes = prefix + core
    else:
        notes = None

    return ParsedRequirements(cpu, gpu, ram, storage, notes, text or None)


# ==================== 详情获取 ====================

def fetch_app_details(appid: int) -> Optional[Dict]:
    """
    拉取某一个 app 的详细信息。
    LANGUAGE = "schinese" 时：
      - 有简中本地化：游戏名称是中文；
      - 没有简中本地化：名称是英文。
    """
    params = {"appids": appid, "cc": REGION_CC}
    if LANGUAGE:
        params["l"] = LANGUAGE

    try:
        resp = requests.get(
            APP_DETAILS_URL,
            params=params,
            timeout=30,
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code != 200:
            return None
        data = resp.json().get(str(appid), {})
        if not data.get("success"):
            return None
        return data.get("data")
    except requests.RequestException:
        return None


def should_keep(details: Dict, allowed_publishers: Optional[List[str]]) -> bool:
    """
    如果设定了 allowed_publishers，则只保留发行商在名单里的游戏。
    """
    if not allowed_publishers:
        return True
    pubs = [p.lower() for p in details.get("publishers", [])]
    return any(pub in pubs for pub in allowed_publishers)


# ==================== 主爬取逻辑 ====================

def scrape(
    max_apps: Optional[int],
    concurrency: int,
    delay: float,
    publishers: Optional[List[str]],
) -> pd.DataFrame:
    """
    核心爬取函数：
      - max_apps: 最多扫描多少个 appid（不是最终行数）
      - concurrency: 线程数
      - delay: 每成功收集一条后 sleep 的秒数
      - publishers: 发行商过滤列表（小写）
    """
    apps = fetch_app_list(max_apps)
    print(f"准备扫描 {len(apps)} 个 appid")

    allowed_publishers = [p.strip().lower() for p in publishers] if publishers else None

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_app_details, app["appid"]): app for app in apps}

        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc="Fetching app details",
        ):
            details = future.result()
            if not details:
                continue

            # 只保留类型为“game”的项目
            if details.get("type") != "game":
                continue

            # 只要支持 Windows 平台
            platforms = details.get("platforms") or {}
            if not platforms.get("windows", False):
                continue

            # 有发行商过滤就再筛一层
            if not should_keep(details, allowed_publishers):
                continue

            name = (details.get("name") or "").strip()
            if not name:
                continue

            pc_req = details.get("pc_requirements") or {}
            if not pc_req:
                continue

            min_req = parse_requirements(pc_req.get("minimum"))
            rec_req = parse_requirements(pc_req.get("recommended"))

            # 发行日期（发售时间）
            rel_info = details.get("release_date") or {}
            release_date = rel_info.get("date")

            # 至少要有一点结构化配置信息（最低或推荐）
            if not any(
                [
                    min_req.cpu,
                    min_req.gpu,
                    min_req.ram,
                    min_req.storage,
                    rec_req.cpu,
                    rec_req.gpu,
                    rec_req.ram,
                    rec_req.storage,
                ]
            ):
                continue

            # 推荐配置：如果没有就用 "None" 字符串
            rec_cpu = rec_req.cpu or "None"
            rec_gpu = rec_req.gpu or "None"
            rec_ram = rec_req.ram or "None"
            rec_storage = rec_req.storage or "None"
            rec_notes = rec_req.notes or "None"

            row = {
                "App_ID": details.get("steam_appid"),
                "游戏名称": name,
                "发行日期": release_date,
                "最低CPU": min_req.cpu,
                "最低显卡": min_req.gpu,
                "最低内存": min_req.ram,
                "最低硬盘": min_req.storage,
                "最低配置的注意事项": min_req.notes,
                "推荐CPU": rec_cpu,
                "推荐显卡": rec_gpu,
                "推荐内存": rec_ram,
                "推荐硬盘": rec_storage,
                "推荐配置的注意事项": rec_notes,
            }

            rows.append(row)

            # 轻微限速，防止过于频繁
            if delay > 0:
                time.sleep(delay)

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="从 Steam 抓取游戏配置数据到 CSV。"
    )
    parser.add_argument(
        "--max-apps",
        type=int,
        default=80000,
        help="最多扫描多少个 appid（不是最终行数）。建议略大于你期望的数据条数。",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="steam_game_specs.csv",
        help="输出 CSV 文件路径。",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="并发线程数（越大越快，但太大可能更容易遇到限流/网络错误）。",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="每成功收集一条记录后 sleep 的秒数，用于温和控制请求节奏。",
    )
    parser.add_argument(
        "--publishers",
        type=str,
        default=None,
        help=(
            "按发行商过滤，逗号分隔，例如："
            "'Electronic Arts,Ubisoft,CAPCOM Co., Ltd.'。不填则不过滤。"
        ),
    )

    args = parser.parse_args()
    pubs = args.publishers.split(",") if args.publishers else None

    df = scrape(args.max_apps, args.concurrency, args.delay, pubs)
    df.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"已保存 {len(df)} 条记录到 {args.out}")


if __name__ == "__main__":
    main()
