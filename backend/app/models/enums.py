import enum


class ProductType(str, enum.Enum):
    motor = "motor"
    bike = "bike"
    life = "life"
    device = "device"


class ThreadStatus(str, enum.Enum):
    active = "active"
    ended = "ended"
    abandoned = "abandoned"


class CollectionStatus(str, enum.Enum):
    collecting = "collecting"
    confirming = "confirming"
    quoting = "quoting"
    payment_pending = "payment_pending"
    complete = "complete"
    abandoned = "abandoned"


class QuoteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"


class PolicyStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"
    expired = "expired"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"


class SentimentType(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class ResolutionStatus(str, enum.Enum):
    resolved = "resolved"
    unresolved = "unresolved"
    partial = "partial"


class RevenuePotential(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
