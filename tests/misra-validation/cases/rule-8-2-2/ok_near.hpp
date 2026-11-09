// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_2_OK_NEAR_HPP
#define KV_RULE_8_2_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_2::ok_near {

[[nodiscard]] inline std::int32_t value() { return 1; }

inline void discard() { (void)value(); }

inline std::uint16_t low(std::uint32_t v) { return static_cast<std::uint16_t>(v & 0xFFFFU); }

}  // namespace kv::rule_8_2_2::ok_near

#endif  // KV_RULE_8_2_2_OK_NEAR_HPP
