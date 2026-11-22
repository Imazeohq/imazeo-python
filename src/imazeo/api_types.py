"""API-key request and response models."""
from __future__ import annotations
from typing import Literal, TypedDict, TYPE_CHECKING
if TYPE_CHECKING:
    from imazeo.types import QrGenerateInput

class _CodeDesignRequired(TypedDict):
    schemaVersion: Literal[1]
    template: Literal['classic', 'rounded', 'dots', 'label']
    templateVersion: Literal[1]


class CodeDesign(_CodeDesignRequired, total=False):
    moduleShape: Literal['square', 'rounded', 'dots', 'soft', 'classy']
    finderOuter: Literal['square', 'rounded', 'circle']
    finderInner: Literal['square', 'rounded', 'dot']
    fill: Literal['solid', 'linear']
    textAlign: Literal['left', 'center', 'right']
    fontFamily: Literal['sans', 'serif', 'mono']
    fontWeight: Literal['normal', 'bold']
    barTextAlign: Literal['left', 'center', 'right']
    barTextPosition: Literal['above', 'below']
    moduleScale: int
    gradientAngle: int
    logoScale: int
    logoPadding: int
    captionSize: int
    quietZone: int
    barTextSize: int
    finderColor: str
    finderInnerColor: str
    gradientColor: str
    frameColor: str
    captionColor: str
    headline: str
    subtitle: str
    frame: Literal['none', 'line', 'rounded', 'brackets', 'badge']
    caption: str
    logoImageId: str


class DocxOptions(TypedDict, total=False):
    page: int
    scale: float
    format: Literal['png', 'jpeg', 'webp']
    quality: int
    fitSinglePage: bool
    honorWordPageBreaks: bool
    renderHeaders: bool
    renderFooters: bool
    renderFootnotes: bool
    renderEndnotes: bool
    repairBrokenRelationships: bool
    unwrapSdt: bool
    collapseMcAlternate: bool
    ignoreImageWrap: bool
    ignoreTableWrap: bool
    applyWordChrome: bool
    normalizeTheme: bool
    renderChanges: bool


class XlsxOptions(TypedDict, total=False):
    page: int
    scale: float
    format: Literal['png', 'jpeg', 'webp']
    quality: int
    engine: Literal['xlsx']
    sheet: int
    renderMode: Literal['sheet', 'print']
    range: str
    showGridLines: bool
    paperSize: Literal['saved', 'A3', 'A4', 'A5', 'Letter', 'Legal', 'Tabloid', 'B5']


class PptxOptions(TypedDict, total=False):
    page: int
    scale: float
    format: Literal['png', 'jpeg', 'webp']
    quality: int
    engine: Literal['pptx']


class WebsiteOptions(TypedDict, total=False):
    page: int
    scale: float
    format: Literal['png', 'jpeg', 'webp']
    quality: int
    engine: Literal['website']
    mode: Literal['viewport', 'fullPage', 'element', 'clip']
    width: int
    height: int
    selector: str
    clipX: int
    clipY: int
    clipWidth: int
    clipHeight: int
    javascriptEnabled: bool
    blockTrackers: bool
    autoScroll: bool
    freezeAnimations: bool
    omitBackground: bool
    colorScheme: Literal['light', 'dark']
    reducedMotion: bool
    waitUntil: Literal['load', 'domcontentloaded', 'networkidle2']
    waitMs: int


class ConversionCapabilities(TypedDict):
    enabled: bool
    maxUploadBytes: int
    maxPixels: int
    maxOutputBytes: int
    formats: list[Literal['png', 'jpeg', 'webp']]
    maxPage: int
    temporaryMinutes: int
    engines: list[ConversionEngineInfo]


class ConversionEngineInfo(TypedDict):
    id: Literal['docx', 'xlsx', 'pptx', 'website']
    enabled: bool
    label: str
    unit: Literal['page', 'sheet', 'slide', 'website']
    maxUnits: int


class ConversionJob(TypedDict):
    id: str
    projectId: str
    status: Literal['queued', 'running', 'cancelling', 'completed', 'failed', 'cancelled']
    engine: Literal['docx', 'xlsx', 'pptx', 'website']
    options: DocxOptions | XlsxOptions | PptxOptions | WebsiteOptions
    credits: int
    createdAt: str
    expiresAt: str | None
    artifactId: str | None
    errorCode: str | None
    result: ConversionResult | None


class ConversionResult(TypedDict):
    bytes: int
    width: int
    height: int
    pageCount: int
    contentType: str
    warnings: list[str]


class DynamicCapabilities(TypedDict):
    enabled: bool
    canEdit: bool
    analytics: bool
    activeCount: int
    maxActiveCodes: int
    retentionDays: int


class _DynamicCodeRequired(TypedDict):
    analyticsEnabled: bool
    qrOptions: QrGenerateInput | None
    id: str
    projectId: str
    name: str
    slug: str
    redirectUrl: str
    destination: str | None
    status: Literal['active', 'paused', 'deleted']
    suspended: bool
    revision: int
    createdAt: str
    updatedAt: str


