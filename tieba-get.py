import argparse
import csv
import hashlib
import re
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Iterator, Tuple, Set

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ==================== 常量设置 ====================

BASE_TIEBA = "https://tieba.baidu.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 标题里要出现的关键词（判断是不是装机/配置贴）
TITLE_KEYWORDS = [
    "配置", "装机", "攒机", "主机", "整机", "求配置", "求装机", "配置单"
]

# 正文里出现这些关键词中的若干个，就当作“疑似攒机配置”
CONTENT_KEYWORDS = [
    "CPU", "显卡", "主板", "内存", "固态", "机械硬盘", "硬盘",
    "电源", "机箱", "散热", "风冷", "水冷",
    "i3", "i5", "i7", "i9",
    "Ryzen", "R3", "R5", "R7", "R9",
    "RTX", "GTX", "RX", "ARC",
    "12490F", "13490F", "5800X3D", "5600X", "7500F", "7600",
]

MIN_TEXT_LEN = 15      # 太短的回复去掉
MAX_TEXT_LEN = 2000    # 太长的广告贴 / 水贴可以筛掉


@dataclass
class ConfigPost:
    source: str           # "tieba"
    bar_name: str         # 比如 "电脑吧"
    thread_url: str
    thread_title: str
    floor: int
    author: Optional[str]
    post_time: Optional[str]
    text: str


# ==================== 工具函数 ====================

def get_html(
    session: requests.Session,
    url: str,
    params: Optional[dict] = None,
    retries: int = 3,
    sleep_sec: float = 1.0,
) -> Optional[str]:
    """带简单重试和延时的获取 HTML."""
    for attempt in range(retries):
        try:
            resp = session.get(url, params=params, timeout=10)
            # 403/302 之类一般是风控 / 登录问题，这里直接返回 None
            if resp.status_code != 200:
                return None
            # 贴吧是 utf-8
            resp.encoding = resp.apparent_encoding or "utf-8"
            time.sleep(sleep_sec)
            return resp.text
        except requests.RequestException:
            time.sleep(sleep_sec * (attempt + 1))
    return None


def clean_text(text: str) -> str:
    """简单清洗：去多余空白，保留换行."""
    # 把全角空格等都压成普通空格
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    # 把连续空行压缩
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def looks_like_build_text(text: str) -> bool:
    """粗略判断一段中文文本是不是攒机配置."""
    if not text:
        return False
    if len(text) < MIN_TEXT_LEN or len(text) > MAX_TEXT_LEN:
        return False

    hit = sum(1 for kw in CONTENT_KEYWORDS if kw in text)
    return hit >= 2  # 至少包含两个硬件相关关键词


# ==================== 贴吧相关解析 ====================

def iter_tieba_threads(
    session: requests.Session,
    kw: str,
    max_pages: int,
) -> Iterator[Tuple[str, str]]:
    """
    遍历某个贴吧的帖子列表，返回 (thread_url, title).

    kw: 吧名，比如 "电脑"
    """
    bar_name = kw + "吧"
    for page in range(max_pages):
        params = {"kw": kw, "ie": "utf-8", "pn": page * 50}
        url = f"{BASE_TIEBA}/f"
        html = get_html(session, url, params=params)
        if not html:
            break

        soup = BeautifulSoup(html, "lxml")

        # 常见结构：<a class="j_th_tit " href="/p/xxxx" title="...">标题</a>
        links = soup.select("a.j_th_tit")
        if not links:
            # 兜底：抓所有 /p/ 开头的链接
            links = [
                a for a in soup.find_all("a", href=True)
                if a["href"].startswith("/p/")
            ]

        if not links:
            # 没有帖子了，认为到尾页
            break

        for a in links:
            title = a.get_text(strip=True)
            href = a.get("href")
            if not href:
                continue
            thread_url = href
            if thread_url.startswith("/"):
                thread_url = BASE_TIEBA + thread_url

            # 标题关键词过滤
            if not any(k in title for k in TITLE_KEYWORDS):
                continue

            yield thread_url, title

        # 简单可视化进度
        print(f"[tieba] {bar_name} 列表页 {page} 处理完毕，总帖数≈{len(links)}")


