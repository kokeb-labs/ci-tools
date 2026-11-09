// Compliant near miss: the <algorithm> std::remove on a range; no <cstdio> function is called.
#ifndef KV_RULE_30_0_1_ALGORITHM_REMOVE_OK_HPP
#define KV_RULE_30_0_1_ALGORITHM_REMOVE_OK_HPP

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iterator>

namespace kv::rule_30_0_1_algorithm_remove::ok {

[[nodiscard]] inline std::ptrdiff_t compact(std::array<std::int32_t, 4U>& values) {
  return std::distance(values.begin(), std::remove(values.begin(), values.end(), 0));
}

}  // namespace kv::rule_30_0_1_algorithm_remove::ok

#endif  // KV_RULE_30_0_1_ALGORITHM_REMOVE_OK_HPP