class DynamicCode(_DynamicCodeRequired, total=False):
    recordedScans: int | None


class _DynamicCreateInputRequired(TypedDict):
    name: str
    destination: str


class DynamicCreateInput(_DynamicCreateInputRequired, total=False):
    analyticsEnabled: bool


class _DynamicEditInputRequired(TypedDict):
    expectedRevision: int


class DynamicEditInput(_DynamicEditInputRequired, total=False):
    analyticsEnabled: bool
    qrOptions: QrGenerateInput
    name: str
    destination: str
    status: Literal['active', 'paused', 'deleted']


class ScanAnalytics(TypedDict):
    days: int
    total: int
    retentionDays: int
    bestEffort: bool
    series: list[ScanPoint]
    devices: list[ScanBreakdown]
    browsers: list[ScanBreakdown]
    countries: list[ScanBreakdown]
    recent: list[ScanRecent]


class ScanPoint(TypedDict):
    date: str
    count: int


class ScanBreakdown(TypedDict):
    key: str
    count: int


class ScanRecent(TypedDict):
    id: str
    createdAt: str
    device: str
    browser: str
    bot: bool
    country: str
    ip: str | None
    forwardedFor: str | None
    userAgent: str | None
    acceptLanguage: str | None
    language: str | None
    referer: str | None
    platform: str
    clientHints: str | None
    mobileHint: bool | None
    protocol: str
    accept: str | None


class CreditQuote(TypedDict):
    replayEnabled: bool
    id: str
    kind: Literal['code.qr', 'code.barcode', 'pdf.info', 'pdf.render', 'pdf.merge', 'pdf.extract', 'image.transform', 'remote.fetch', 'docx.render', 'xlsx.render', 'pptx.render', 'website.capture']
    units: int
    credits: int
    unitCost: int
    remoteUnitCost: int
    scheduleId: str
    expiresAt: str


class _CreditQuoteInputRequired(TypedDict):
    kind: Literal['code.qr', 'code.barcode', 'pdf.info', 'pdf.render', 'pdf.merge', 'pdf.extract', 'image.transform', 'docx.render', 'xlsx.render', 'pptx.render', 'website.capture']
    units: int


class CreditQuoteInput(_CreditQuoteInputRequired, total=False):
    remote: Literal[True, False]


class ProcessingStatus(TypedDict):
    id: str
    kind: Literal['code.qr', 'code.barcode', 'pdf.info', 'pdf.render', 'pdf.merge', 'pdf.extract', 'image.transform', 'remote.fetch', 'docx.render', 'xlsx.render', 'pptx.render', 'website.capture']
    state: Literal['running', 'completed', 'failed']
    resultExpiresAt: str
    hasResult: bool
    failureCode: str | None


class ProcessingLookupInput(TypedDict):
    kind: Literal['code.qr', 'code.barcode', 'pdf.info', 'pdf.render', 'pdf.merge', 'pdf.extract', 'image.transform', 'remote.fetch', 'docx.render', 'xlsx.render', 'pptx.render', 'website.capture']
    key: str


class ToolArtifact(TypedDict):
    _id: str
    projectId: str
    kind: Literal['qr', 'barcode', 'pdf_render', 'pdf_merge', 'pdf_extract', 'image_transform', 'docx_render', 'xlsx_render', 'pptx_render', 'website_capture']
    displayName: str
    status: Literal['ready', 'deleting']
    bytes: int
    sha256: str
    contentType: str
    outputType: str
    requestSnapshot: dict[str, object]
    sourceImageId: str | None
    createdAt: str
    updatedAt: str


class _OutputsSummaryRequired(TypedDict):
    total: int
    originals: int
    transforms: int
    images: int
    qr: int
    barcode: int
    pdf: int


class OutputsSummary(_OutputsSummaryRequired, total=False):
    docx: int
    xlsx: int
    pptx: int
    website: int


class _OutputRowRequired(TypedDict):
    id: str
    kind: Literal['original', 'transform', 'image_transform', 'qr', 'barcode', 'pdf', 'docx', 'xlsx', 'pptx', 'website']
    name: str
    type: str
    status: str
    createdAt: str
    bytes: int
    thumbAvailable: bool


class OutputRow(_OutputRowRequired, total=False):
    sourceImageId: str | None
    contentType: str | None
    meta: dict[str, object]


class ProcessingOptions(TypedDict, total=False):
    idempotencyKey: str
    quoteId: str

class ArtifactSaveInput(TypedDict):
    kind: Literal['qr', 'barcode', 'pdf_render', 'pdf_merge', 'pdf_extract', 'image_transform']
    displayName: str
    contentType: str

class ScanQuery(TypedDict, total=False):
    days: int
    device: Literal['desktop', 'mobile', 'tablet', 'bot', 'unknown']
    browser: Literal['chrome', 'edge', 'firefox', 'safari', 'other', 'unknown']
    country: str
    bot: bool
