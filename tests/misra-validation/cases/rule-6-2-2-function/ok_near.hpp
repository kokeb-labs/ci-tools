// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_2_2_FUNCTION_OK_NEAR_HPP
#define KV_RULE_6_2_2_FUNCTION_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_2_2_function::near {

// Overloads with different parameter types are different functions, not incompatible declarations.
std::int32_t reading(std::int32_t channel);
std::int64_t reading(std::int64_t channel);
// A repeated declaration with the identical type.
std::int32_t reading(std::int32_t channel);

}  // namespace kv::rule_6_2_2_function::near

#endif  // KV_RULE_6_2_2_FUNCTION_OK_NEAR_HPP
