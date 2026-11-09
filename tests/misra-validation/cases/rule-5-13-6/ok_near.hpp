// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_13_6_OK_NEAR_HPP
#define KV_RULE_5_13_6_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_13_6::near {

// A small single-L literal is long on every target; a large value written with LL.
inline std::int64_t small_long() { return 5L; }
inline std::int64_t big() { return 4000000000LL; }

}  // namespace kv::rule_5_13_6::near

#endif  // KV_RULE_5_13_6_OK_NEAR_HPP
