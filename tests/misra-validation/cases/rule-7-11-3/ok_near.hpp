// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_11_3_OK_NEAR_HPP
#define KV_RULE_7_11_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_11_3::ok_near {

inline std::int32_t two() { return 2; }

using Fn = std::int32_t (*)();

inline std::int32_t call(Fn f) { return f(); }

inline std::int32_t by_address() { return call(&two); }

inline std::int32_t local_lambda() {
  auto const f = []() -> std::int32_t { return 3; };
  return f();
}

}  // namespace kv::rule_7_11_3::ok_near

#endif  // KV_RULE_7_11_3_OK_NEAR_HPP
