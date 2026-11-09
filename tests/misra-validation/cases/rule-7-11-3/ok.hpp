#ifndef KV_RULE_7_11_3_OK_HPP
#define KV_RULE_7_11_3_OK_HPP

// Compliant: function pointers are formed by assignment to a function pointer object.
#include <cstdint>

namespace kv::rule_7_11_3::ok {

inline std::int32_t one() { return 1; }

using Fn = std::int32_t (*)();

inline std::int32_t use() {
  Fn const f = &one;
  return f();
}

}  // namespace kv::rule_7_11_3::ok

#endif  // KV_RULE_7_11_3_OK_HPP
