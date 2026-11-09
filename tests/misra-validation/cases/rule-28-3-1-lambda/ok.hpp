// Compliant near miss: a lambda predicate that captures a limit by value and does not change it.
#ifndef KV_RULE_28_3_1_LAMBDA_OK_HPP
#define KV_RULE_28_3_1_LAMBDA_OK_HPP

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_28_3_1_lambda::ok {

[[nodiscard]] inline std::ptrdiff_t count_above(const std::array<std::int32_t, 4U>& values, std::int32_t limit) {
  return std::count_if(values.begin(), values.end(), [limit](std::int32_t v) { return v > limit; });
}

}  // namespace kv::rule_28_3_1_lambda::ok

#endif  // KV_RULE_28_3_1_LAMBDA_OK_HPP
