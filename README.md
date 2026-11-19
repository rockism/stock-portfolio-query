# Portfolio Value Query

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

用公開報價估算台股、美股持股的台幣現值，並列出現金、借款與質押持股市值／借款比率。只需 Python 3 標準函式庫。

## 使用

1. 複製 `examples/portfolio.example.json` 到你自己的私人路徑，修改成自己的持股。不要把真實持股提交到 Git。
2. 執行 `python3 portfolio_value.py --portfolio /path/to/portfolio.json`。
3. 要取得結構化結果，加入 `--json`。

檔案格式見範例。`market` 可為 `TW` 或 `US`；台股代碼不帶 `.TW`；`shares` 必須大於零。`pledged` 標示台股質押持股。同一股票若同時有一般持股與質押持股，請列成兩筆。`cash_twd`、`loan_twd` 未知時請省略；省略現金會使資產合計與淨資產顯示為空，省略借款會使淨資產與質押比率顯示為空。不能填零冒充已確認的餘額。

## 實測範例：質押維持率 360.8% 怎麼算？

2026/11/20 00:27:56（台灣時間，UTC+8），以版本 `91df8f6` 執行[範例持股檔](examples/portfolio.example.json)，取得以下 Yahoo Finance 報價。

| 標的 | 範例部位 | 當時報價 | 報價時間（台灣時間） |
|---|---|---:|---|
| 2330 | 一般持股 10 股 | NT$2,100.00／股 | 2026/11/19 13:30:05 |
| 0050 | **質押 20 股** | **NT$90.20／股** | **2026/11/19 13:30:01** |
| AAPL | 一般持股 2 股 | US$349.72／股 | 2026/11/20 00:27:53 |
| USD/TWD | 美股換算匯率 | NT$33.014／美元 | 2026/11/20 00:27:53 |

1. **算質押市值。** 範例中只有 0050 標記為 `pledged: true`。20 股 × NT$90.20／股 = **NT$1,804**。
2. **除以借款餘額，再換成百分比。** 範例的質押借款（`loan_twd`）為 NT$500，因此 NT$1,804 ÷ NT$500 × 100% = **360.8%**。

換句話說，每借 NT$1，當時約有 NT$3.61 的質押股票作為擔保。這是按當時報價估算的維持率，券商正式維持率依契約計算。

執行下列指令即可用同一份範例重新查價。結果在 `summary.pledge_coverage_percent`，會隨報價變動。

```sh
python3 portfolio_value.py --portfolio examples/portfolio.example.json --json
```

## 用券商 App 截圖更新持股

在支援看圖的 AI 助理中，把券商 App 的持股頁面截圖交給助理，並請它依 `SKILL.md` 更新**本機私人**持股 JSON。可提供多張截圖，涵蓋一般持股、質押持股，以及借款餘額頁；若要完整資產總覽，還需提供現金資料。截圖可讓助理整理資料，命令列程式本身沒有圖片辨識功能。

助理應逐筆核對股票代號、股數、幣別及是否質押。能清楚辨識且對應帳戶確定的資料，可先備份私人 JSON，再更新並驗證格式，最後回報實際差異；不需另外下指令確認。看不清、被裁切或頁面未涵蓋的資料須標成「需確認」，不可猜測，也不可把未出現在截圖中的既有持股直接刪除。若截圖與現有資料衝突、或無法判定一般股與質押股的歸屬，先列出差異請使用者釐清。截圖中的姓名、帳號與餘額屬敏感資料，請勿提交到公開倉庫。

### 截圖範例：同一檔股票有部分股數已質押

![虛構券商 App 持股明細：2330 庫存共 1,000 股，包含一般持股 700 股與質押持股 300 股。](assets/portfolio-2330-demo.svg?v=2)

假設同一帳戶、同一時間的券商 App 截圖顯示下列資料。股數均為虛構，單位為「股」。

| 截圖頁面 | 股票代號 | 畫面上的欄位 | 股數 |
|---|---|---|---:|
| 持股總覽 | 2330 | 庫存總股數（含已質押） | 1,000 |
| 質押明細 | 2330 | 已質押股數 | 300 |

總覽的 1,000 股已包含質押的 300 股，因此一般持股為 **1,000 − 300 = 700 股**。更新私人 JSON 時，同一個代號分兩筆存入 `holdings`：

```json
{
  "holdings": [
    {"market": "TW", "symbol": "2330", "shares": 700, "pledged": false},
    {"market": "TW", "symbol": "2330", "shares": 300, "pledged": true}
  ]
}
```

核對時，兩筆相加應等於庫存總數（700 + 300 = 1,000 股）。計算質押維持率時，只有標記為 `true` 的 300 股計入擔保品市值。若畫面已明列「未質押股數」，可直接採用該數字；若無法判斷總覽是否包含質押股，先確認欄位定義再更新。

