// Seeded violation: #pragma and _Pragma.
#pragma GCC diagnostic push
#pragma GCC diagnostic pop
_Pragma("GCC diagnostic push")
_Pragma("GCC diagnostic pop")

namespace kv::rule_19_6_1::bad {
constexpr int kValue = 1;
}  // namespace kv::rule_19_6_1::bad
