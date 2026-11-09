// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_10_1_OK_NEAR_HPP
#define KV_RULE_5_10_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_10_1::near {

// Trailing underscores and single inner underscores are not reserved.
struct Reg {
  std::uint32_t field_{0U};
  std::uint32_t low_byte{0U};
};
inline std::uint32_t pick(const Reg& r) { return r.field_ ^ r.low_byte; }

}  // namespace kv::rule_5_10_1::near

#endif  // KV_RULE_5_10_1_OK_NEAR_HPP