程式以 `pledged=true` 的台股市值除以 `loan_twd`，計算 `pledge_coverage_percent`（%）。質押股票報價缺失、借款餘額未知或為零時不輸出比率。券商正式維持率可能按契約納入其他擔保品、折扣與負債；若需要與券商數字一致，須以該券商規則和當前借款資料核對。截圖裡的券商維持率可作比對，但不應悄悄覆寫程式估算值。

報價取自 Yahoo Finance chart endpoint，可能延遲、停留在前一交易日或無法取得。每筆報價和匯率附 UTC 時間；程式不保證它是即時成交價或正式收盤價。查價失敗時不輸出完整資產總額，exit code 為 1；輸入錯誤為 2。

請勿把真實持股檔、執行輸出、API 憑證或個人財務資料提交到公開倉庫。

## 授權

程式與文件採 [MIT License](LICENSE)。

## English

Estimate Taiwan and US stock holdings in TWD using public quotes. The report includes cash, loans and estimated coverage of loans secured by Taiwan stocks. Requires only the Python 3 standard library.

### Run a valuation

Copy [the fictional portfolio](examples/portfolio.example.json) to a private location and edit your copy. Run `python3 portfolio_value.py --portfolio /path/to/portfolio.json`. Add `--json` for structured output.

Use `TW` or `US` for `market`, omit the exchange suffix from Taiwan symbols, and enter a positive number of shares. Use separate rows for pledged and unpledged shares of the same stock. Omit unknown balances. Missing `cash_twd` leaves total and net assets blank. Missing `loan_twd` leaves net assets and coverage blank. Enter zero only for a confirmed zero balance.

### Worked example: 360.8% collateral coverage

At 00:27:56 on November 20, 2026 (Taiwan time, UTC+8), version `91df8f6` retrieved these Yahoo Finance quotes for the sample portfolio.

| Symbol | Example position | Price or exchange rate | Quote time (UTC+8) |
|---|---|---:|---|
| 2330 | 10 unpledged shares | NT$2,100.00 | 2026-11-19 13:30:05 |
| 0050 | 20 pledged shares | NT$90.20 | 2026-11-19 13:30:01 |
| AAPL | 2 unpledged shares | US$349.72 | 2026-11-20 00:27:53 |
| USD/TWD | Currency conversion | NT$33.014 per US dollar | 2026-11-20 00:27:53 |

Only 0050 was pledged. Its 20 shares × NT$90.20 were worth **NT$1,804**. Dividing by the NT$500 outstanding loan gives **NT$1,804 ÷ NT$500 × 100% = 360.8%**, or about NT$3.61 in collateral per NT$1 borrowed. To see the estimate at current available prices, run:

```sh
python3 portfolio_value.py --portfolio examples/portfolio.example.json --json
```

Read `summary.pledge_coverage_percent` in the output.

### Update holdings from brokerage screenshots

Give a vision-capable assistant the holdings, pledge and loan balance screens and ask it to follow [SKILL.md](SKILL.md) to update your private JSON. Include cash for a full asset valuation. The assistant reads the images. The command-line tool reads JSON.

Match each visible symbol, share count, currency and pledge status to the correct account. For clear entries, back up the file, update it, validate it and report the changes. Keep existing entries outside the screenshot. Ask for clarification if a field is cropped, the account is ambiguous or figures conflict.

![Fictional brokerage screen: 1,000 shares of 2330, including 700 unpledged and 300 pledged.](assets/portfolio-2330-demo.svg?v=2)

In this separate screenshot example, the holdings screen shows **1,000 shares of 2330 including collateral**, and the pledge screen shows **300 pledged** in the same account at the same time. Record **700 unpledged shares** and **300 pledged shares**:

```json
{
  "holdings": [
    {"market": "TW", "symbol": "2330", "shares": 700, "pledged": false},
    {"market": "TW", "symbol": "2330", "shares": 300, "pledged": true}
  ]
}
```

The rows add up to 1,000. Only the 300 pledged shares count toward coverage. If a screen explicitly lists unpledged shares, use that figure directly. If the total's definition is unclear, confirm it before updating.

### Interpreting the output

Coverage equals the market value of pledged Taiwan shares divided by the outstanding loan, expressed as a percentage. A missing pledged quote or a missing or zero loan balance leaves coverage blank. Your broker may apply collateral discounts or include other assets or liabilities under your agreement. Keep the broker's figure separate when comparing it with this estimate.

Yahoo Finance quotes and exchange rates carry UTC timestamps and can be delayed, unavailable or from a previous session. When a required quote is missing, the tool omits complete portfolio totals and exits with code 1. Invalid input exits with code 2. Keep real holdings, account screenshots, private output and credentials out of public repositories.

### License

The code and documentation use the [MIT License](LICENSE).
