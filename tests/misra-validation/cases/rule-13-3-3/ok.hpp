// Compliant: every declaration uses the same parameter names.
#ifndef KV_RULE_13_3_3_OK_HPP
#define KV_RULE_13_3_3_OK_HPP

#include <cstdint>

namespace kv::rule_13_3_3::ok {

std::uint32_t clamp_to(std::uint32_t value, std::uint32_t limit);

inline std::uint32_t clamp_to(std::uint32_t value, std::uint32_t limit) {
  return (value > limit) ? limit : value;
}

}  // namespace kv::rule_13_3_3::ok

#endif  // KV_RULE_13_3_3_OK_HPP
