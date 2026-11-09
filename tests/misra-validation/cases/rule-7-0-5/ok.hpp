#ifndef KV_RULE_7_0_5_OK_HPP
#define KV_RULE_7_0_5_OK_HPP

// Compliant: operands are widened explicitly to one unsigned type before the arithmetic.
#include <cstdint>

namespace kv::rule_7_0_5::ok {

inline std::uint32_t sum(std::uint8_t a, std::uint8_t b) {
  return static_cast<std::uint32_t>(a) + static_cast<std::uint32_t>(b);
}

}  // namespace kv::rule_7_0_5::ok

#endif  // KV_RULE_7_0_5_OK_HPP
