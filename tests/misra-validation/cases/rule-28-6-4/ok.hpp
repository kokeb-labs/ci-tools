// Compliant: the new logical end returned by std::remove is used.
#ifndef KV_RULE_28_6_4_OK_HPP
#define KV_RULE_28_6_4_OK_HPP

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iterator>

namespace kv::rule_28_6_4::ok {

[[nodiscard]] inline std::ptrdiff_t compact(std::array<std::int32_t, 6U>& values) {
  const auto end = std::remove(values.begin(), values.end(), 0);
  return std::distance(values.begin(), end);
}

[[nodiscard]] inline bool nothing_left(const std::array<std::int32_t, 6U>& values) { return values.empty(); }

}  // namespace kv::rule_28_6_4::ok

#endif  // KV_RULE_28_6_4_OK_HPP
