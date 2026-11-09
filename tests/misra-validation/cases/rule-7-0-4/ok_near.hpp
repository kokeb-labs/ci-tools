// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_0_4_OK_NEAR_HPP
#define KV_RULE_7_0_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_0_4::ok_near {

inline constexpr std::uint32_t kMask = 0xF0U;

inline std::uint32_t merge(std::uint32_t a, std::uint32_t b) { return ((a | b) ^ kMask) & ~a; }

inline std::uint32_t top_bit(std::uint32_t v) { return v >> 31U; }

}  // namespace kv::rule_7_0_4::ok_near

#endif  // KV_RULE_7_0_4_OK_NEAR_HPP
