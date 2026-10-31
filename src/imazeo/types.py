"""Public types for the Imazeo Python SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Literal, TypeVar, TypedDict

T = TypeVar("T")

FitMode = Literal["cover", "contain", "inside", "fill"]
ImageFormat = Literal["jpeg", "png", "webp", "avif", "gif"]
RotateDegrees = Literal[-360, -270, -180, -90, 0, 90, 180, 270, 360]
TransformMode = Literal["PERSIST", "CACHE", "EPHEMERAL"]
QrFormat = Literal["png", "svg"]
ErrorCorrection = Literal["L", "M", "Q", "H"]
BarcodeType = Literal["code128", "code39", "ean13", "ean8", "upca", "itf14"]
BarcodeImageFormat = Literal["png", "svg"]
PdfImageFormat = Literal["png", "jpeg", "webp"]
Position = Literal["center", "entropy", "attention"]


@dataclass(slots=True)
class PageParams:
    page: int | None = None
    limit: int | None = None
    q: str | None = None


@dataclass
class Page(Generic[T]):
    items: list[T]
    page: int
    limit: int
    total: int
    pages: int
    request_id: str


@dataclass
class BinaryResult:
    data: bytes
    content_type: str
    request_id: str
    headers: dict[str, str] = field(default_factory=dict)
    etag: str | None = None
    width: int | None = None
    height: int | None = None
    format: str | None = None
    transformation_id: str | None = None
    cache: str | None = None
    pdf_page: int | None = None
    not_modified: bool = False


class ImageMetadata(TypedDict):
    format: str
    mimeType: str
    width: int
    height: int
    frames: int
    pixelCount: int
    hasAlpha: bool
    orientation: int | None


class ImageRecord(TypedDict):
    _id: str
    projectId: str
    sourceType: Literal["upload"]
    originalName: str
    bytes: int
    sha256: str
    metadata: ImageMetadata
    status: str
    createdAt: str
    updatedAt: str


class CropSpec(TypedDict):
    left: int
    top: int
    width: int
    height: int


class ExtendSpec(TypedDict):
    top: int
    right: int
    bottom: int
    left: int


class TrimSpec(TypedDict):
    threshold: int


class TransformSpec(TypedDict, total=False):
    width: int
    height: int
    fit: FitMode
    crop: CropSpec
    format: ImageFormat
    quality: int
    rotate: RotateDegrees
    flip: bool
    flop: bool
    optimize: bool
    stripMetadata: Literal[True]
    grayscale: bool
    negate: bool
    blur: float
    sharpen: float
    brightness: float
    saturation: float
    hue: int
    trim: Literal[True] | TrimSpec
    extend: ExtendSpec
    background: str
    position: Position


class TransformRequest(TypedDict, total=False):
    imageId: str
    url: str
    mode: TransformMode
    maxOutputBytes: int
    transform: TransformSpec


class NormalizedTransformSpec(TypedDict):
    width: int | None
    height: int | None
    fit: FitMode
    crop: CropSpec | None
    format: ImageFormat
    quality: int
    rotate: Literal[0, 90, 180, 270]
    flip: bool
    flop: bool
    optimize: bool
    stripMetadata: Literal[True]
    grayscale: bool
    negate: bool
    blur: float | None
    sharpen: float | None
    brightness: float | None
    saturation: float | None
    hue: int | None
    trim: TrimSpec | None
    extend: ExtendSpec | None
    background: str
    position: Position


class TransformationRecord(TypedDict):
    _id: str
    projectId: str
    imageId: str | None
    sourceHash: str
    transformHash: str
    spec: NormalizedTransformSpec
    mode: TransformMode
    bytes: int
    processingMs: int
    status: str
    sha256: str
    metadata: ImageMetadata
    expiresAt: str | None
    createdAt: str


class ApiKeyContext(TypedDict):
    projectId: str
    keyId: str


class _QrRequired(TypedDict):
    content: str


class QrGenerateInput(_QrRequired, total=False):
    format: QrFormat
    size: int
    margin: int
    errorCorrection: ErrorCorrection
    foreground: str
    background: str


class _BarcodeRequired(TypedDict):
    type: BarcodeType
    content: str


class BarcodeGenerateInput(_BarcodeRequired, total=False):
    format: BarcodeImageFormat
    scale: int
    height: int
    includeText: bool
    foreground: str
    background: str


class PdfPageInfo(TypedDict):
    pageNumber: int
    width: float
    height: float


class PdfInfo(TypedDict):
    pageCount: int
    encrypted: bool
    pages: list[PdfPageInfo]


class PdfRenderOptions(TypedDict, total=False):
    pages: str
    rangeStart: int
    rangeEnd: int
    all: bool
    format: PdfImageFormat
    scale: float
    quality: int


class PdfRenderPage(TypedDict):
    pageNumber: int
    width: float
    height: float
    contentType: str
    data: str


class PdfExtractOptions(TypedDict, total=False):
    pages: str
    rangeStart: int
    rangeEnd: int


@dataclass(slots=True)
class UploadFile:
    """Explicit multipart upload payload (bytes only — never a filesystem path string)."""

    data: bytes
    filename: str | None = None
    content_type: str | None = None


UploadSource = bytes | bytearray | memoryview | UploadFile


@dataclass(slots=True)
class PreparedUpload:
    data: bytes
    filename: str
    content_type: str

    @property
    def byte_length(self) -> int:
        return len(self.data)


@dataclass(slots=True)
class PdfMultiPageResult:
    pages: list[PdfRenderPage]
    request_id: str
