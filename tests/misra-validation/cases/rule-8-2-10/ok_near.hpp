// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_10_OK_NEAR_HPP
#define KV_RULE_8_2_10_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_10::ok_near {

inline std::uint32_t half(std::uint32_t n) { return n / 2U; }

inline std::uint32_t half(std::uint16_t n) { return half(static_cast<std::uint32_t>(n)); }

inline std::uint32_t quarter(std::uint32_t n) { return half(half(n)); }

}  // namespace kv::rule_8_2_10::ok_near

#endif  // KV_RULE_8_2_10_OK_NEAR_HPP
