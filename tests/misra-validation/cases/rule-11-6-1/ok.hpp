// Compliant: every variable is initialised where it is declared.
#ifndef KV_RULE_11_6_1_OK_HPP
#define KV_RULE_11_6_1_OK_HPP

#include <cstdint>

namespace kv::rule_11_6_1::ok {

inline std::uint32_t pick(bool high) {
  const std::uint32_t v = high ? 10U : 1U;
  return v;
}

}  // namespace kv::rule_11_6_1::ok

#endif  // KV_RULE_11_6_1_OK_HPP
