// Compliant: the stored value is read on the path that keeps it.
#ifndef KV_RULE_0_1_1_OK_HPP
#define KV_RULE_0_1_1_OK_HPP

#include <cstdint>

namespace kv::rule_0_1_1::ok {

inline std::uint32_t pick(std::uint32_t a, bool big) {
  std::uint32_t r = a;
  if (big) {
    r = 7U;
  }
  return r;
}

}  // namespace kv::rule_0_1_1::ok

#endif  // KV_RULE_0_1_1_OK_HPP
