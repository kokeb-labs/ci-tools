// Compliant: every use of the parameter in an expression is parenthesised.
#ifndef KV_RULE_19_3_4_OK_HPP
#define KV_RULE_19_3_4_OK_HPP

#include <cstdint>

#define KV_RULE_19_3_4_DOUBLE(X) ((X) * 2U)

namespace kv::rule_19_3_4::ok {

inline std::uint32_t twice(std::uint32_t a, std::uint32_t b) { return KV_RULE_19_3_4_DOUBLE(a + b); }

}  // namespace kv::rule_19_3_4::ok

#undef KV_RULE_19_3_4_DOUBLE

#endif  // KV_RULE_19_3_4_OK_HPP
