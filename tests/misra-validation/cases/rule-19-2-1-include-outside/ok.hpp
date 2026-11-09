#ifndef KV_RULE_19_2_1_INCLUDE_OUTSIDE_OK_HPP
#define KV_RULE_19_2_1_INCLUDE_OUTSIDE_OK_HPP

// Compliant: the #include is inside the guard.
#include <cstdint>

namespace kv::rule_19_2_1_include_outside::ok {

inline std::uint8_t one() { return 1U; }

}  // namespace kv::rule_19_2_1_include_outside::ok

#endif  // KV_RULE_19_2_1_INCLUDE_OUTSIDE_OK_HPP
