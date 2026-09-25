"""Bitstamp raw HTTP response를 변형 없이 보존한다."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


class RawResponseConflictError(RuntimeError):
    """같은 요청 경로에 서로 다른 raw response가 이미 존재한다."""


def raw_response_filename(start_time: str, end_time: str) -> str:
    """Chunk 요청 경계를 포함한 Windows-safe 파일명을 만든다."""
    safe_start = start_time.replace(":", "-")
    safe_end = end_time.replace(":", "-")
    return f"bitstamp_usdcusd_{safe_start}_{safe_end}.json"


class ProvisionalRawResponse:
    """완전히 기록된 임시 파일을 검증 결과에 따라 원자적으로 게시한다."""

    def __init__(
        self,
        temporary_path: Path,
        canonical_path: Path,
        failed_directory: Path,
        body_digest: str,
    ) -> None:
        self.temporary_path = temporary_path
        self.canonical_path = canonical_path
        self.failed_directory = failed_directory
        self.body_digest = body_digest

    def _publish(self, target: Path) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(self.temporary_path, target)
        except FileExistsError:
            if target.read_bytes() != self.temporary_path.read_bytes():
                raise RawResponseConflictError(
                    f"raw response conflict for existing file: {target}"
                ) from None
        finally:
            self.temporary_path.unlink(missing_ok=True)
        return target

    def publish(self) -> Path:
        """검증된 body를 canonical filename으로 no-clobber 게시한다."""
        return self._publish(self.canonical_path)

    def quarantine(self) -> Path:
        """검증 실패 body를 canonical namespace 밖에 보존한다."""
        failed_name = (
            f"{self.canonical_path.stem}.failed-{self.body_digest}.json"
        )
        return self._publish(self.failed_directory / failed_name)


class RawResponseDirectory:
    """요청별 raw bytes를 충돌 안전 정책으로 저장하는 callable sink."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    def stage(
        self, body: bytes, start_time: str, end_time: str
    ) -> ProvisionalRawResponse:
        """body를 같은 filesystem의 임시 파일에 완전히 기록한다."""
        self.directory.mkdir(parents=True, exist_ok=True)
        canonical_path = self.directory / raw_response_filename(start_time, end_time)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=self.directory,
            prefix=f".{canonical_path.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as raw_file:
                written = raw_file.write(body)
                if written != len(body):
                    raise OSError("incomplete raw response write")
                raw_file.flush()
                os.fsync(raw_file.fileno())
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
        return ProvisionalRawResponse(
            temporary_path=temporary_path,
            canonical_path=canonical_path,
            failed_directory=self.directory / "failed",
            body_digest=hashlib.sha256(body).hexdigest(),
        )

    def __call__(self, body: bytes, start_time: str, end_time: str) -> Path:
        """검증이 필요 없는 호출자를 위한 즉시 atomic publish 호환 API."""
        return self.stage(body, start_time, end_time).publish()
