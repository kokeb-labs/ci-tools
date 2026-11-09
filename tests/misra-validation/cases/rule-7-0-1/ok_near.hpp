// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_0_1_OK_NEAR_HPP
#define KV_RULE_7_0_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_0_1::ok_near {

inline bool keep(bool v) { return v; }

inline std::int32_t as_number(bool flag) { return flag ? 1 : 0; }

inline bool agree(bool a, bool b) { return (a == b) && !(a && !b); }

inline bool pass(bool flag) { return keep(flag); }

}  // namespace kv::rule_7_0_1::ok_near

#endif  // KV_RULE_7_0_1_OK_NEAR_HPP
