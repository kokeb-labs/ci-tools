// Compliant near miss: an array owned by unique_ptr<T[]> from make_unique; nothing is released by hand.
#ifndef KV_RULE_21_6_2_ARRAY_OK_HPP
#define KV_RULE_21_6_2_ARRAY_OK_HPP

#include <cstddef>
#include <cstdint>
#include <memory>

namespace kv::rule_21_6_2_array::ok {

[[nodiscard]] inline std::int32_t first_of(std::size_t n) {
  const std::unique_ptr<std::int32_t[]> values = std::make_unique<std::int32_t[]>(n);
  return values[0];
}

}  // namespace kv::rule_21_6_2_array::ok

#endif  // KV_RULE_21_6_2_ARRAY_OK_HPP
