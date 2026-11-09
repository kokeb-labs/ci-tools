// Compliant: the values arrive as a typed span.
#ifndef KV_RULE_21_10_1_OK_HPP
#define KV_RULE_21_10_1_OK_HPP

#include <algorithm>
#include <cstddef>
#include <span>

namespace kv::rule_21_10_1::ok {

[[nodiscard]] inline std::ptrdiff_t count_set(std::span<const bool> flags) {
  return std::count(flags.begin(), flags.end(), true);
}

}  // namespace kv::rule_21_10_1::ok

#endif  // KV_RULE_21_10_1_OK_HPP
