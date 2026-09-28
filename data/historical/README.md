# USDC historical hourly signals

이 디렉터리의 데이터는 Bitstamp public OHLC API의 `usdcusd` 시장에서 받은
USDC/USD 가격을 Signal v1 형식으로 변환한 결과다. 각 `price_usd` 값은 UTC 기준
1시간 캔들의 종가이며, 같은 시각의 `peg_deviation_bps`는
`(price_usd - 1.0) * 10,000`을 소수 둘째 자리로 반올림해 계산한다.

## 수집 구간

| 구분 | 파일 | 시작(포함) | 종료(제외) | 시간 | 시그널 수 |
| --- | --- | --- | --- | ---: | ---: |
| 위기 | `signals_usdc_2023_depeg_hourly.json` | `2023-03-09T00:00:00Z` | `2023-03-14T00:00:00Z` | 120 | 240 |
| 평시 | `signals_usdc_2023_calm_hourly.json` | `2023-01-15T00:00:00Z` | `2023-02-12T00:00:00Z` | 672 | 1,344 |

## 출처 기록

기존 데이터의 출처 기록 파일은 `USDC price data.xlsx`다. 이 파일에는 공통으로
`Source: Bitstamp Public API, USDC/USD OHLC endpoint`, 데이터 접근·수집일
`2026-09-18`, `Interval: 1 hour (step=3600)`이 기록되어 있다.

| 구분 | 엑셀에 기록된 기간 | API URL |
| --- | --- | --- |
| 평시 | `2023-01-15 00:00–2023-02-11 23:00 UTC` (672시간) | `https://www.bitstamp.net/api/v2/ohlc/usdcusd/?step=3600&limit=672&start=1673740800&end=1676156400` |
| 위기 | `2023-03-09 00:00–2023-03-13 23:00 UTC` (120시간) | `https://www.bitstamp.net/api/v2/ohlc/usdcusd/?step=3600&limit=120&start=1678320000&end=1678748400` |

`USDC price data.xlsx`의 SHA-256은
`26B6174ADA8FC47CDA164CEA14E947AEC207421CBB5798FC967CB203F0FC705B`다. 이 값은
출처 기록용 엑셀 파일의 해시이며 Bitstamp raw JSON 파일의 해시가 아니다.

## 재생성

저장소 루트의 Windows PowerShell 5.1에서 다음 명령을 실행한다. 이 함수는 변환된
Signal JSON을 대상 파일과 같은 디렉터리의 임시 파일에 UTF-8 BOM 없이 기록한다.
수집과 임시 파일 기록이 모두 성공한 경우에만 기존 파일을 교체하며, 실패하면 임시
파일을 삭제하고 기존 historical 파일을 보존한다. 요청별 원본 HTTP 응답은
기본적으로 `data/raw/bitstamp/usdcusd/`에 함께 보존된다.

```powershell
function Export-BitstampHistory {
    param(
        [Parameter(Mandatory = $true)][string]$Start,
        [Parameter(Mandatory = $true)][string]$End,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    $target = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
    $directory = Split-Path -Parent $target
    $temporary = Join-Path $directory ("." + [System.IO.Path]::GetRandomFileName())
    $backup = Join-Path $directory ("." + [System.IO.Path]::GetRandomFileName())

    try {
        $jsonLines = & .\.venv\Scripts\python.exe -m scripts.collect_bitstamp_usdc --start $Start --end $End
        if ($LASTEXITCODE -ne 0) {
            throw "Bitstamp collection failed with exit code $LASTEXITCODE"
        }

        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllLines(
            $temporary,
            [string[]]$jsonLines,
            $utf8NoBom
        )

        if ([System.IO.File]::Exists($target)) {
            [System.IO.File]::Replace($temporary, $target, $backup)
            Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
        } else {
            [System.IO.File]::Move($temporary, $target)
        }
    } finally {
        Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
    }
}

Export-BitstampHistory -Start 2023-03-09T00:00:00Z -End 2023-03-14T00:00:00Z -OutputPath data/historical/signals_usdc_2023_depeg_hourly.json
Export-BitstampHistory -Start 2023-01-15T00:00:00Z -End 2023-02-12T00:00:00Z -OutputPath data/historical/signals_usdc_2023_calm_hourly.json
```

raw 파일명은 요청 청크의 시작과 종료를 포함하는
`bitstamp_usdcusd_<chunk-start>_<chunk-end>.json` 형식이다. Windows에서도 사용할
수 있도록 시각 안의 `:`는 `-`로 바뀐다. 예를 들면
`bitstamp_usdcusd_2023-03-09T00-00-00Z_2023-03-14T00-00-00Z.json`이다.

## 무결성과 검토 기록

`2026-09-18` 접근·수집 당시의 Bitstamp raw JSON 파일은 보관되어 있지 않다. 위에
기록한 엑셀 파일의 SHA-256은 당시 raw JSON의 해시를 대신하지 않는다.

raw 출처를 복구하기 위해 `2026-09-28T09:03:16Z`에 같은 요청 기간을 다시 수집했다.
재수집한 Signal 결과를 기존 historical JSON과 비교한 결과 전체 시그널 수,
`(observed_at, metric)` 키와 배열 순서, 각 `value`, `schema_version`, 시간 범위 및
전체 JSON 배열이 두 기간 모두 동일했다. 기존 historical JSON은 수정하지 않았다.

| 구분 | 요청 기간 (`--start` 포함, `--end` 제외) | 재검증 raw 파일명 | SHA-256 |
| --- | --- | --- | --- |
| 평시 | `2023-01-15T00:00:00Z`–`2023-02-12T00:00:00Z` | `bitstamp_usdcusd_2023-01-15T00-00-00Z_2023-02-12T00-00-00Z.json` | `1357F54F5006132FE4E16C2966DED73EB101DF48DA210A57295FDF717CB7D1E3` |
| 위기 | `2023-03-09T00:00:00Z`–`2023-03-14T00:00:00Z` | `bitstamp_usdcusd_2023-03-09T00-00-00Z_2023-03-14T00-00-00Z.json` | `14E6C75DE426EE0BF43BCAFFDA0CB76B391634FFCBD024CFEC5689A771D4F24C` |

위 해시는 `data/raw/bitstamp/usdcusd/`에 보존한 재검증 raw JSON의 해시다. 최초
수집 raw와 바이트 단위로 동일하다는 뜻은 아니다. 이후 수집에서도 raw 파일을
보존하고 다음과 같이 해시를 산출하며, UTC 수집일시, 대상 기간, raw 파일명,
SHA-256을 한 기록에 함께 남겨야 한다.

```powershell
Get-FileHash -Algorithm SHA256 data/raw/bitstamp/usdcusd/*.json
```

엑셀을 이용한 검토 과정에서 데이터 값을 수동으로 수정하지 않았다. historical
파일은 수집 결과를 코드로 변환한 값이며, 테스트에서 시간 연속성, 중복, 스키마,
가격과 페그 이탈값의 일치 여부를 검사한다.

엑셀에는 `close price`와 `volume`이 있지만 현재 historical Signal JSON에는 거래량을
포함하지 않았다. 현재 파일에는 1시간 종가로 만든 `price_usd`와 가격에서 계산한
`peg_deviation_bps`만 저장한다.

## 한계

Bitstamp는 중앙화 거래소다. 이 데이터는 거래소의 USDC/USD 체결을 집계한 시장
가격이며 블록체인 상태나 DEX 거래를 직접 관측한 엄밀한 온체인 데이터가 아니다.
따라서 온체인 유동성, 준비금 상태, 다른 거래소와의 가격 차이를 단독으로 설명할
수 없다.
