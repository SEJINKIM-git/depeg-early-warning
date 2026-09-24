"""Bitstamp raw HTTP response를 변형 없이 보존한다."""

from __future__ import annotations

from pathlib import Path


class RawResponseConflictError(RuntimeError):
    """같은 요청 경로에 서로 다른 raw response가 이미 존재한다."""


def raw_response_filename(start_time: str, end_time: str) -> str:
    """Chunk 요청 경계를 포함한 Windows-safe 파일명을 만든다."""
    safe_start = start_time.replace(":", "-")
    safe_end = end_time.replace(":", "-")
    return f"bitstamp_usdcusd_{safe_start}_{safe_end}.json"


class RawResponseDirectory:
    """요청별 raw bytes를 충돌 안전 정책으로 저장하는 callable sink."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    def __call__(self, body: bytes, start_time: str, end_time: str) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / raw_response_filename(start_time, end_time)
        if target.exists():
            if target.read_bytes() == body:
                return target
            raise RawResponseConflictError(
                f"raw response conflict for existing file: {target}"
            )

        try:
            with target.open("xb") as raw_file:
                raw_file.write(body)
        except FileExistsError:
            if target.read_bytes() == body:
                return target
            raise RawResponseConflictError(
                f"raw response conflict for existing file: {target}"
            ) from None
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return target
