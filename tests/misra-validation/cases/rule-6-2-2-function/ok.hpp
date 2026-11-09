#ifndef KV_RULE_6_2_2_FUNCTION_OK_HPP
#define KV_RULE_6_2_2_FUNCTION_OK_HPP

// Compliant: one declaration in one header, used by every translation unit.
#include <cstdint>

namespace kv::rule_6_2_2_function::ok {

std::int32_t kv_rule_6_2_2_ok_reading(std::int32_t channel);

inline std::int32_t sample() { return kv_rule_6_2_2_ok_reading(1); }

}  // namespace kv::rule_6_2_2_function::ok

#endif  // KV_RULE_6_2_2_FUNCTION_OK_HPP
