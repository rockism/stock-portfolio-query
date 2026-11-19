# Portfolio Value Query

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

用公開報價估算台股、美股持股的台幣現值，並列出現金、借款與質押持股市值／借款比率。只需 Python 3 標準函式庫。

## 第一次使用

1. 在 GitHub 選 **Code → Download ZIP**，解壓縮後，在含有 `portfolio_value.py` 的資料夾開啟終端機。
2. 安裝 Python 3 後，直接用虛構資料試跑：`python3 portfolio_value.py --portfolio examples/portfolio.example.json --json`。查看 `summary.pledge_coverage_percent`，即可看到依當次報價估算的質押維持率。
3. 用能看圖、讀寫本機檔案並執行 Python 的 AI 助理開啟同一個資料夾，貼上：「請閱讀 [SKILL.md](SKILL.md)，用範例持股查詢現值，說明質押維持率怎麼算。」

要開始記錄自己的持股時，請指定專案外的私人檔案路徑，並明確要求「請依這些截圖建立我的持股檔」。新檔只填入已確認的個人持股與餘額；範例中的股票、股數、現金與借款都不要帶入。之後可用 `python3 portfolio_value.py --portfolio /path/to/portfolio.json` 查詢，加上 `--json` 可取得結構化輸出。

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

助理應逐筆核對股票代號、股數、幣別及是否質押。只提供截圖、詢問內容或要求試算時，一律唯讀。只有在使用者明確要求建立或更新持股檔時才寫入；更新既有檔案前先備份，完成後驗證格式並回報差異。看不清、被裁切或頁面未涵蓋的資料須標成「需確認」，不可猜測，也不可把未出現在截圖中的既有持股直接刪除。若截圖與現有資料衝突、或無法判定一般股與質押股的歸屬，先列出差異請使用者釐清。截圖中的姓名、帳號與餘額屬敏感資料，請勿提交到公開倉庫。

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

#### 2330 截圖實測結果

使用版本 `f1ce838` 的技能說明和上方虛構截圖，在獨立的暫存目錄分兩輪測試。

1. **只問「圖中持股多少？」** 助理回答：2330 共 1,000 股，其中一般持股 700 股、質押持股 300 股。回答前後，存放私人持股檔的測試目錄都是空的。
2. **明確要求「依這張截圖建立持股檔」。** 助理建立了 1 個 JSON 檔。用 `load_portfolio` 讀回後，確認只有兩筆：2330 一般持股 **700 股**（`pledged: false`）及 2330 質押持股 **300 股**（`pledged: true`）。

測試也核對了範例檔中的 2330 **10 股**、0050、AAPL 和範例現金、借款均未帶入。截圖未列借款餘額，因此本次估值的質押維持率為 `null`。

程式以 `pledged=true` 的台股市值除以 `loan_twd`，計算 `pledge_coverage_percent`（%）。質押股票報價缺失、借款餘額未知或為零時不輸出比率。券商正式維持率可能按契約納入其他擔保品、折扣與負債；若需要與券商數字一致，須以該券商規則和當前借款資料核對。截圖裡的券商維持率可作比對，但不應悄悄覆寫程式估算值。

報價取自 Yahoo Finance chart endpoint，可能延遲、停留在前一交易日或無法取得。每筆報價和匯率附 UTC 時間；程式不保證它是即時成交價或正式收盤價。查價失敗時不輸出完整資產總額，exit code 為 1；輸入錯誤為 2。

請勿把真實持股檔、執行輸出、API 憑證或個人財務資料提交到公開倉庫。

## 授權

程式與文件採 [MIT License](LICENSE)。

## English

Estimate Taiwan and US stock holdings in TWD using public quotes. The report includes cash, loans and estimated coverage of loans secured by Taiwan stocks. Requires only the Python 3 standard library.

### First-time setup

1. On GitHub, choose **Code → Download ZIP**. Extract the archive and open a terminal in the folder containing `portfolio_value.py`.
2. With Python 3 installed, run `python3 portfolio_value.py --portfolio examples/portfolio.example.json --json`. The fictional portfolio is ready to use. Look for `summary.pledge_coverage_percent` to see the coverage estimate at the prices returned.
3. Open the same folder in an AI assistant that can read images, access local files and run Python. Try this prompt: “Read [SKILL.md](SKILL.md), value the example portfolio and explain how you calculated collateral coverage.”

To start your own portfolio, specify a private path outside the repository and explicitly ask the assistant to create the file from your screenshots. Include only your confirmed holdings and balances. Leave out all sample symbols, share counts, cash and loans unless independently confirmed by your own data. Query your file with `python3 portfolio_value.py --portfolio /path/to/portfolio.json`. Add `--json` for structured output.

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

Match each visible symbol, share count, currency and pledge status to the correct account. A screenshot, question or valuation request is read-only. Write only when the user explicitly requests creation or an update. Back up an existing file before updating it, validate the result and report the changes. Keep existing entries outside the screenshot. Ask for clarification if a field is cropped, the account is ambiguous or figures conflict.

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

#### 2330 screenshot test results

This two-step test used the fictional screenshot above and the skill instructions from version `f1ce838` in a separate temporary directory.

1. **“How many shares are shown?”** The assistant reported 1,000 shares of 2330: 700 unpledged and 300 pledged. The directory designated for the private portfolio file was empty both before and after the answer.
2. **“Create a holdings file from this screenshot.”** The assistant created one JSON file. Reading it back with `load_portfolio` confirmed exactly two entries: **700 unpledged** shares of 2330 (`pledged: false`) and **300 pledged** shares of 2330 (`pledged: true`).

The file contained none of the sample portfolio’s 10-share 2330 position, 0050 or AAPL holdings, cash or loan balance. The screenshot showed no outstanding loan balance, so the valuation returned `null` for collateral coverage.

### Interpreting the output

Coverage equals the market value of pledged Taiwan shares divided by the outstanding loan, expressed as a percentage. A missing pledged quote or a missing or zero loan balance leaves coverage blank. Your broker may apply collateral discounts or include other assets or liabilities under your agreement. Keep the broker's figure separate when comparing it with this estimate.

Yahoo Finance quotes and exchange rates carry UTC timestamps and can be delayed, unavailable or from a previous session. When a required quote is missing, the tool omits complete portfolio totals and exits with code 1. Invalid input exits with code 2. Keep real holdings, account screenshots, private output and credentials out of public repositories.

### License

The code and documentation use the [MIT License](LICENSE).
