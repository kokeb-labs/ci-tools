// Compliant: the value is written before every read.
#ifndef KV_RULE_11_6_2_OK_HPP
#define KV_RULE_11_6_2_OK_HPP

#include <cstdint>

namespace kv::rule_11_6_2::ok {

inline std::uint32_t maybe(bool set) {
  std::uint32_t v = 0U;
  if (set) {
    v = 3U;
  }
  return v;
}

}  // namespace kv::rule_11_6_2::ok

#endif  // KV_RULE_11_6_2_OK_HPP
