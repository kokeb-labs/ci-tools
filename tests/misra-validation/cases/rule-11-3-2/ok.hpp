// Compliant: at most one level of indirection, through a reference.
#ifndef KV_RULE_11_3_2_OK_HPP
#define KV_RULE_11_3_2_OK_HPP

#include <cstdint>

namespace kv::rule_11_3_2::ok {

inline std::uint32_t deref(const std::uint32_t& p) { return p; }

}  // namespace kv::rule_11_3_2::ok

#endif  // KV_RULE_11_3_2_OK_HPP
