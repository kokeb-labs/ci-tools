// Compliant: a fixed array of bool holds real bool objects.
#ifndef KV_RULE_26_3_1_OK_HPP
#define KV_RULE_26_3_1_OK_HPP

#include <array>
#include <cstddef>

namespace kv::rule_26_3_1::ok {

[[nodiscard]] inline std::size_t count_flags() {
  const std::array<bool, 8U> flags{};
  return flags.size();
}

}  // namespace kv::rule_26_3_1::ok

#endif  // KV_RULE_26_3_1_OK_HPP
