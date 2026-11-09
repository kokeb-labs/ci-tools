// Compliant: the volatile object is read through a volatile reference.
#ifndef KV_RULE_8_2_3_REFERENCE_OK_HPP
#define KV_RULE_8_2_3_REFERENCE_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_3_reference::ok {

inline std::uint32_t read_once(const volatile std::uint32_t& reg) {
  const std::uint32_t value = reg;
  return value;
}

}  // namespace kv::rule_8_2_3_reference::ok

#endif  // KV_RULE_8_2_3_REFERENCE_OK_HPP
