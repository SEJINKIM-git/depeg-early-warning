# Circle USDC 준비금 증명 보고서 원본 (raw)

이 디렉터리는 Circle 투명성 페이지(https://www.circle.com/transparency)에서 내려받은
월간 USDC 준비금 증명(examination/attestation) PDF를 **변형 없이** 보관한다.
온체인 raw 규칙과 동일하게, 같은 파일명에 같은 내용이면 재사용하고 내용이 다르면
덮어쓰지 않고 오류로 처리한다. 파일명은 `circle_usdc_examination_<기준 월>.pdf`
(기준 월 = 보고서가 다루는 월말 기준일의 연-월)이다.

PDF 수집 일시: `2026-11-06` (UTC 00:47–00:51 사이, macOS `curl`)

| 파일 | 기준일(as-of) | 발행일 | 검증 기관 | 원본 URL (base = `https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/`) | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `circle_usdc_examination_2022-11.pdf` | 2022-11-30 | 2022-12-22 | Grant Thornton LLP | `2022/2022%20USDC%20Circle%20Grant%20Thornton%20Report%20November.pdf` | `cfa178ceef047ff6a6f8c47eff512a1ada3b6bf65d7fc6481c2df4a6a2c30d7c` |
| `circle_usdc_examination_2022-12.pdf` | 2022-12-31 | 2023-01-25 | Grant Thornton LLP | `2022/2022%20USDC%20Circle%20Grant%20Thornton%20Report%20December.pdf` | `ed20b46f081b0cdd9de226611cfdcc586ee3ac6736c35d7822174fb89053c40a` |
| `circle_usdc_examination_2023-01.pdf` | 2023-01-17, 2023-01-31 | 2023-03-02 | Deloitte & Touche LLP | `2023%20USDC_Circle%20Examination%20Report%20January%202023.pdf` | `6dbd9dffe1a399ee4f2cbc11a41824e99df04f8b65ff0b279aa09a30d5fb77c6` |
| `circle_usdc_examination_2023-02.pdf` | 2023-02-09, 2023-02-28 | 2023-03-30 | Deloitte & Touche LLP | `2023%20USDC_Circle%20Examination%20Report%20February%202023.pdf` | `a080c787fadf7c8a928e40977d375b0376df0fce39cde89801bdb7b069af590c` |
| `circle_usdc_examination_2023-03.pdf` | 2023-03-06, 2023-03-31 | 2023-04-28 | Deloitte & Touche LLP | `2023/2023%20USDC_Circle%20Examination%20Report%20March%202023.pdf` | `f855c0b8815e07e7c292be0f419a71d5e776c7a2f703256ca756c6e0522dc0a1` |
| `circle_usdc_examination_2026-07.pdf` | 2026-07-08, 2026-07-31 | 2026-08-27 | Deloitte & Touche LLP | `2026/2026%20USDC_Examination%20Report%20July%2026%20(1).pdf` | `9bb3e852cc468819261b1f72bba3e8344c414f93f95765ef963aaf1e9b6ec0e2` |
| `circle_usdc_examination_2026-08.pdf` | 2026-08-11, 2026-08-31 | 2026-09-29 | Deloitte & Touche LLP | `2026/2026%20USDC_Examination%20Report%20August%2026.pdf` | `ae9d0a3bece12334d24392d8fcdd3fdda3a8662fc05addbe95db928f0a1f2485` |
| `circle_usdc_examination_2026-09.pdf` | 2026-09-04, 2026-09-30 | 2026-10-26 | Deloitte & Touche LLP | `2026/2026%20USDC_Examination%20Report%20September%2026.pdf` | `3c7d773aedb18078d92d8f9be3e6d26fb1e219446ee17624e0f6a376e9399e6a` |

## 주의: 투명성 페이지의 "December 2022" 링크는 USDC가 아니다

투명성 페이지의 2022년 12월 항목은
`2022%20EUROC_Circle%20Examination%20Report%20December%202022.pdf`
(SHA-256 `74ece1b9b57d1dcc144c57d92597cdeb5285282133ed61944de7f533ac63a96c`)을 가리키는데,
열어 보면 **EUROC(유로코인)** 보고서다. 진짜 USDC 2022-12 보고서는 2022년 Grant Thornton
파일명 규칙(`2022/2022 USDC Circle Grant Thornton Report December.pdf`)으로 접근해야 나온다.
파서는 본문에 `USD Coin ("USDC")` 또는 `USDC Reserve Report`가 없는 파일을 거부해야 한다.

## 해시 재계산

```bash
shasum -a 256 data/raw/circle/*.pdf
```
