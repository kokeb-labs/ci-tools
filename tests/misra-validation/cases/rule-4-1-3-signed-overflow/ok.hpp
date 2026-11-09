// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_SIGNED_OVERFLOW_OK_HPP
#define KV_RULE_4_1_3_SIGNED_OVERFLOW_OK_HPP

#include <cstdint>
#include <limits>

namespace kv::rule_4_1_3_signed_overflow::ok {

inline std::int32_t add(std::int32_t a, std::int32_t b) {
  // Two 32-bit values cannot overflow a 64-bit sum; the result is clamped before narrowing.
  const std::int64_t wide = static_cast<std::int64_t>(a) + static_cast<std::int64_t>(b);
  std::int64_t clamped = wide;
  if (wide > static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::max())) {
    clamped = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::max());
  }
  if (wide < static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::min())) {
    clamped = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::min());
  }
  return static_cast<std::int32_t>(clamped);
}

}  // namespace kv::rule_4_1_3_signed_overflow::ok

#endif  // KV_RULE_4_1_3_SIGNED_OVERFLOW_OK_HPP
