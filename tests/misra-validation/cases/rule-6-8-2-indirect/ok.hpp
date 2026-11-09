// Compliant: the references returned are to the caller's objects.
#ifndef KV_RULE_6_8_2_INDIRECT_OK_HPP
#define KV_RULE_6_8_2_INDIRECT_OK_HPP

#include <cstdint>

namespace kv::rule_6_8_2_indirect::ok {

inline const std::int32_t& larger(const std::int32_t& a, const std::int32_t& b) { return (a > b) ? a : b; }

}  // namespace kv::rule_6_8_2_indirect::ok

#endif  // KV_RULE_6_8_2_INDIRECT_OK_HPP
