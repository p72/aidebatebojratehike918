# Opus-A の作戦メモと出典（Opus-B には渡していない）

## 立場
食料品の消費税減税（8%→1%）は、7〜8割以上が値札に届き、CPIを1ポイント超押し下げる（高い転嫁派）。

## 発言1で使った事実
- IMF WP/15/214（Benedek, De Mooij, Keen, Wingender, "Estimating VAT Pass Through"）：ユーロ圏17か国、1999〜2013年の月次データ。標準税率の変更の最終的な転嫁はほぼ100%、軽減税率の変更は約30%、区分の変更はほぼゼロ。引き上げと引き下げで有意な差はない。（[IMF](https://www.imf.org/external/pubs/cat/longres.aspx?sk=43322.0)、[CESifo WP 5531](https://www.cesifo.org/DocDL/cesifo1_wp5531.pdf)）
- ドイツ2020年7〜12月：標準税率19%→16%、軽減税率7%→5%。約13万点のスーパーの価格で、減税分の約70%が転嫁。（[CESifo WP 9149](https://www.econstor.eu/bitstream/10419/236691/1/cesifo1_wp9149.pdf)）
- 総額表示（税込価格の表示）は2021年4月から義務化。
- 1.01÷1.08－1＝－6.48%（完全転嫁なら食料品価格は約6.5%下がる、計算）。

## 先方が使いそうな論点
- 小売の端数価格、値上げラッシュで相殺（第一生命経済研究所「値下がり幅は▲7%より小さい可能性」）
- 外食は対象外
- 増税は転嫁されやすく、減税は転嫁されにくい（NBER の理容業の研究）

## Opus-B の実行記録
| 発言 | サブエージェント | モデル指定 | ツール呼び出し | トークン |
|---|---|---|---|---|
| 2 | a277f9443c659cfbd | opus | 11 | 72,887 |

## 発言3で使った事実
- Fuest ほか：減税のなかったオーストリアを比較対象にした推計。2020年7月1日〜12月31日の時限措置。競合商品の多い商品群ほど転嫁率が高く、自社ブランド（垂直統合）はメーカー品より転嫁率が高い。（[CESifo WP 9149](https://www.econstor.eu/bitstream/10419/236691/1/cesifo1_wp9149.pdf)、[ifo](https://ifo.de/en/press-release/2020-11-09/supermarkets-reduction-vat)）
- ifo の初期の論考（約6万点の Rewe の商品）では平均2%の値下がりで「完全な転嫁」と報告。（[ifo](https://ifo.de/en/publications/2020/article-journal/price-effects-reduction-value-added-tax-german-supermarkets)）
| 4 | a5af1eaa28186208c | opus | 12 | 78,579 |

## 発言5で使った事実
- IMF WP/15/214：引き上げと引き下げで転嫁に有意な差はない。
- 2014年の消費税率引き上げ：国内企業物価やサービス価格はおおむね全額転嫁（伊藤忠経済研究所）。消費者向けは4月の上乗せと5月の巻き戻しが混在。（[伊藤忠経済研究所](https://www.itochu.co.jp/ja/files/20140605_2014-074_J_Inflation.pdf)、[大和総研](https://www.dir.co.jp/report/research/economics/japan/20140425_008477.html)）
| 6 | a303238f299abf44c | opus | 4 | 67,497 |

## 発言7で使った事実
- ドイツ：2021年1月に税率を戻したときの価格効果は、引き下げ時の約半分。（CESifo WP 9149）
- エコノミストの試算で、2027年度の生鮮食品を除く CPI を1〜1.4ポイント押し下げ。（[日本経済新聞](https://www.nikkei.com/article/DGXZQOFL290IKTZ20C26A7000000/)）
- 完全転嫁の場合、消費者物価総合で▲1.5ポイント（第一生命経済研究所の試算）。（[第一生命経済研究所](https://www.dlri.co.jp/report/macro/617880.html)）
| 8 | a64f197017de0fff8 | opus | 9 | 74,381 |

## 発言9で使った事実
- ESPフォーキャスト9月調査（2026年9月15日公表、回答者37名）：消費税減税による物価押し下げ効果は1.07%ポイント。（[日本経済研究センター](https://www.jcer.or.jp/?p=141346)。検索結果の抜粋で確認）
- 8月調査：食料品の時限的減税を織り込んだ機関の平均で、2027年度のコアCPIは1.00%。（[日本経済研究センター](https://www.jcer.or.jp/esp/20260812-3.html)）
- 1.07÷1.3〜1.5＝約0.7〜0.8（計算）。
| 10 | a15f83b50d6862e98 | opus | 5 | 68,832 |

## 発言11で使った事実（e-Stat API で取得）
- 消費者物価指数（2020年基準、全国、品目「ビール」コード2021、statsDataId=0003427113）：2020年9月 101.0 → 10月 96.7（-4.3%）、2023年9月 101.2 → 10月 97.2（-4.0%）。
- 同「ビール風アルコール飲料」（コード2027）は増税で、2020年9月 95.3 → 10月 107.5、2023年9月 114.6 → 10月 127.2。
- ビールの酒税は2020年10月に350mlあたり77円→70円（7円減）、2023年10月に70円→63.35円。（[サントリー](https://www.suntory.co.jp/news/article/13716.html)、[キリン](https://www.kirinholdings.com/jp/newsroom/release/2020/0526_02.pdf)）
- 取得URLの例：`https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?statsDataId=0003427113&cdCat01=2021&cdArea=00000&cdTab=1`（appId は省略）
| 12 | ab60ddd0179e684fe | opus | 4 | 70,160 |
| 14 | a4aac8daa3cfaa4c9 | opus | 4 | 70,607 |
| 16 | ab770c21bfbfdf3ae | opus | 1 | 67,333 |
| ファクトチェック | a49504e96ea4695ba | opus | 24 | 90,612 |
