#ifndef KV_RULE_6_0_3_OK_HPP
#define KV_RULE_6_0_3_OK_HPP

// Compliant: our declarations live in a named namespace.
#include <cstdint>

namespace kv::rule_6_0_3::ok {

struct Point {
  std::int32_t x{0};
};

inline std::int32_t origin_x() { return Point{}.x; }

}  // namespace kv::rule_6_0_3::ok

#endif  // KV_RULE_6_0_3_OK_HPP
