# Opus の作戦メモと出典（gpt-6.1-sol には渡していない）

## 立場
米9月CPIを受けても、FRBは利上げを見送るべき（今回のCPIは利上げの根拠として弱い）。

## データ（FRED API で 2026年10月14日に取得。季節調整値）
| 系列 | 値 | 計算 |
|---|---|---|
| CPIAUCSL（総合） | 2026年9月 336.298、8月 334.131、2025年9月 324.245 | 前年比 +3.72%、前月比 +0.65% |
| CPILFESL（コア） | 9月 338.896、8月 337.765、6月 336.065、4月 335.423、3月 334.165、2025年9月 330.418 | 前年比 +2.57%、前月比 +0.33%、3か月年率 +3.41%。**6か月年率は 9月÷3月で +2.85%**。討論中に言った「約2.1%」は、誤って4月を起点にした5か月分を2乗したもので、誤り（討論後に判明） |
| CPIENGSL（エネルギー） | 9月 337.834、2025年9月 280.700 | 前年比 +20.35%、前月比 +5.20% |
| CUSR0000SETB01（ガソリン） | 9月 376.558、8月 345.169、2025年9月 280.658 | 前月比 +9.09%、前年比 +34.17% |
| UNRATE（失業率） | 9月 4.2%、8月 4.1% | |
| CES0500000003（平均時給） | 9月 37.81ドル、2025年9月 36.70ドル | 前年比 +3.02% |
| T5YIFR（5年先5年の予想インフレ） | 10月13日 2.33% | |
| DFEDTARU（FF金利の上限） | 10月14日 4.00% | |
| DGS10（10年国債） | 10月9日 5.24% | |
| DGS2（2年国債） | 10月9日 4.80% | |
| PCEPILFE（コアPCE） | 8月 130.455、2025年8月 126.646 | 前年比 +3.01%、3か月年率 +2.05% |
| CUSR0000SASLE（住居を除くサービス） | 9月 448.723、8月 447.075 | 前月比 +0.37%、前年比 +3.16% |
| CUSR0000SAH1（住居） | 9月 431.908、8月 430.227 | 前月比 +0.39%、前年比 +3.22% |

取得URLの例：`https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&file_type=json`（APIキーは省略）。2025年10月分は欠測（政府閉鎖）。

## 報道
- 9月の雇用統計：非農業部門雇用者+2万9千人（予想8万4千〜9万5千人）、7月は-1万人、8月は+13万3千人に下方修正、失業率4.2%、平均時給は前年比+3.0%。（[Trading Economics](https://tradingeconomics.com/united-states/unemployment-rate/news/589164)、[Fox Business](https://www.foxbusiness.com/economy/us-jobs-report-september-2026)）
- FOMC（9月15〜16日）：25bpの利上げで3.75〜4.00%、3年余りぶりの利上げ、全会一致。ドット中央値は2026年末4.1%、18人中16人が年内にもう1回以上の利上げを想定。ウォーシュ議長はドットを出さず、選択肢を残すと発言。（[Chase](https://www.chase.com/personal/investments/learning-and-insights/article/federal-reserve-raises-rates-officials-signal-one-more-hike-in-2026)、[Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/2026/09/16/feds-interest-rate-decision-september-16-2026)）
- 9月CPI：総合 前月比+0.6%（予想どおり）、前年比+3.7%（予想3.6%）。コア 前月比+0.3%（予想0.2%）、前年比+2.6%（予想2.5%）。ガソリンは前月比9.1%で総合の上昇の約半分。発表後、市場は10月は見送り・12月に利上げとみている（CNBC）。（[CNN](https://www.cnn.com/2026/10/14/economy/us-cpi-inflation-september)、[CNBC](https://www.cnbc.com/2026/10/14/cpi-inflation-report-september-2026.html)、[ダイヤモンド・ザイ](https://zai.diamond.jp/articles/-/497257)）

## 発言5で使った事実
- CME FedWatch：10月の利上げ確率は9月CPI発表前21.6%→発表後43.7%（据え置き56.3%）。（[PANews](https://panews.io/articles/01a13a80-c997-703a-a341-58f96b33edb8)、[TechFlow](https://www.techflowpost.com/en-US/newsletter/139952)）
- 9月の利上げ直後は55%、10月12日（月）時点で22%。（[Morningstar](https://www.morningstar.com/economy/cpi-forecasts-show-moderated-inflation-september-keeping-fed-hold)）
- WTI（FRED: DCOILWTICO）：9月15日 107.02ドルが8月以降の最高、10月6日 96.24ドル。
- ガソリン小売価格（FRED: GASREGW、週次）：9月21日 4.478ドルが最高、10月5日 4.354ドル。

## 発言7で使った事実
- 2年国債利回り（FRED: DGS2）10月9日 4.80%、FF金利の上限（DFEDTARU）4.00%。
- 航空運賃（FRED: CUSR0000SETG01、季節調整）：8月 323.244（前月比+2.68%）、9月 326.991（前月比+1.16%）。

## 発言9で使った事実
- 住居費（FRED: CUSR0000SAH1）前年比：2025年9月 418.422/2024年9月 403.956＝+3.58%、2026年9月 +3.22%。
- 10年国債利回り（DGS10）10月9日 5.24%。
- 雇用者数：7月 -1万人（改定）、9月 +2万9千人。

## 発言11で使った事実
- 10年物実質利回り（FRED: DFII10）：10月9日 2.91%、2025年の年平均 1.96%（frequency=a）。
- 5年先5年の予想インフレ（T5YIFR）：10月13日 2.33%（9月24日〜10月13日は2.32〜2.36%）。

## 発言13で使った事実
- 総合 前月比+0.6%は予想どおり、コア 前月比+0.3%（予想+0.2%）、前年比+2.6%（予想+2.5%）。（[ダイヤモンド・ザイ](https://zai.diamond.jp/articles/-/497257)、[myforex](https://myforex.com/ja/news/dzh261014188.html)）
- 9月FOMCの議事要旨（10月7日公表）：参加者は追加利上げを見込むが、時期の手がかりはない。（[CNBC](https://www.cnbc.com/2026/10/07/fed-officials-see-another-hike-coming-but-no-sign-as-to-when-minutes-show.html)）
- 発表後、市場は10月は見送り、12月に利上げとの見方（CNBC）。