def parse_tieba_thread(
    session: requests.Session,
    thread_url: str,
    thread_title: str,
    bar_name: str,
    max_pages_per_thread: int = 3,
) -> List[ConfigPost]:
    """
    解析单个帖子，抓出疑似攒机配置的楼层文本.
    为了控制体量，每个帖子最多爬前 max_pages_per_thread 页.
    """
    results: List[ConfigPost] = []
    for page in range(1, max_pages_per_thread + 1):
        url = f"{thread_url}?pn={page}"
        html = get_html(session, url)
        if not html:
            break

        soup = BeautifulSoup(html, "lxml")

        # 贴吧帖子一般结构：
        # <div class="d_post_content j_d_post_content " id="post_content_xxx">
        content_divs = soup.find_all(
            "div",
            class_=lambda c: c and "d_post_content" in c
        )
        if not content_divs:
            # 页里没有内容了
            break

        # 作者和时间结构比较杂，很多情况下你未必需要，这里就不强行解析了
        floor_num = 0
        for div in content_divs:
            floor_num += 1
            raw_text = div.get_text(separator="\n", strip=True)
            text = clean_text(raw_text)

            if not looks_like_build_text(text):
                continue

            post = ConfigPost(
                source="tieba",
                bar_name=bar_name,
                thread_url=thread_url,
                thread_title=thread_title,
                floor=floor_num,
                author=None,       # 需要的话可以再写一个解析函数
                post_time=None,    # 同上
                text=text,
            )
            results.append(post)

    return results


def crawl_tieba_configs(
    kw: str,
    target_posts: int,
    max_list_pages: int,
    max_pages_per_thread: int,
) -> List[ConfigPost]:
    """主流程：针对一个贴吧抓配置文本."""
    session = requests.Session()
    session.headers.update(HEADERS)

    bar_name = kw + "吧"
    collected: List[ConfigPost] = []
    seen_hashes: Set[str] = set()

    threads = list(iter_tieba_threads(session, kw, max_list_pages))
    print(f"[tieba] {bar_name} 预计候选帖子：{len(threads)}")

    for thread_url, title in tqdm(threads, desc=f"解析 {bar_name} 帖子"):
        posts = parse_tieba_thread(
            session,
            thread_url=thread_url,
            thread_title=title,
            bar_name=bar_name,
            max_pages_per_thread=max_pages_per_thread,
        )

        for p in posts:
            # 用文本内容做简单去重，以免同贴多页/转贴
            h = hashlib.md5(p.text.encode("utf-8")).hexdigest()
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            collected.append(p)

            if len(collected) >= target_posts:
                return collected

    return collected


# ==================== CLI & 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description="爬取贴吧攒机配置文本（电脑吧等）"
    )
    parser.add_argument(
        "--kw",
        type=str,
        default="电脑",
        help="贴吧名（不带“吧”字），默认：电脑",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=30000,
        help="希望抓取的配置文本数量（上限），默认 30000",
    )
    parser.add_argument(
        "--list-pages",
        type=int,
        default=1000,
        help="最多爬多少个列表页（每页约 50 帖），默认 1000",
    )
    parser.add_argument(
        "--thread-pages",
        type=int,
        default=3,
        help="每个帖子最多解析多少页，默认 3",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="tieba_build_configs.csv",
        help="输出 CSV 文件名",
    )

    args = parser.parse_args()

    bar_name = args.kw + "吧"
    print(
        f"开始抓取 [{bar_name}]，目标≈{args.target} 条攒机配置文本，"
        f"列表页上限={args.list_pages}，帖内页上限={args.thread_pages}"
    )

    posts = crawl_tieba_configs(
        kw=args.kw,
        target_posts=args.target,
        max_list_pages=args.list_pages,
        max_pages_per_thread=args.thread_pages,
    )

    if not posts:
        print("没有抓到任何符合条件的帖子，建议降低过滤条件或先试更少页数。")
        return

    # 写 CSV
    fieldnames = [
        "source",
        "bar_name",
        "thread_url",
        "thread_title",
        "floor",
        "author",
        "post_time",
        "text",
    ]

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in posts:
            writer.writerow(asdict(p))

    print(
        f"完成！共写入 {len(posts)} 条记录到 {args.out}；"
        "后续可以单独写脚本做 CPU/显卡/内存/硬盘的解析。"
    )


if __name__ == "__main__":
    main()
