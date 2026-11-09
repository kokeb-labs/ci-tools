// Compliant: the predicate is a const call operator without side effects.
#ifndef KV_RULE_28_3_1_OK_HPP
#define KV_RULE_28_3_1_OK_HPP

#include <algorithm>
#include <array>
#include <cstdint>
#include <iterator>

namespace kv::rule_28_3_1::ok {

struct IsPositive {
  bool operator()(std::int32_t value) const { return value > 0; }
};

[[nodiscard]] inline std::ptrdiff_t count_positive(const std::array<std::int32_t, 4U>& values) {
  return std::count_if(values.begin(), values.end(), IsPositive{});
}

}  // namespace kv::rule_28_3_1::ok

#endif  // KV_RULE_28_3_1_OK_HPP
