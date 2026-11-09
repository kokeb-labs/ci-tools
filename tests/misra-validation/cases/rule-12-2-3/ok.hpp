// Compliant: the named one-bit field is unsigned.
#ifndef KV_RULE_12_2_3_OK_HPP
#define KV_RULE_12_2_3_OK_HPP

#include <cstdint>

namespace kv::rule_12_2_3::ok {

struct Bits {
  std::uint32_t enabled : 1;
  std::uint32_t level : 3;
};

inline std::uint32_t level_if_enabled(const Bits& b) { return (b.enabled != 0U) ? b.level : 0U; }

}  // namespace kv::rule_12_2_3::ok

#endif  // KV_RULE_12_2_3_OK_HPP
