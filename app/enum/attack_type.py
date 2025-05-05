import enum

class AttackType(str, enum.Enum):
    format_string = "format-string"
    off_by_one = "off-by-one"
    heap_overflow = "heap-overflow"
    stack_overflow = "stack-overflow"
