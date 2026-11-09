// Compliant: the long long literal carries LL.
#ifndef KV_RULE_5_13_6_OK_HPP
#define KV_RULE_5_13_6_OK_HPP

#include <cstdint>

namespace kv::rule_5_13_6::ok {

inline std::int64_t big() { return 3000000000LL; }

}  // namespace kv::rule_5_13_6::ok

#endif  // KV_RULE_5_13_6_OK_HPP
