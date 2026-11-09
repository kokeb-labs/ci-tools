#ifndef KV_RULE_6_2_1_OK_HPP
#define KV_RULE_6_2_1_OK_HPP

// Compliant: one definition, in one header, shared by every translation unit that includes it.
#include <cstdint>

namespace kv::rule_6_2_1::ok {

inline std::int32_t limit(std::int32_t v) { return (v > 10) ? 10 : v; }

}  // namespace kv::rule_6_2_1::ok

#endif  // KV_RULE_6_2_1_OK_HPP
