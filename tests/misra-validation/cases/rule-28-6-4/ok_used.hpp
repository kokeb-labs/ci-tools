// Compliant near misses: fill (no result to use), and the results of remove_if and empty used.
#ifndef KV_RULE_28_6_4_OK_USED_HPP
#define KV_RULE_28_6_4_OK_USED_HPP

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iterator>

namespace kv::rule_28_6_4::ok_used {

inline void zero(std::array<std::int32_t, 4U>& values) { std::fill(values.begin(), values.end(), 0); }

[[nodiscard]] inline std::ptrdiff_t keep_positive(std::array<std::int32_t, 4U>& values) {
  const auto end = std::remove_if(values.begin(), values.end(), [](std::int32_t v) { return v < 0; });
  return std::distance(values.begin(), end);
}

[[nodiscard]] inline bool has_any(const std::array<std::int32_t, 4U>& values) { return !values.empty(); }

}  // namespace kv::rule_28_6_4::ok_used

#endif  // KV_RULE_28_6_4_OK_USED_HPP
