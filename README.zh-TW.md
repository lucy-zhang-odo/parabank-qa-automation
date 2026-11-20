# ParaBank QA 自動化測試

以 Parasoft 提供的公開示範網路銀行 [ParaBank](https://parabank.parasoft.com/parabank/) 為測試對象，
使用 **Python、pytest、Playwright** 撰寫 UI 與 API 自動化測試，並在 **GitHub Actions** 執行。

[English](README.md)

## 測試範圍

| 功能 | UI（Playwright） | API（REST） |
|---|---|---|
| 登入／登出 | 正確登入、密碼錯誤、欄位空白、登出後無法進入帳戶頁 | 正確登入回傳客戶資料、密碼錯誤回 400 |
| 註冊 | 新客戶、密碼不一致、帳號已存在、必填欄位 | – |
| 帳戶 | 總覽餘額與 API 一致、開立儲蓄帳戶 | 新客戶只有一個支票帳戶、開戶存款是移轉而非憑空產生、查無帳戶 |
| 轉帳 | 從 UI 轉帳後，以 API 核對餘額、以 UI 核對交易紀錄 | 金額精確（0.01／25.50／100）、總餘額不變、兩個帳戶都有交易紀錄 |
| 已知缺陷 | – | 3 項，見 [docs/findings.md](docs/findings.md) |

## 測試設計

- **自建測試資料**：每個測試檔註冊自己的客戶（帳號不重複），不使用公用示範帳號，不受其他人操作影響。
- **UI 與後端交叉驗證**：UI 操作（開戶、轉帳）後，再用 API 讀回結果，畫面正確但資料存錯也會被抓到。
- **金額用 Decimal 比較**，不用浮點數。
- **已知缺陷寫成嚴格的預期失敗**：測試描述正確行為；ParaBank 修好後測試會故意變紅，提醒更新。
- **對共用網站保持節制**：每個測試檔共用一個客戶、瀏覽器不載入圖片、API 請求之間稍作間隔；
  遇到 429 或網站停擺會明確停止；程式無法呼叫會重設整個網站的端點（`cleanDB` 等）。
- **Page Object Model**：選擇器集中在 `parabank/pages.py`，測試只描述要驗證的事。

## 本機執行

```bash
pip install -r requirements.txt
python -m playwright install chromium
pytest -m api          # 只跑 API
pytest -m ui --headed  # 看著瀏覽器跑 UI
```

設定 `PARABANK_BASE_URL` 可改測其他 ParaBank，例如本機 Docker（`docker run -p 8080:8080 parasoft/parabank`）。

## CI

push 到 `main`、PR、每週一與手動觸發時執行。API 與 UI 測試分成兩個 job 先後執行，分散對示範網站的請求。
每個 job 的 summary 有結果表格，HTML 報告（及 UI 失敗測試的 Playwright trace）上傳為 artifact；
失敗的測試會連同原因顯示在執行頁上。同一時間只跑一個，降低對示範網站的負擔。

示範網站停擺或開始限流（429）時，測試會立刻停止並說明原因，不會把剩下的測試全部報成失敗。
