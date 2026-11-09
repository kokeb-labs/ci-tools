// Compliant: one action per statement.
#ifndef KV_RULE_8_19_1_OK_HPP
#define KV_RULE_8_19_1_OK_HPP

#include <cstdint>

namespace kv::rule_8_19_1::ok {

inline std::uint32_t step(std::uint32_t& a, std::uint32_t& b) {
  ++a;
  ++b;
  return b;
}

}  // namespace kv::rule_8_19_1::ok

#endif  // KV_RULE_8_19_1_OK_HPP
