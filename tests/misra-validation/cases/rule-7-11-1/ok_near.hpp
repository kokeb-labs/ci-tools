// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_11_1_OK_NEAR_HPP
#define KV_RULE_7_11_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_11_1::ok_near {

inline std::int32_t const* none() { return nullptr; }

inline std::int32_t read_or_zero(std::int32_t const* p, std::int32_t count) {
  if ((p == nullptr) || (count == 0)) {
    return 0;
  }
  return *p;
}

}  // namespace kv::rule_7_11_1::ok_near

#endif  // KV_RULE_7_11_1_OK_NEAR_HPP
