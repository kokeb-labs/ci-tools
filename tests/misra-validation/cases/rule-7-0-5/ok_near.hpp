// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_0_5_OK_NEAR_HPP
#define KV_RULE_7_0_5_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_0_5::ok_near {

inline std::uint32_t area(std::uint16_t w, std::uint16_t h) {
  return static_cast<std::uint32_t>(w) * static_cast<std::uint32_t>(h);
}

inline std::uint32_t flip(std::uint8_t v) { return ~static_cast<std::uint32_t>(v); }

inline std::uint32_t both(std::uint32_t a, std::uint32_t b) { return a & b; }

}  // namespace kv::rule_7_0_5::ok_near

#endif  // KV_RULE_7_0_5_OK_NEAR_HPP
